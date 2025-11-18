"""[Server Name] MCP server implemented with the Python FastMCP helper.

This server exposes widget-backed tools that render UI bundles. Each handler returns
the HTML shell via an MCP resource and echoes structured data so the ChatGPT client
can hydrate the widget. The module also wires the handlers into an HTTP/SSE stack
so you can run the server with uvicorn on port 8000.
"""

from __future__ import annotations

import os
from copy import deepcopy
from dataclasses import dataclass
from typing import Any, Dict, List

import mcp.types as types
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, ConfigDict, Field, ValidationError


def get_static_url() -> str:
    """Get the static asset base URL from environment or use default."""
    return os.getenv("STATIC_URL", "https://persistent.oaistatic.com/ecosystem-built-assets")


@dataclass(frozen=True)
class Widget:
    """Widget configuration for MCP tools."""
    identifier: str
    title: str
    template_uri: str
    invoking: str
    invoked: str
    html: str
    response_text: str


def create_widgets() -> List[Widget]:
    """Create widgets with environment-aware asset URLs."""
    static_url = get_static_url()

    # Asset hash for versioned widget bundles
    # Update this to match your build output (e.g., -0038)
    asset_hash = "-0038"

    return [
        Widget(
            identifier="example-widget",
            title="Show Example Widget",
            template_uri="ui://widget/example.html",
            invoking="Loading example widget",
            invoked="Example widget ready",
            html=(
                "<div id=\"example-root\"></div>\n"
                f"<link rel=\"stylesheet\" href=\"{static_url}/assets/example{asset_hash}.css\">\n"
                f"<script type=\"module\" src=\"{static_url}/assets/example{asset_hash}.js\"></script>"
            ),
            response_text="Rendered example widget!",
        ),
        # Add more widgets here
    ]


widgets = create_widgets()


MIME_TYPE = "text/html+skybridge"


WIDGETS_BY_ID: Dict[str, Widget] = {widget.identifier: widget for widget in widgets}
WIDGETS_BY_URI: Dict[str, Widget] = {widget.template_uri: widget for widget in widgets}


class ToolInput(BaseModel):
    """Schema for tool input parameters."""

    example_param: str = Field(
        ...,
        alias="exampleParam",
        description="Example parameter for the tool.",
    )

    model_config = ConfigDict(populate_by_name=True, extra="forbid")


mcp = FastMCP(
    name="my-mcp-server",  # Change this to your server name
    sse_path="/mcp",
    message_path="/mcp/messages",
    stateless_http=True,
)


TOOL_INPUT_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "exampleParam": {
            "type": "string",
            "description": "Example parameter for the tool.",
        }
    },
    "required": ["exampleParam"],
    "additionalProperties": False,
}


def _resource_description(widget: Widget) -> str:
    return f"{widget.title} widget markup"


def _tool_meta(widget: Widget) -> Dict[str, Any]:
    return {
        "openai/outputTemplate": widget.template_uri,
        "openai/toolInvocation/invoking": widget.invoking,
        "openai/toolInvocation/invoked": widget.invoked,
        "openai/widgetAccessible": True,
        "openai/resultCanProduceWidget": True,
        "annotations": {
          "destructiveHint": False,
          "openWorldHint": False,
          "readOnlyHint": True,
        }
    }


def _embedded_widget_resource(widget: Widget) -> types.EmbeddedResource:
    return types.EmbeddedResource(
        type="resource",
        resource=types.TextResourceContents(
            uri=widget.template_uri,
            mimeType=MIME_TYPE,
            text=widget.html,
            title=widget.title,
        ),
    )


@mcp._mcp_server.list_tools()
async def _list_tools() -> List[types.Tool]:
    return [
        types.Tool(
            name=widget.identifier,
            title=widget.title,
            description=widget.title,
            inputSchema=deepcopy(TOOL_INPUT_SCHEMA),
            _meta=_tool_meta(widget),
        )
        for widget in widgets
    ]


@mcp._mcp_server.list_resources()
async def _list_resources() -> List[types.Resource]:
    return [
        types.Resource(
            name=widget.title,
            title=widget.title,
            uri=widget.template_uri,
            description=_resource_description(widget),
            mimeType=MIME_TYPE,
            _meta=_tool_meta(widget),
        )
        for widget in widgets
    ]


@mcp._mcp_server.list_resource_templates()
async def _list_resource_templates() -> List[types.ResourceTemplate]:
    return [
        types.ResourceTemplate(
            name=widget.title,
            title=widget.title,
            uriTemplate=widget.template_uri,
            description=_resource_description(widget),
            mimeType=MIME_TYPE,
            _meta=_tool_meta(widget),
        )
        for widget in widgets
    ]


async def _handle_read_resource(req: types.ReadResourceRequest) -> types.ServerResult:
    widget = WIDGETS_BY_URI.get(str(req.params.uri))
    if widget is None:
        return types.ServerResult(
            types.ReadResourceResult(
                contents=[],
                _meta={"error": f"Unknown resource: {req.params.uri}"},
            )
        )

    contents = [
        types.TextResourceContents(
            uri=widget.template_uri,
            mimeType=MIME_TYPE,
            text=widget.html,
            _meta=_tool_meta(widget),
        )
    ]

    return types.ServerResult(types.ReadResourceResult(contents=contents))


async def _call_tool_request(req: types.CallToolRequest) -> types.ServerResult:
    widget = WIDGETS_BY_ID.get(req.params.name)
    if widget is None:
        return types.ServerResult(
            types.CallToolResult(
                content=[
                    types.TextContent(
                        type="text",
                        text=f"Unknown tool: {req.params.name}",
                    )
                ],
                isError=True,
            )
        )

    arguments = req.params.arguments or {}
    try:
        payload = ToolInput.model_validate(arguments)
    except ValidationError as exc:
        return types.ServerResult(
            types.CallToolResult(
                content=[
                    types.TextContent(
                        type="text",
                        text=f"Input validation error: {exc.errors()}",
                    )
                ],
                isError=True,
            )
        )

    # Process your tool logic here
    example_value = payload.example_param

    widget_resource = _embedded_widget_resource(widget)
    meta: Dict[str, Any] = {
        "openai.com/widget": widget_resource.model_dump(mode="json"),
        "openai/outputTemplate": widget.template_uri,
        "openai/toolInvocation/invoking": widget.invoking,
        "openai/toolInvocation/invoked": widget.invoked,
        "openai/widgetAccessible": True,
        "openai/resultCanProduceWidget": True,
    }

    return types.ServerResult(
        types.CallToolResult(
            content=[
                types.TextContent(
                    type="text",
                    text=widget.response_text,
                )
            ],
            structuredContent={"exampleParam": example_value},
            _meta=meta,
        )
    )


mcp._mcp_server.request_handlers[types.CallToolRequest] = _call_tool_request
mcp._mcp_server.request_handlers[types.ReadResourceRequest] = _handle_read_resource


app = mcp.streamable_http_app()

try:
    from starlette.middleware.cors import CORSMiddleware

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
        allow_credentials=False,
    )
except Exception:
    pass


if __name__ == "__main__":
    import uvicorn

    # Update the module path to match your server directory name
    uvicorn.run("servers.python.your_server_name.main:app", host="0.0.0.0", port=8000)
