# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This is the Apps SDK Examples Gallery - a repository showcasing UI components and MCP (Model Context Protocol) servers for building ChatGPT apps. The project demonstrates how to create widget-backed tools that render rich UI components inline in ChatGPT using the Apps SDK.

## Key Commands

### Development
```bash
# Install dependencies (uses pnpm workspace)
pnpm install

# Build all widget components into standalone assets
pnpm run build

# Run development server for widget preview (port 4444)
pnpm run dev

# Serve static assets for preview (port 4444 with CORS)
pnpm run serve

# Type check
pnpm run tsc
```

### MCP Servers

All MCP servers are organized in the `servers/` directory by language. See `MCP_SERVERS.md` for detailed documentation.

**Node.js Pizzaz Server:**
```bash
cd servers/node/pizzaz
pnpm install
pnpm start
```

**Python Pizzaz Server:**
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r servers/python/pizzaz/requirements.txt
uvicorn servers.python.pizzaz.main:app --port 8000
```

**Python Solar System Server:**
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r servers/python/solar-system/requirements.txt
uvicorn servers.python.solar-system.main:app --port 8000
```

**Python Draftworx Server:**
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r servers/python/draftworx/requirements.txt
uvicorn servers.python.draftworx.main:app --port 8000
```

**Creating New MCP Servers:**
- Python: Copy `servers/python/_template/` to `servers/python/your-server/`
- Node.js: Copy `servers/node/_template/` to `servers/node/your-server/`

## Architecture

### Build System

The project uses a custom Vite-based build orchestrator (`build-all.mts`) that:

1. **Auto-discovers widget entrypoints**: Scans `src/**/index.{tsx,jsx}` for widget entries
2. **Bundles each widget separately**: Creates isolated `.html`, `.js`, and `.css` files for each widget
3. **Version hashing**: Generates SHA-256 hash from `package.json` version and appends to filenames (e.g., `pizzaz-0038.js`)
4. **Self-contained HTML**: Produces standalone HTML files that inline both CSS and JS for easy distribution
5. **CSS handling**: Automatically includes global CSS (`src/index.css`) and per-widget CSS using glob patterns

Output is written to `assets/` directory with versioned filenames.

### Widget Development

**Widget Structure:**
- Each widget lives in `src/<widget-name>/`
- Must have an `index.jsx` or `index.tsx` entrypoint
- Can include component-specific CSS files (auto-bundled)
- Uses React 19 with TypeScript/JSX

**Widget Runtime:**
- Widgets receive data via `window.openai` global object
- Use `useWidgetProps<T>()` hook to access tool output data
- Use `useOpenAiGlobal()` hook to access ChatGPT environment (theme, displayMode, locale, etc.)
- Support for state persistence via `widgetState` and `setWidgetState`

**Key Hooks:**
- `useWidgetProps<T>()` - Access tool output data passed from MCP server
- `useOpenAiGlobal()` - Access ChatGPT environment (theme, maxHeight, displayMode, safeArea, userAgent)
- `useDisplayMode()` - Current display mode (pip/inline/fullscreen)
- `useWidgetState<T>()` - Persistent widget state

### MCP Server Architecture

**Server Types:**
- Node.js server uses `@modelcontextprotocol/sdk` with SSE transport
- Python servers use `FastMCP` helper with HTTP/SSE

**Tool Response Structure:**
Each MCP tool must return:
1. **Plain text content** - Human-readable response
2. **Structured JSON** - Data payload (accessed as `toolOutput` in widgets)
3. **Metadata** - `_meta.openai/outputTemplate` pointing to widget HTML

**Metadata Keys:**
- `openai/outputTemplate` - URI to widget HTML (e.g., `ui://widget/pizza-map.html`)
- `openai/toolInvocation/invoking` - Message shown while tool executes
- `openai/toolInvocation/invoked` - Message shown when complete
- `openai/widgetAccessible` - Boolean indicating widget is accessible
- `openai/resultCanProduceWidget` - Boolean indicating result can render widget

### Project Structure

- `src/` - Widget source code (React components)
- `assets/` - Built widget bundles (generated, versioned)
- `servers/` - MCP server implementations organized by language
  - `python/` - Python MCP servers
    - `_template/` - Template for creating new Python MCP servers
    - `pizzaz/` - Python Pizzaz demo server
    - `solar-system/` - Python 3D solar system server
    - `draftworx/` - Python Draftworx server
  - `node/` - Node.js MCP servers
    - `_template/` - Template for creating new Node.js MCP servers
    - `pizzaz/` - Node.js Pizzaz demo server
- `build-all.mts` - Build orchestrator for widget bundling
- `vite.config.mts` - Dev server config with multi-entry support
- `vite.host.config.mts` - Alternative Vite config for host development
- `MCP_SERVERS.md` - Comprehensive MCP server documentation

### Widget to MCP Integration Flow

1. MCP server tool is called with arguments
2. Server executes logic and returns response with:
   - Text content for ChatGPT to read
   - JSON data payload for widget
   - `_meta.openai/outputTemplate` URI pointing to widget HTML
3. ChatGPT fetches widget HTML from specified URI
4. Widget HTML is loaded with data injected into `window.openai.toolOutput`
5. Widget renders using React and accesses data via `useWidgetProps()`

### Development Workflow

1. Create new widget in `src/<name>/index.jsx`
2. Run `pnpm run build` to generate bundled assets
3. Update MCP server to reference new widget HTML and pass appropriate data
4. Test locally using `pnpm run serve` and ngrok tunnel
5. Add to ChatGPT via Settings > Connectors (developer mode required)

### TypeScript Configuration

Project uses TypeScript with multiple configs:
- `tsconfig.json` - References app and node configs
- `tsconfig.app.json` - Application/widget code config
- `tsconfig.node.json` - Build scripts and Node.js code config
