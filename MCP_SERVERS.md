# MCP Servers Documentation

This document provides comprehensive documentation for all MCP (Model Context Protocol) servers in this repository, including how to create new servers following the established patterns.

## Table of Contents

- [Directory Structure](#directory-structure)
- [Available Servers](#available-servers)
- [Creating New MCP Servers](#creating-new-mcp-servers)
  - [Python MCP Servers](#python-mcp-servers)
  - [Node.js MCP Servers](#nodejs-mcp-servers)
- [Server Architecture](#server-architecture)
- [Development Workflow](#development-workflow)
- [Testing](#testing)
- [Deployment](#deployment)

## Directory Structure

All MCP servers are organized in the `servers/` directory by implementation language:

```
servers/
├── python/                    # Python MCP servers
│   ├── _template/            # Template for new Python servers
│   │   ├── main.py
│   │   ├── requirements.txt
│   │   └── README.md
│   ├── pizzaz/               # Pizzaz demo server
│   ├── solar-system/         # 3D solar system server
│   └── draftworx/            # Draftworx server
└── node/                     # Node.js MCP servers
    ├── _template/            # Template for new Node.js servers
    │   ├── src/server.ts
    │   ├── package.json
    │   ├── tsconfig.json
    │   └── README.md
    └── pizzaz/               # Pizzaz demo server
```

**Benefits of this structure:**
- Clear separation by language
- Easy to discover and navigate servers
- Consistent patterns across implementations
- Templates ready for rapid development
- Scales well as new servers are added

## Available Servers

### Python Servers

#### 1. Pizzaz (`servers/python/pizzaz/`)
Demo server showcasing multiple widget-backed tools for pizza-related UI components.

**Features:**
- Pizza map widget
- Pizza carousel widget
- Pizza albums widget
- Pizza list widget
- Pizza video widget

**Run:**
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r servers/python/pizzaz/requirements.txt
uvicorn servers.python.pizzaz.main:app --port 8000
```

#### 2. Solar System (`servers/python/solar-system/`)
3D solar system visualization server demonstrating planetary data and interactive widgets.

**Run:**
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r servers/python/solar-system/requirements.txt
uvicorn servers.python.solar-system.main:app --port 8000
```

#### 3. Draftworx (`servers/python/draftworx/`)
Custom Draftworx server implementation.

**Run:**
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r servers/python/draftworx/requirements.txt
uvicorn servers.python.draftworx.main:app --port 8000
```

### Node.js Servers

#### 1. Pizzaz (`servers/node/pizzaz/`)
Node.js implementation of the Pizzaz demo server using the official TypeScript SDK.

**Run:**
```bash
cd servers/node/pizzaz
pnpm install
pnpm start
```

## Creating New MCP Servers

### Python MCP Servers

#### Quick Start

1. **Copy the template:**
   ```bash
   cp -r servers/python/_template servers/python/your-server-name
   cd servers/python/your-server-name
   ```

2. **Set up virtual environment:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Customize the server:**
   Edit `main.py` to configure your widgets and tools:

   ```python
   # Update the server name
   mcp = FastMCP(
       name="your-server-name",
       sse_path="/mcp",
       message_path="/mcp/messages",
       stateless_http=True,
   )

   # Define your widgets
   def create_widgets() -> List[Widget]:
       static_url = get_static_url()
       asset_hash = "-0038"  # Match your build output

       return [
           Widget(
               identifier="your-widget-id",
               title="Your Widget Title",
               template_uri="ui://widget/your-widget.html",
               invoking="Loading your widget",
               invoked="Your widget ready",
               html=(
                   "<div id=\"your-root\"></div>\n"
                   f"<link rel=\"stylesheet\" href=\"{static_url}/assets/your-widget{asset_hash}.css\">\n"
                   f"<script type=\"module\" src=\"{static_url}/assets/your-widget{asset_hash}.js\"></script>"
               ),
               response_text="Your widget rendered!",
           ),
       ]

   # Define your input schema
   class ToolInput(BaseModel):
       your_param: str = Field(
           ...,
           alias="yourParam",
           description="Description of your parameter.",
       )

   # Implement tool logic in _call_tool_request()
   ```

4. **Run your server:**
   ```bash
   python main.py
   # or
   uvicorn servers.python.your_server_name.main:app --port 8000
   ```

#### Python Template Structure

- **`main.py`** - Main server implementation
  - Widget definitions
  - Tool handlers
  - Resource handlers
  - FastMCP app configuration

- **`requirements.txt`** - Python dependencies
  - `mcp[fastapi]` - Official MCP SDK with FastAPI support
  - `fastapi` - Web framework
  - `uvicorn` - ASGI server

- **`README.md`** - Documentation template

### Node.js MCP Servers

#### Quick Start

1. **Copy the template:**
   ```bash
   cp -r servers/node/_template servers/node/your-server-name
   cd servers/node/your-server-name
   ```

2. **Install dependencies:**
   ```bash
   pnpm install  # or npm install / yarn install
   ```

3. **Customize the server:**
   Edit `src/server.ts` to configure your widgets and tools:

   ```typescript
   // Update the server name
   const server = new Server(
     {
       name: "your-server-name",
       version: "0.1.0"
     },
     {
       capabilities: {
         resources: {},
         tools: {}
       }
     }
   );

   // Define your widgets
   const widgets: Widget[] = [
     {
       id: "your-widget-id",
       title: "Your Widget Title",
       templateUri: "ui://widget/your-widget.html",
       invoking: "Loading your widget",
       invoked: "Your widget ready",
       html: `
   <div id="your-root"></div>
   <link rel="stylesheet" href="https://your-cdn.com/assets/your-widget-0038.css">
   <script type="module" src="https://your-cdn.com/assets/your-widget-0038.js"></script>
       `.trim(),
       responseText: "Your widget rendered!"
     }
   ];

   // Define your input schema
   const toolInputSchema = {
     type: "object",
     properties: {
       yourParam: {
         type: "string",
         description: "Description of your parameter."
       }
     },
     required: ["yourParam"],
     additionalProperties: false
   } as const;

   const toolInputParser = z.object({
     yourParam: z.string()
   });
   ```

4. **Run your server:**
   ```bash
   pnpm start        # Production mode
   pnpm run dev      # Development mode with auto-reload
   ```

#### Node.js Template Structure

- **`src/server.ts`** - Main server implementation
  - Widget definitions
  - Tool handlers
  - Resource handlers
  - HTTP/SSE server setup

- **`package.json`** - Dependencies and scripts
  - `@modelcontextprotocol/sdk` - Official MCP SDK
  - `zod` - Runtime validation
  - `tsx` - TypeScript execution

- **`tsconfig.json`** - TypeScript configuration

- **`README.md`** - Documentation template

## Server Architecture

### Core Concepts

#### 1. Widgets
A widget is a UI component that renders in ChatGPT. Each widget is defined by:
- **identifier/id** - Unique identifier for the widget
- **title** - Display name
- **templateUri** - URI for widget HTML (e.g., `ui://widget/example.html`)
- **html** - HTML markup with CSS and JS references
- **invoking/invoked** - Status messages during execution

#### 2. Tools
MCP tools are functions exposed to ChatGPT. Each tool:
- Takes structured input (validated via JSON schema)
- Executes business logic
- Returns text content, structured data, and metadata
- Can optionally render a widget via `_meta.openai/outputTemplate`

#### 3. Resources
Resources provide the widget HTML templates. Each resource:
- Has a unique URI matching the widget's `templateUri`
- Returns HTML markup with inline CSS and JS references
- Includes metadata for ChatGPT integration

### Request Flow

1. **ChatGPT calls tool** → MCP server receives `CallToolRequest`
2. **Server validates input** → Pydantic (Python) or Zod (Node.js)
3. **Server executes logic** → Your custom business logic
4. **Server returns response** →
   - Plain text (human-readable)
   - Structured JSON (for widget)
   - Metadata (widget URI, invocation messages)
5. **ChatGPT fetches widget** → Requests resource via `templateUri`
6. **Server returns HTML** → Widget markup with CSS/JS
7. **Widget renders** → React app hydrates with data from `window.openai.toolOutput`

### MCP Endpoints

Both Python and Node.js servers expose:

- **`GET /mcp`** - SSE (Server-Sent Events) stream for establishing connections
- **`POST /mcp/messages?sessionId=...`** - Message endpoint for active sessions

CORS is enabled for local development and MCP Inspector compatibility.

## Development Workflow

### 1. Widget Development First

Before creating an MCP server, develop your widget:

```bash
# Create widget in src/your-widget/
mkdir src/your-widget
touch src/your-widget/index.tsx

# Build widgets
pnpm run build

# Widgets are output to assets/ with versioned filenames
# e.g., assets/your-widget-0038.js, assets/your-widget-0038.css
```

### 2. Create MCP Server

Follow the [Creating New MCP Servers](#creating-new-mcp-servers) guide above.

### 3. Connect Widget to Server

In your server code, reference the built widget assets:

**Python:**
```python
html=(
    "<div id=\"your-widget-root\"></div>\n"
    f"<link rel=\"stylesheet\" href=\"{static_url}/assets/your-widget{asset_hash}.css\">\n"
    f"<script type=\"module\" src=\"{static_url}/assets/your-widget{asset_hash}.js\"></script>"
)
```

**Node.js:**
```typescript
html: `
<div id="your-widget-root"></div>
<link rel="stylesheet" href="https://your-cdn.com/assets/your-widget-0038.css">
<script type="module" src="https://your-cdn.com/assets/your-widget-0038.js"></script>
`.trim()
```

### 4. Test Locally

1. **Start your MCP server** (see [Available Servers](#available-servers))
2. **Use MCP Inspector** for testing:
   ```bash
   npx @modelcontextprotocol/inspector
   ```
3. **Connect ChatGPT** (developer mode required)

## Testing

### Manual Testing with MCP Inspector

The MCP Inspector provides a UI for testing your server:

```bash
npx @modelcontextprotocol/inspector
```

Connect to your server endpoint (e.g., `http://localhost:8000/mcp`) and:
- List available tools
- Call tools with test data
- Inspect responses and metadata
- View widget rendering

### Automated Testing

#### Python
```bash
# Install dev dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest tests/
```

#### Node.js
```bash
# Install dev dependencies
pnpm add -D vitest @types/node

# Run tests
pnpm test
```

### Testing Checklist

- [ ] Server starts without errors
- [ ] Tools are listed correctly
- [ ] Resources are listed correctly
- [ ] Tool input validation works
- [ ] Tool execution returns expected response
- [ ] Widget HTML is served correctly
- [ ] Metadata includes all required fields
- [ ] Widget renders in MCP Inspector
- [ ] Widget receives correct data via `toolOutput`

## Deployment

### Environment Variables

**Python:**
- `STATIC_URL` - Base URL for widget assets (default: OpenAI CDN)
- `PORT` - Server port (default: 8000)

**Node.js:**
- `PORT` - Server port (default: 8000)

### Production Considerations

1. **Asset Hosting**
   - Deploy built widgets to a CDN
   - Update `STATIC_URL` to point to your CDN
   - Ensure CORS is configured on your CDN

2. **Security**
   - Implement authentication/authorization
   - Configure CORS appropriately (don't use `*` in production)
   - Add rate limiting
   - Validate all inputs
   - Sanitize outputs

3. **Monitoring**
   - Add logging (structured logs recommended)
   - Set up error tracking (e.g., Sentry)
   - Monitor server health and performance
   - Track tool usage metrics

4. **Scaling**
   - Use process managers (e.g., systemd, PM2, supervisord)
   - Consider containerization (Docker)
   - Load balance multiple instances
   - Cache static resources

### Railway Deployment

This repository is configured for Railway deployment. See `railway.json` and `nixpacks.toml` for configuration.

```bash
# Deploy to Railway
railway up
```

## Common Patterns

### Environment-Aware Asset URLs

**Python:**
```python
def get_static_url() -> str:
    """Get the static asset base URL from environment or use default."""
    return os.getenv("STATIC_URL", "https://persistent.oaistatic.com/ecosystem-built-assets")
```

**Node.js:**
```typescript
const staticUrl = process.env.STATIC_URL || "https://persistent.oaistatic.com/ecosystem-built-assets";
```

### Structured Content

Return data that your widget can access:

**Python:**
```python
structuredContent={"param": value}
```

**Node.js:**
```typescript
structuredContent: { param: value }
```

Widget access via:
```typescript
const { param } = useWidgetProps<{ param: string }>();
```

### Error Handling

**Python:**
```python
try:
    payload = ToolInput.model_validate(arguments)
except ValidationError as exc:
    return types.ServerResult(
        types.CallToolResult(
            content=[types.TextContent(type="text", text=f"Error: {exc.errors()}")],
            isError=True,
        )
    )
```

**Node.js:**
```typescript
try {
  const args = toolInputParser.parse(request.params.arguments ?? {});
} catch (error) {
  throw new Error(`Invalid input: ${error.message}`);
}
```

## Additional Resources

- [MCP Official Documentation](https://modelcontextprotocol.io/)
- [Apps SDK Documentation](https://platform.openai.com/docs/apps)
- [FastMCP Python Helper](https://github.com/modelcontextprotocol/python-sdk)
- [MCP TypeScript SDK](https://github.com/modelcontextprotocol/typescript-sdk)

## Support

For issues or questions:
1. Check existing server implementations in `servers/`
2. Review template READMEs
3. Consult `CLAUDE.md` for repository-specific guidance
4. Open an issue in the repository
