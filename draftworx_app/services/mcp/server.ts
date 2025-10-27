import { createServer, type IncomingMessage, type ServerResponse } from "node:http";
import { randomUUID } from "node:crypto";
import { URL } from "node:url";

import { Server } from "@modelcontextprotocol/sdk/dist/server/index.js";
import { SSEServerTransport } from "@modelcontextprotocol/sdk/dist/server/sse.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
  type CallToolRequest,
  type ListToolsRequest,
  type Tool
} from "@modelcontextprotocol/sdk/dist/types.js";

import { sessionStore } from "./db/session_state.js";
import { handleCollectContext } from "./handlers/collect_context.js";
import { handleCreateClient } from "./handlers/create_client.js";
import { handleCreateDraft } from "./handlers/create_draft.js";
import { handleMapAccounts } from "./handlers/map_accounts.js";
import { handleRecommendTemplate } from "./handlers/recommend_template.js";
import { handleUploadTrialBalance } from "./handlers/upload_trial_balance.js";
import { DraftworxClient } from "./lib/draftworx_client.js";
import type { ContextInput, DraftInput, MappingInput, TemplateInput, UploadInput } from "./lib/validation.js";

const baseUrl = process.env.DRAFTWORX_API_BASE_URL ?? "https://api.draftworx.test";
const apiKey = process.env.DRAFTWORX_API_KEY;
const draftworxClient = new DraftworxClient({ baseUrl, apiKey });

const toolMeta = {
  "draftworx.collect_context": {
    template: "ui://draftworx/context-collector.html",
    invoking: "Gathering client context",
    invoked: "Context updated"
  },
  "draftworx.create_client": {
    template: "ui://draftworx/client-confirmation.html",
    invoking: "Registering client",
    invoked: "Client created"
  },
  "draftworx.upload_trial_balance": {
    template: "ui://draftworx/tb-uploader.html",
    invoking: "Uploading trial balance",
    invoked: "Trial balance uploaded"
  },
  "draftworx.map_accounts": {
    template: "ui://draftworx/mapping-review.html",
    invoking: "Mapping accounts",
    invoked: "Mappings prepared"
  },
  "draftworx.recommend_template": {
    template: "ui://draftworx/template-selector.html",
    invoking: "Evaluating templates",
    invoked: "Template recommended"
  },
  "draftworx.create_draft": {
    template: "ui://draftworx/draft-summary.html",
    invoking: "Generating draft",
    invoked: "Draft ready"
  }
} as const;

type ToolName = keyof typeof toolMeta;

function widgetMeta(name: ToolName) {
  const meta = toolMeta[name];
  return {
    "openai/outputTemplate": meta.template,
    "openai/toolInvocation/invoking": meta.invoking,
    "openai/toolInvocation/invoked": meta.invoked,
    "openai/widgetAccessible": true,
    "openai/resultCanProduceWidget": true
  } as const;
}

const contextFieldConfig = [
  {
    key: "jurisdiction",
    label: "Jurisdiction",
    helperText: "Where the entity is registered"
  },
  {
    key: "entityType",
    label: "Entity type",
    helperText: "Company, trust, partnership, etc."
  },
  {
    key: "yearEnd",
    label: "Year-end date",
    helperText: "Use ISO format YYYY-MM-DD"
  },
  {
    key: "framework",
    label: "Reporting framework",
    helperText: "e.g. IFRS for SMEs, IFRS, GAAP"
  }
] as const;

const tools: Tool[] = [
  {
    name: "draftworx.collect_context",
    description: "Collect jurisdiction, entity type, year-end, and reporting framework.",
    inputSchema: {
      type: "object",
      properties: {
        entityType: { type: "string" },
        jurisdiction: { type: "string" },
        yearEnd: { type: "string", format: "date" },
        framework: { type: "string" }
      },
      required: [],
      additionalProperties: false
    },
    outputSchema: {
      type: "object",
      properties: {
        summary: { type: "string" }
      }
    },
    title: "Collect reporting context",
    _meta: widgetMeta("draftworx.collect_context")
  },
  {
    name: "draftworx.create_client",
    description: "Confirm and register a Draftworx client.",
    inputSchema: {
      type: "object",
      properties: {
        entityType: { type: "string" },
        jurisdiction: { type: "string" },
        yearEnd: { type: "string", format: "date" },
        framework: { type: "string" }
      },
      required: ["entityType", "jurisdiction", "yearEnd", "framework"],
      additionalProperties: false
    },
    title: "Create Draftworx client",
    _meta: widgetMeta("draftworx.create_client")
  },
  {
    name: "draftworx.upload_trial_balance",
    description: "Upload a trial balance file (CSV/XLSX/ZIP).",
    inputSchema: {
      type: "object",
      properties: {
        clientId: { type: "string" },
        fileId: { type: "string" },
        fileType: { type: "string", enum: ["csv", "xlsx", "zip"] }
      },
      required: ["clientId", "fileId", "fileType"],
      additionalProperties: false
    },
    title: "Upload trial balance",
    _meta: widgetMeta("draftworx.upload_trial_balance")
  },
  {
    name: "draftworx.map_accounts",
    description: "Map trial balance accounts and flag low-confidence matches.",
    inputSchema: {
      type: "object",
      properties: {
        tbId: { type: "string" },
        confidenceThreshold: { type: "number", minimum: 0, maximum: 1 }
      },
      required: ["tbId", "confidenceThreshold"],
      additionalProperties: false
    },
    title: "Map accounts",
    _meta: widgetMeta("draftworx.map_accounts")
  },
  {
    name: "draftworx.recommend_template",
    description: "Recommend the best reporting template.",
    inputSchema: {
      type: "object",
      properties: {
        jurisdiction: { type: "string" },
        entityType: { type: "string" },
        framework: { type: "string" }
      },
      required: ["jurisdiction", "entityType", "framework"],
      additionalProperties: false
    },
    title: "Recommend template",
    _meta: widgetMeta("draftworx.recommend_template")
  },
  {
    name: "draftworx.create_draft",
    description: "Generate the Draftworx Cloud draft.",
    inputSchema: {
      type: "object",
      properties: {
        clientId: { type: "string" },
        tbId: { type: "string" },
        templateId: { type: "string" }
      },
      required: ["clientId", "tbId", "templateId"],
      additionalProperties: false
    },
    title: "Create draft",
    _meta: widgetMeta("draftworx.create_draft")
  }
];

