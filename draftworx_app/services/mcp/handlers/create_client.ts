import { randomUUID } from "node:crypto";

import { sessionStore } from "../db/session_state.js";
import { DraftworxClient } from "../lib/draftworx_client.js";
import { telemetryBuffer } from "../lib/telemetry.js";
import type { ToolRunStatus } from "../lib/types.js";
import { contextSchema, type ContextInput } from "../lib/validation.js";

export interface CreateClientResult {
  toolRunId: string;
  status: ToolRunStatus;
  clientId?: string;
  summary: string;
  context: Record<string, string>;
}

export async function handleCreateClient(
  sessionId: string,
  input: Partial<ContextInput>,
  draftworxClient: DraftworxClient
): Promise<CreateClientResult> {
  const state = sessionStore.get(sessionId);
  const mergedContext = {
    ...state.context,
    ...input
  };

  const parsed = contextSchema.parse(mergedContext);

  try {
    const response = await draftworxClient.createClient(parsed);

    telemetryBuffer.record({
      toolRunId: response.toolRunId,
      toolName: "draftworx.create_client",
      status: response.status,
      timestamp: new Date().toISOString()
    });

    sessionStore.update(sessionId, {
      context: {
        ...parsed,
        completed: true
      },
      clientId: response.data.clientId
    });
    sessionStore.pushToolRun(sessionId, response.toolRunId);

    return {
      toolRunId: response.toolRunId,
      status: response.status,
      clientId: response.data.clientId,
      summary: response.summary ?? "Client created in Draftworx.",
      context: parsed
    };
  } catch (error) {
    const failureId = randomUUID();
    telemetryBuffer.record({
      toolRunId: failureId,
      toolName: "draftworx.create_client",
      status: "failed",
      timestamp: new Date().toISOString(),
      error: error instanceof Error ? error.message : String(error)
    });
    throw error;
  }
}
