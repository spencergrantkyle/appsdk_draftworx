"""
Draftworx MCP server implemented using FastMCP.

This server exposes Draftworx tools for ChatGPT Apps SDK integration.
It handles context collection, trial balance upload, account mapping,
template recommendation, and draft creation. Each tool returns structured
content and metadata that allows ChatGPT to render the correct component.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, List

import mcp.types as types
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field, ConfigDict, ValidationError

# ----------------------------------------------------------------------
# Tool Schemas
# ----------------------------------------------------------------------


class CollectContextInput(BaseModel):
    entityType: str = Field(..., description="Entity type such as company, partnership, sole_prop, ngo, or trust.")
    jurisdiction: str = Field(..., description="Jurisdiction code such as ZA, UK, US, AU, CA, EU, or other.")
    yearEnd: str = Field(..., description="Year end in format YYYY MM DD.")
    framework: str = Field(..., description="Reporting framework such as IFRS, IFRS_SMEs, US_GAAP, UK_GAAP, or other.")

    model_config = ConfigDict(extra="forbid")


class UploadTrialBalanceInput(BaseModel):
    clientId: str = Field(..., description="Unique identifier of the Draftworx client.")
    fileId: str = Field(..., description="Identifier of the uploaded trial balance file.")
    fileType: str = Field(..., description="File type of the uploaded trial balance (xlsx, csv, or zip).")

    model_config = ConfigDict(extra="forbid")


class MapAccountsInput(BaseModel):
    tbId: str = Field(..., description="Identifier of the imported trial balance to be mapped.")
    confidenceThreshold: float = Field(..., description="Confidence threshold between 0 and 1 for auto-mapping suggestions.")

    model_config = ConfigDict(extra="forbid")


class RecommendTemplateInput(BaseModel):
    jurisdiction: str = Field(..., description="Jurisdiction code for the entity (ZA, UK, US, etc.).")
    entityType: str = Field(..., description="Entity type such as company, partnership, ngo, trust.")
    framework: str = Field(..., description="Reporting framework such as IFRS, IFRS_SMEs, US_GAAP, UK_GAAP, or other.")

    model_config = ConfigDict(extra="forbid")


class CreateDraftInput(BaseModel):
    clientId: str = Field(..., description="Unique identifier for the Draftworx client.")
    tbId: str = Field(..., description="Trial balance identifier used for the draft.")
    templateId: str = Field(..., description="Identifier for the chosen template to apply.")

    model_config = ConfigDict(extra="forbid")


# ----------------------------------------------------------------------
# MCP Server setup
# ----------------------------------------------------------------------

mcp = FastMCP(
    name="draftworx-mcp",
    sse_path="/mcp",
    message_path="/mcp/messages",
    stateless_http=True,
)

# ----------------------------------------------------------------------
# Tool Metadata Helpers
# ----------------------------------------------------------------------


def _tool_meta(description: str, read_only: bool = False) -> Dict[str, Any]:
    return {
        "annotations": {
            "readOnlyHint": read_only,
            "destructiveHint": False,
            "openWorldHint": False,
        },
        "openai/toolInvocation/invoking": "Processing Draftworx task...",
        "openai/toolInvocation/invoked": "Draftworx task completed",
        "openai/resultCanProduceWidget": False,
    }


def _make_tool(name: str, title: str, description: str, schema: Dict[str, Any], read_only=False) -> types.Tool:
    return types.Tool(
        name=name,
        title=title,
        description=description,
        inputSchema=deepcopy(schema),
        _meta=_tool_meta(description, read_only=read_only),
    )


# ----------------------------------------------------------------------
# Input Schemas
# ----------------------------------------------------------------------

TOOL_SCHEMAS: Dict[str, Dict[str, Any]] = {
    "collect_context": {
        "type": "object",
        "properties": {
            "entityType": {"type": "string", "enum": ["company", "partnership", "sole_prop", "ngo", "trust"]},
            "jurisdiction": {"type": "string", "enum": ["ZA", "UK", "US", "AU", "CA", "EU", "other"]},
            "yearEnd": {"type": "string", "description": "YYYY MM DD"},
            "framework": {"type": "string", "enum": ["IFRS", "IFRS_SMEs", "US_GAAP", "UK_GAAP", "other"]},
        },
        "required": ["entityType", "jurisdiction", "yearEnd", "framework"],
        "additionalProperties": False,
    },
    "upload_trial_balance": {
        "type": "object",
        "properties": {
            "clientId": {"type": "string"},
            "fileId": {"type": "string"},
            "fileType": {"type": "string", "enum": ["xlsx", "csv", "zip"]},
        },
        "required": ["clientId", "fileId", "fileType"],
        "additionalProperties": False,
    },
    "map_accounts": {
        "type": "object",
        "properties": {
            "tbId": {"type": "string"},
            "confidenceThreshold": {"type": "number", "minimum": 0, "maximum": 1},
        },
        "required": ["tbId", "confidenceThreshold"],
        "additionalProperties": False,
    },
    "recommend_template": {
        "type": "object",
        "properties": {
            "jurisdiction": {"type": "string", "enum": ["ZA", "UK", "US", "AU", "CA", "EU", "other"]},
            "entityType": {"type": "string", "enum": ["company", "partnership", "sole_prop", "ngo", "trust"]},
            "framework": {"type": "string", "enum": ["IFRS", "IFRS_SMEs", "US_GAAP", "UK_GAAP", "other"]},
        },
        "required": ["jurisdiction", "entityType", "framework"],
        "additionalProperties": False,
    },
    "create_draft": {
        "type": "object",
        "properties": {
            "clientId": {"type": "string"},
            "tbId": {"type": "string"},
            "templateId": {"type": "string"},
        },
        "required": ["clientId", "tbId", "templateId"],
        "additionalProperties": False,
    },
}

# ----------------------------------------------------------------------
# Tool Registry
# ----------------------------------------------------------------------

TOOLS: List[types.Tool] = [
    _make_tool(
        "draftworx.collect_context",
        "Collect Entity Context",
        "Use this when the user needs to specify or confirm entity details like jurisdiction, entity type, year end, and framework before client creation or upload.",
        TOOL_SCHEMAS["collect_context"],
        read_only=True,
    ),
    _make_tool(
        "draftworx.upload_trial_balance",
        "Upload Trial Balance",
        "Use this when the user wants to upload a trial balance file and begin mapping. Do not use for invoice or bank export files.",
        TOOL_SCHEMAS["upload_trial_balance"],
    ),
    _make_tool(
        "draftworx.map_accounts",
        "Map Accounts",
        "Use this when a trial balance has been imported and mappings must be reviewed. Presents low confidence accounts for confirmation or correction.",
        TOOL_SCHEMAS["map_accounts"],
    ),
    _make_tool(
        "draftworx.recommend_template",
        "Recommend Template",
        "Use this when the user needs the correct template based on entity and jurisdiction. Do not use after a template has already been confirmed.",
        TOOL_SCHEMAS["recommend_template"],
        read_only=True,
    ),
    _make_tool(
        "draftworx.create_draft",
        "Create Draft",
        "Use this when context, mapping, and template are set and a Draftworx file should be created.",
        TOOL_SCHEMAS["create_draft"],
    ),
]

# ----------------------------------------------------------------------
# Tool Handlers
# ----------------------------------------------------------------------


@mcp._mcp_server.list_tools()
async def _list_tools() -> List[types.Tool]:
    return TOOLS


async def _call_tool_request(req: types.CallToolRequest) -> types.ServerResult:
    name = req.params.name
    args = req.params.arguments or {}

    try:
        if name == "draftworx.collect_context":
            payload = CollectContextInput(**args)
            summary = f"Collected context for {payload.entityType} in {payload.jurisdiction} ({payload.framework})."
            structured = payload.model_dump()
        elif name == "draftworx.upload_trial_balance":
            payload = UploadTrialBalanceInput(**args)
            summary = f"Uploaded {payload.fileType} file for client {payload.clientId}."
            structured = payload.model_dump()
        elif name == "draftworx.map_accounts":
            payload = MapAccountsInput(**args)
            summary = f"Mapping accounts for {payload.tbId} with threshold {payload.confidenceThreshold}."
            structured = payload.model_dump()
        elif name == "draftworx.recommend_template":
            payload = RecommendTemplateInput(**args)
            summary = f"Recommended template for {payload.entityType} in {payload.jurisdiction} ({payload.framework})."
            structured = payload.model_dump()
        elif name == "draftworx.create_draft":
            payload = CreateDraftInput(**args)
            summary = f"Created draft for client {payload.clientId} using template {payload.templateId}."
            structured = payload.model_dump()
        else:
            return types.ServerResult(
                types.CallToolResult(
                    content=[types.TextContent(type="text", text=f"Unknown tool: {name}")],
                    isError=True,
                )
            )

        return types.ServerResult(
            types.CallToolResult(
                content=[types.TextContent(type="text", text=summary)],
                structuredContent=structured,
                _meta=_tool_meta(summary),
            )
        )

    except ValidationError as exc:
        return types.ServerResult(
            types.CallToolResult(
                content=[types.TextContent(type="text", text=f"Validation error: {exc.errors()}")],
                isError=True,
            )
        )


mcp._mcp_server.request_handlers[types.CallToolRequest] = _call_tool_request

# ----------------------------------------------------------------------
# HTTP App
# ----------------------------------------------------------------------

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

    uvicorn.run("draftworx_server.main:app", host="0.0.0.0", port=8000)