function extractSessionId(request: CallToolRequest): string {
  return request.params.sessionId ?? request.params.metadata?.sessionId ?? "default";
}

function formatContextFields(context: Record<string, string | undefined>) {
  return contextFieldConfig.map((field) => ({
    key: field.key,
    label: field.label,
    value: context[field.key],
    required: true,
    helperText: field.helperText
  }));
}

function ensureState(sessionId: string, requirement: "context" | "client" | "trialBalance" | "template") {
  const state = sessionStore.get(sessionId);
  switch (requirement) {
    case "context":
      if (!state.context?.completed) {
        throw new Error("Context is incomplete. Run draftworx.collect_context first.");
      }
      break;
    case "client":
      if (!state.clientId) {
        throw new Error("No Draftworx client registered yet.");
      }
      break;
    case "trialBalance":
      if (!state.tbId) {
        throw new Error("No trial balance uploaded yet.");
      }
      break;
    case "template":
      if (!state.templateId) {
        throw new Error("No reporting template selected yet.");
      }
      break;
  }
}

function createDraftworxServer(): Server {
  const server = new Server(
    {
      name: "draftworx-node",
      version: "0.1.0"
    },
    {
      capabilities: {
        tools: {}
      }
    }
  );

  server.setRequestHandler(ListToolsRequestSchema, async (_request: ListToolsRequest) => ({
    tools
  }));

  server.setRequestHandler(CallToolRequestSchema, async (request: CallToolRequest) => {
    const sessionId = extractSessionId(request);
    const args = (request.params.arguments ?? {}) as Record<string, unknown>;
    const name = request.params.name as ToolName;

    switch (name) {
      case "draftworx.collect_context": {
        const result = handleCollectContext(sessionId, args as Partial<ContextInput>);
        const fields = formatContextFields(result.context);
        return {
          content: [
            { type: "text", text: result.summary }
          ],
          structuredContent: {
            component: "ContextCollector",
            props: {
              toolRunId: result.toolRunId,
              summary: result.summary,
              fields,
              missingFields: result.missingFields
            }
          },
          _meta: widgetMeta(name)
        };
      }
      case "draftworx.create_client": {
        ensureState(sessionId, "context");
        const result = await handleCreateClient(sessionId, args as Partial<ContextInput>, draftworxClient);
        return {
          content: [
            { type: "text", text: result.summary }
          ],
          structuredContent: {
            component: "ClientConfirmation",
            props: {
              toolRunId: result.toolRunId,
              status: result.status,
              clientId: result.clientId,
              summary: result.summary,
              context: result.context
            }
          },
          _meta: widgetMeta(name)
        };
      }
      case "draftworx.upload_trial_balance": {
        ensureState(sessionId, "client");
        const result = await handleUploadTrialBalance(sessionId, args as UploadInput, draftworxClient);
        return {
          content: [
            { type: "text", text: result.summary }
          ],
          structuredContent: {
            component: "TrialBalanceUploader",
            props: {
              toolRunId: result.toolRunId,
              status: result.status,
              uploadSummary: result.summary,
              detectedAccounts: result.detectedAccounts,
              versionTag: result.versionTag,
              allowedTypes: ["csv", "xlsx", "zip"],
              fileName: (args as { fileName?: string }).fileName
            }
          },
          _meta: widgetMeta(name)
        };
      }
      case "draftworx.map_accounts": {
        ensureState(sessionId, "trialBalance");
        const mappingArgs = args as MappingInput;
        const result = await handleMapAccounts(sessionId, mappingArgs, draftworxClient);
        return {
          content: [
            { type: "text", text: `Confirmed ${result.confirmedMappings.length} mappings.` }
          ],
          structuredContent: {
            component: "MappingReview",
            props: {
              toolRunId: result.toolRunId,
              status: result.status,
              confirmedMappings: result.confirmedMappings,
              unresolvedAccounts: result.unresolvedAccounts,
              confidenceThreshold: Number(mappingArgs.confidenceThreshold ?? 0.85)
            }
          },
          _meta: widgetMeta(name)
        };
      }
      case "draftworx.recommend_template": {
        ensureState(sessionId, "context");
        const result = await handleRecommendTemplate(sessionId, args as TemplateInput, draftworxClient);
        return {
          content: [
            { type: "text", text: result.rationale }
          ],
          structuredContent: {
            component: "TemplateSelector",
            props: {
              toolRunId: result.toolRunId,
              status: result.status,
              templateId: result.templateId,
              confidence: result.confidence,
              rationale: result.rationale,
              options: result.options
            }
          },
          _meta: widgetMeta(name)
        };
      }
      case "draftworx.create_draft": {
        ensureState(sessionId, "client");
        ensureState(sessionId, "trialBalance");
        ensureState(sessionId, "template");
        const result = await handleCreateDraft(sessionId, args as DraftInput, draftworxClient);
        const state = sessionStore.get(sessionId);
        return {
          content: [
            { type: "text", text: result.summary }
          ],
          structuredContent: {
            component: "DraftSummaryCard",
            props: {
              toolRunId: result.toolRunId,
              status: result.status,
              draftUrl: result.draftUrl,
              summary: result.summary,
              clientId: state.clientId,
              tbId: state.tbId,
              templateId: state.templateId,
              keyHighlights: [
                { label: "Reporting framework", value: state.context?.framework ?? "" },
                { label: "Trial balance version", value: state.versionTag ?? "v1" }
              ]
            }
          },
          _meta: widgetMeta(name)
        };
      }
      default:
        throw new Error(`Unknown tool: ${name}`);
    }
  });

  return server;
}

