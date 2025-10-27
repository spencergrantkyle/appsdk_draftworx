export type ToolRunStatus = "pending" | "succeeded" | "failed";

export interface ContextField {
  key: "entityType" | "jurisdiction" | "yearEnd" | "framework";
  label: string;
  value?: string;
  required?: boolean;
  helperText?: string;
}

export interface ContextCollectorProps {
  toolRunId: string;
  summary: string;
  fields: ContextField[];
  missingFields: string[];
}

export interface ClientConfirmationProps {
  toolRunId: string;
  status: ToolRunStatus;
  clientId?: string;
  summary: string;
  context: Record<string, string>;
}

export interface TrialBalanceUploadProps {
  toolRunId: string;
  status: ToolRunStatus;
  uploadSummary: string;
  detectedAccounts: Array<{ account: string; balance: number }>;
  versionTag: string;
  allowedTypes: string[];
  fileName?: string;
}

export interface MappingReviewProps {
  toolRunId: string;
  status: ToolRunStatus;
  confirmedMappings: Array<{ source: string; target: string; confidence: number }>;
  unresolvedAccounts: Array<{ account: string; suggestedTarget?: string; confidence: number }>;
  confidenceThreshold: number;
}

export interface TemplateRecommendationProps {
  toolRunId: string;
  status: ToolRunStatus;
  templateId: string;
  confidence: number;
  rationale: string;
  options: Array<{ id: string; name: string; description: string }>;
}

export interface DraftSummaryProps {
  toolRunId: string;
  status: ToolRunStatus;
  draftUrl: string;
  summary: string;
  clientId: string;
  tbId: string;
  templateId: string;
  keyHighlights: Array<{ label: string; value: string }>;
}

export type TelemetryRecord = {
  toolRunId: string;
  toolName: string;
  status: ToolRunStatus;
  startedAt: string;
  completedAt?: string;
  error?: string;
};
