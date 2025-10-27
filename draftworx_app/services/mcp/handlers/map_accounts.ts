import { randomUUID } from "node:crypto";

import { sessionStore } from "../db/session_state.js";
import { DraftworxClient } from "../lib/draftworx_client.js";
import { telemetryBuffer } from "../lib/telemetry.js";
import type { ToolRunStatus } from "../lib/types.js";
import { mappingSchema, type MappingInput } from "../lib/validation.js";

export interface MapAccountsResult {
  toolRunId: string;
  status: ToolRunStatus;
  confirmedMappings: Array<{ source: string; target: string; confidence: number }>;
  unresolvedAccounts: Array<{ account: string; suggestedTarget?: string; confidence: number }>;
}

export async function handleMapAccounts(
  sessionId: string,
  input: MappingInput,
  draftworxClient: DraftworxClient
): Promise<MapAccountsResult> {
  const parsed = mappingSchema.parse(input);

  try {
    const response = await draftworxClient.mapAccounts(parsed);

    telemetryBuffer.record({
      toolRunId: response.toolRunId,
      toolName: "draftworx.map_accounts",
      status: response.status,
      timestamp: new Date().toISOString()
    });

    sessionStore.pushToolRun(sessionId, response.toolRunId);

    return {
      toolRunId: response.toolRunId,
      status: response.status,
      confirmedMappings: response.data.confirmedMappings,
      unresolvedAccounts: response.data.unresolvedAccounts
    };
  } catch (error) {
    const failureId = randomUUID();
    telemetryBuffer.record({
      toolRunId: failureId,
      toolName: "draftworx.map_accounts",
      status: "failed",
      timestamp: new Date().toISOString(),
      error: error instanceof Error ? error.message : String(error)
    });
    throw error;
  }
}