type SessionRecord = {
  server: Server;
  transport: SSEServerTransport;
};

const sessions = new Map<string, SessionRecord>();

const ssePath = "/mcp";
const postPath = "/mcp/messages";

async function handleSseRequest(res: ServerResponse) {
  res.setHeader("Access-Control-Allow-Origin", "*");
  const server = createDraftworxServer();
  const transport = new SSEServerTransport(postPath, res);
  const sessionId = transport.sessionId ?? randomUUID();

  sessions.set(sessionId, { server, transport });

  transport.onclose = async () => {
    sessions.delete(sessionId);
    await server.close();
  };

  transport.onerror = (error) => {
    console.error("SSE transport error", error);
  };

  try {
    await server.connect(transport);
  } catch (error) {
    sessions.delete(sessionId);
    console.error("Failed to start SSE connection", error);
    if (!res.headersSent) {
      res.writeHead(500).end("Failed to establish SSE connection");
    }
  }
}

async function handlePostMessage(req: IncomingMessage, res: ServerResponse, url: URL) {
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Headers", "content-type");
  const sessionId = url.searchParams.get("sessionId");

  if (!sessionId) {
    res.writeHead(400).end("Missing sessionId query parameter");
    return;
  }

  const session = sessions.get(sessionId);

  if (!session) {
    res.writeHead(404).end("Unknown session");
    return;
  }

  try {
    await session.transport.handlePostMessage(req, res);
  } catch (error) {
    console.error("Failed to process message", error);
    if (!res.headersSent) {
      res.writeHead(500).end("Failed to process message");
    }
  }
}

const portEnv = Number(process.env.PORT ?? 8010);
const port = Number.isFinite(portEnv) ? portEnv : 8010;

const httpServer = createServer(async (req: IncomingMessage, res: ServerResponse) => {
  if (!req.url) {
    res.writeHead(400).end("Missing URL");
    return;
  }

  const url = new URL(req.url, `http://${req.headers.host ?? "localhost"}`);

  if (req.method === "OPTIONS" && (url.pathname === ssePath || url.pathname === postPath)) {
    res.writeHead(204, {
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
      "Access-Control-Allow-Headers": "content-type"
    });
    res.end();
    return;
  }

  if (req.method === "GET" && url.pathname === ssePath) {
    await handleSseRequest(res);
    return;
  }

  if (req.method === "POST" && url.pathname === postPath) {
    await handlePostMessage(req, res, url);
    return;
  }

  res.writeHead(404).end("Not Found");
});

httpServer.on("clientError", (err: Error, socket) => {
  console.error("HTTP client error", err);
  socket.end("HTTP/1.1 400 Bad Request\r\n\r\n");
});

httpServer.listen(port, () => {
  console.log(`Draftworx MCP server listening on http://localhost:${port}`);
  console.log(`  SSE stream: GET http://localhost:${port}${ssePath}`);
  console.log(`  Message endpoint: POST http://localhost:${port}${postPath}?sessionId=...`);
});
