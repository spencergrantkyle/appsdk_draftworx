# [Server Name] MCP Server (Python)

This directory contains a Python implementation of an MCP server using the `FastMCP` helper from the official Model Context Protocol SDK. It exposes widget-backed tools that render UI components inline in ChatGPT.

## Prerequisites

- Python 3.10+
- A virtual environment (recommended)

## Installation

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

> **Note:** There is a similarly named package `modelcontextprotocol` on PyPI that is unrelated to the official MCP SDK. This template uses the official `mcp` distribution with its FastAPI extra. If you previously installed the other project, run `pip uninstall modelcontextprotocol` before installing requirements.

## Development

### 1. Configure Your Widget

Edit `main.py` and update:
- `create_widgets()` - Define your widget configurations
- `ToolInput` - Define your tool's input schema
- `TOOL_INPUT_SCHEMA` - JSON schema for tool inputs
- `_call_tool_request()` - Implement your tool logic

### 2. Update Asset References

Make sure your widget HTML references match your built assets:
- Update `asset_hash` to match your build output (e.g., `-0038`)
- Update widget identifiers to match your React component names
- Ensure `template_uri` matches your widget routing

### 3. Run the Server

```bash
python main.py
```

Or with uvicorn directly:

```bash
uvicorn servers.python.your_server_name.main:app --port 8000
```

This boots a FastAPI app on `http://127.0.0.1:8000`. The server exposes:

- `GET /mcp` - SSE stream endpoint
- `POST /mcp/messages?sessionId=...` - Follow-up messages for active sessions

Cross-origin requests are enabled for local development and MCP Inspector compatibility.

## Testing

Test your server with:
- MCP Inspector (local testing)
- ChatGPT connectors (developer mode required)
- curl/httpie for endpoint validation

## Production Deployment

Before deploying to production:

1. Set `STATIC_URL` environment variable to your CDN/asset server
2. Implement authentication/authorization as needed
3. Configure CORS appropriately for your use case
4. Add error handling and logging
5. Set up monitoring and health checks

## Widget Integration

Each tool returns:
1. **Plain text content** - Human-readable response for ChatGPT
2. **Structured JSON** - Data payload (accessed as `toolOutput` in widgets)
3. **Metadata** - `_meta.openai/outputTemplate` pointing to widget HTML

The widget receives data via `window.openai.toolOutput` and can use:
- `useWidgetProps<T>()` - Access tool output data
- `useOpenAiGlobal()` - Access ChatGPT environment
- `useDisplayMode()` - Current display mode

## Next Steps

Use this template as a starting point for:
- Adding real data sources and APIs
- Implementing authentication
- Adding localization support
- Creating custom business logic
- Integrating with external services
