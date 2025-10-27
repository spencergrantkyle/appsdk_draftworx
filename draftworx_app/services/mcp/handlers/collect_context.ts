import { randomUUID } from "node:crypto";

import { sessionStore } from "../db/session_state.js";
import { telemetryBuffer } from "../lib/telemetry.js";
import { contextSchema, type ContextInput } from "../lib/validation.js";

const REQUIRED_FIELDS = ["entityType", "jurisdiction", "yearEnd", "framework"] as const;

type RequiredField = (typeof REQUIRED_FIELDS)[number];

export interface CollectContextResult {
  toolRunId: string;
  summary: string;
  missingFields: RequiredField[];
  context: Record<string, string | undefined>;
}

export function handleCollectContext(sessionId: string, input: Partial<ContextInput>): CollectContextResult {
  const toolRunId = randomUUID();
  const current = sessionStore.get(sessionId);
  const mergedContext = {
    ...current.context,
    ...input
  };

  const missingFields = REQUIRED_FIELDS.filter((field) => {
    const value = mergedContext[field];
    if (!value) return true;
    try {
      contextSchema.pick({ [field]: true as const }).parse({ [field]: value });
      return false;
    } catch (error) {
      return true;
    }
  });

  const completed = missingFields.length === 0;

  sessionStore.update(sessionId, {
    context: {
      ...mergedContext,
      completed
    }
  });
  sessionStore.pushToolRun(sessionId, toolRunId);

  telemetryBuffer.record({
    toolRunId,
    toolName: "draftworx.collect_context",
    status: "succeeded",
    timestamp: new Date().toISOString()
  });

  const collectedCount = REQUIRED_FIELDS.length - missingFields.length;
  const summary = `${collectedCount} of ${REQUIRED_FIELDS.length} context fields captured.`;

  return {
    toolRunId,
    summary,
    missingFields,
    context: mergedContext as Record<string, string | undefined>
  };
}
