import { randomUUID } from "node:crypto";

import { sessionStore } from "../db/session_state.js";
import { DraftworxClient } from "../lib/draftworx_client.js";
import { telemetryBuffer } from "../lib/telemetry.js";
import type { ToolRunStatus } from "../lib/types.js";
import { draftSchema, type DraftInput } from "../lib/validation.js";

export interface CreateDraftResult {
  toolRunId: string;
  status: ToolRunStatus;
  draftUrl?: string;
  summary: string;
}

export async function handleCreateDraft(
  sessionId: string,
  input: DraftInput,
  draftworxClient: DraftworxClient
): Promise<CreateDraftResult> {
  const state = sessionStore.get(sessionId);
  const merged = {
    clientId: state.clientId,
    tbId: state.tbId,
    templateId: state.templateId,
    ...input
  };

  const parsed = draftSchema.parse(merged);

  try {
    const response = await draftworxClient.createDraft(parsed);

    telemetryBuffer.record({
      toolRunId: response.toolRunId,
      toolName: "draftworx.create_draft",
      status: response.status,
      timestamp: new Date().toISOString()
    });

    sessionStore.pushToolRun(sessionId, response.toolRunId);

    return {
      toolRunId: response.toolRunId,
      status: response.status,
      draftUrl: response.data.draftUrl,
      summary: response.data.summary
    };
  } catch (error) {
    const failureId = randomUUID();
    telemetryBuffer.record({
      toolRunId: failureId,
      toolName: "draftworx.create_draft",
      status: "failed",
      timestamp: new Date().toISOString(),
      error: error instanceof Error ? error.message : String(error)
    });
    throw error;
  }
}
