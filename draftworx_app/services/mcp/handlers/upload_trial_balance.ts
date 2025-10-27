import { randomUUID } from "node:crypto";

import { sessionStore } from "../db/session_state.js";
import { DraftworxClient } from "../lib/draftworx_client.js";
import { telemetryBuffer } from "../lib/telemetry.js";
import type { ToolRunStatus } from "../lib/types.js";
import { uploadSchema, type UploadInput } from "../lib/validation.js";

export interface UploadTrialBalanceResult {
  toolRunId: string;
  status: ToolRunStatus;
  summary: string;
  detectedAccounts: Array<{ account: string; balance: number }>;
  versionTag: string;
  tbId?: string;
}

export async function handleUploadTrialBalance(
  sessionId: string,
  input: UploadInput,
  draftworxClient: DraftworxClient
): Promise<UploadTrialBalanceResult> {
  const parsed = uploadSchema.parse(input);

  try {
    const response = await draftworxClient.uploadTrialBalance(parsed);

    telemetryBuffer.record({
      toolRunId: response.toolRunId,
      toolName: "draftworx.upload_trial_balance",
      status: response.status,
      timestamp: new Date().toISOString()
    });

    sessionStore.update(sessionId, {
      tbId: response.data.tbId,
      versionTag: response.data.versionTag
    });
    sessionStore.pushToolRun(sessionId, response.toolRunId);

    return {
      toolRunId: response.toolRunId,
      status: response.status,
      summary: response.data.uploadSummary,
      detectedAccounts: response.data.detectedAccounts,
      versionTag: response.data.versionTag,
      tbId: response.data.tbId
    };
  } catch (error) {
    const failureId = randomUUID();
    telemetryBuffer.record({
      toolRunId: failureId,
      toolName: "draftworx.upload_trial_balance",
      status: "failed",
      timestamp: new Date().toISOString(),
      error: error instanceof Error ? error.message : String(error)
    });
    throw error;
  }
}
