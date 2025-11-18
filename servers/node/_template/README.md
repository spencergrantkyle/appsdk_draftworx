# [Server Name] MCP Server (Node.js)

This directory contains a Model Context Protocol (MCP) server implemented with the official TypeScript SDK. The server exposes widget-backed tools that render UI components inline in ChatGPT.

## Prerequisites

- Node.js 18+
- pnpm, npm, or yarn for dependency management

## Installation

```bash
pnpm install
```

If you prefer npm or yarn:
```bash
npm install
# or
yarn install
```

## Development

### 1. Configure Your Widget

Edit `src/server.ts` and update:
- `widgets` array - Define your widget configurations
- `toolInputSchema` - Define your tool's JSON schema
- `toolInputParser` - Define Zod validation schema
- `CallToolRequestSchema` handler - Implement your tool logic

### 2. Update Asset References

Make sure your widget HTML references match your built assets:
- Update asset URLs to match your CDN/build output
- Update widget identifiers to match your React component names
- Ensure `templateUri` matches your widget routing

### 3. Run the Server

Development mode (with auto-reload):
```bash
pnpm run dev
```

Production mode:
```bash
pnpm start
```

The server will start on `http://localhost:8000` (configurable via `PORT` environment variable).

## Server Endpoints

- `GET /mcp` - SSE stream endpoint for establishing connections
- `POST /mcp/messages?sessionId=...` - Message endpoint for active sessions

CORS is enabled for all origins to support local development and MCP Inspector.

## Testing

Test your server with:
- **MCP Inspector** - Local testing and debugging
- **ChatGPT connectors** - Requires developer mode
- **curl/httpie** - Manual endpoint validation

Example curl test:
```bash
# Establish SSE connection
curl http://localhost:8000/mcp
```

## Widget Integration

Each tool returns:
1. **content** - Human-readable text response for ChatGPT
2. **structuredContent** - JSON payload (accessed as `toolOutput` in widgets)
3. **_meta** - Metadata including `openai/outputTemplate` pointing to widget HTML

The widget receives data via `window.openai.toolOutput` and can use:
- `useWidgetProps<T>()` - Access tool output data
- `useOpenAiGlobal()` - Access ChatGPT environment (theme, displayMode, locale)
- `useDisplayMode()` - Current display mode (pip/inline/fullscreen)

## Production Deployment

Before deploying to production:

1. Configure environment variables:
   - `PORT` - Server port (default: 8000)
   - Update static asset URLs to point to your CDN

2. Add security measures:
   - Implement authentication/authorization
   - Configure CORS appropriately
   - Add rate limiting
   - Implement request validation

3. Build for production:
   ```bash
   pnpm run build
   node dist/server.js
   ```

4. Set up monitoring:
   - Error logging
   - Health checks
   - Performance metrics

## Project Structure

```
.
├── src/
│   └── server.ts       # Main server implementation
├── package.json        # Dependencies and scripts
├── tsconfig.json       # TypeScript configuration
└── README.md          # This file
```

## Next Steps

Use this template as a starting point for:
- Adding real data sources and APIs
- Implementing authentication
- Adding localization support
- Creating custom business logic
- Integrating with external services
- Building multi-widget experiences
