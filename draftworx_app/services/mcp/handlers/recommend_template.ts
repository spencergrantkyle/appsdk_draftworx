import { randomUUID } from "node:crypto";

import { sessionStore } from "../db/session_state.js";
import { DraftworxClient } from "../lib/draftworx_client.js";
import { telemetryBuffer } from "../lib/telemetry.js";
import type { ToolRunStatus } from "../lib/types.js";
import { templateSchema, type TemplateInput } from "../lib/validation.js";

export interface RecommendTemplateResult {
  toolRunId: string;
  status: ToolRunStatus;
  templateId: string;
  confidence: number;
  rationale: string;
  options: Array<{ id: string; name: string; description: string; confidence: number }>;
}

export async function handleRecommendTemplate(
  sessionId: string,
  input: TemplateInput,
  draftworxClient: DraftworxClient
): Promise<RecommendTemplateResult> {
  const parsed = templateSchema.parse(input);

  try {
    const response = await draftworxClient.recommendTemplate(parsed);

    telemetryBuffer.record({
      toolRunId: response.toolRunId,
      toolName: "draftworx.recommend_template",
      status: response.status,
      timestamp: new Date().toISOString()
    });

    sessionStore.update(sessionId, {
      templateId: response.data.templateId
    });
    sessionStore.pushToolRun(sessionId, response.toolRunId);

    return {
      toolRunId: response.toolRunId,
      status: response.status,
      templateId: response.data.templateId,
      confidence: response.data.confidence,
      rationale: response.data.rationale,
      options: response.data.options
    };
  } catch (error) {
    const failureId = randomUUID();
    telemetryBuffer.record({
      toolRunId: failureId,
      toolName: "draftworx.recommend_template",
      status: "failed",
      timestamp: new Date().toISOString(),
      error: error instanceof Error ? error.message : String(error)
    });
    throw error;
  }
}
