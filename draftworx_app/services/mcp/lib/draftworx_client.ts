import { randomUUID } from "node:crypto";

export interface DraftworxClientOptions {
  baseUrl: string;
  apiKey?: string;
  fetchImpl?: typeof fetch;
}

export interface DraftworxResponse<T> {
  toolRunId: string;
  status: "pending" | "succeeded" | "failed";
  summary?: string;
  data: T;
}

export class DraftworxClient {
  private readonly baseUrl: string;
  private readonly apiKey?: string;
  private readonly fetchImpl: typeof fetch;

  constructor(options: DraftworxClientOptions) {
    this.baseUrl = options.baseUrl.replace(/\/$/, "");
    this.apiKey = options.apiKey;
    this.fetchImpl = options.fetchImpl ?? fetch;
  }

  private headers(): Record<string, string> {
    const headers: Record<string, string> = {
      "Content-Type": "application/json"
    };

    if (this.apiKey) {
      headers.Authorization = `Bearer ${this.apiKey}`;
    }

    return headers;
  }

  private async request<T>(path: string, init: RequestInit): Promise<T> {
    const response = await this.fetchImpl(`${this.baseUrl}${path}`, {
      ...init,
      headers: {
        ...this.headers(),
        ...init.headers
      }
    });

    if (!response.ok) {
      const text = await response.text();
      throw new Error(`Draftworx API request failed: ${response.status} ${text}`);
    }

    return (await response.json()) as T;
  }

  async createClient(input: {
    entityType: string;
    jurisdiction: string;
    yearEnd: string;
    framework: string;
  }): Promise<DraftworxResponse<{ clientId: string }>> {
    const toolRunId = randomUUID();
    const body = await this.request<{ id: string; summary: string }>(`/clients`, {
      method: "POST",
      body: JSON.stringify(input)
    });

    return {
      toolRunId,
      status: "succeeded",
      summary: body.summary,
      data: { clientId: body.id }
    };
  }

  async uploadTrialBalance(input: {
    clientId: string;
    fileId: string;
    fileType: "csv" | "xlsx" | "zip";
  }): Promise<
    DraftworxResponse<{
      tbId: string;
      uploadSummary: string;
      detectedAccounts: Array<{ account: string; balance: number }>;
      versionTag: string;
    }>
  > {
    const toolRunId = randomUUID();
    const body = await this.request<{
      tbId: string;
      summary: string;
      detectedAccounts: Array<{ account: string; balance: number }>;
      versionTag: string;
    }>(`/trial-balances`, {
      method: "POST",
      body: JSON.stringify(input)
    });

    return {
      toolRunId,
      status: "succeeded",
      summary: body.summary,
      data: {
        tbId: body.tbId,
        uploadSummary: body.summary,
        detectedAccounts: body.detectedAccounts,
        versionTag: body.versionTag
      }
    };
  }

  async mapAccounts(input: {
    tbId: string;
    confidenceThreshold: number;
  }): Promise<
    DraftworxResponse<{
      confirmedMappings: Array<{ source: string; target: string; confidence: number }>;
      unresolvedAccounts: Array<{ account: string; suggestedTarget?: string; confidence: number }>;
    }>
  > {
    const toolRunId = randomUUID();
    const body = await this.request<{
      confirmedMappings: Array<{ source: string; target: string; confidence: number }>;
      unresolvedAccounts: Array<{ account: string; suggestedTarget?: string; confidence: number }>;
    }>(`/trial-balances/${input.tbId}/map`, {
      method: "POST",
      body: JSON.stringify({ confidenceThreshold: input.confidenceThreshold })
    });

    return {
      toolRunId,
      status: "succeeded",
      data: body
    };
  }

  async recommendTemplate(input: {
    jurisdiction: string;
    entityType: string;
    framework: string;
  }): Promise<
    DraftworxResponse<{
      templateId: string;
      confidence: number;
      rationale: string;
      options: Array<{ id: string; name: string; description: string; confidence: number }>;
    }>
  > {
    const toolRunId = randomUUID();
    const body = await this.request<
      Array<{ id: string; name: string; description: string; confidence: number; rationale: string }>
    >(`/templates?jurisdiction=${encodeURIComponent(input.jurisdiction)}&entityType=${encodeURIComponent(
      input.entityType
    )}&framework=${encodeURIComponent(input.framework)}`, {
      method: "GET"
    });

    const [best] = body;
    if (!best) {
      throw new Error("No templates available for provided context");
    }

    return {
      toolRunId,
      status: "succeeded",
      data: {
        templateId: best.id,
        confidence: best.confidence,
        rationale: best.rationale,
        options: body.map((entry) => ({
          id: entry.id,
          name: entry.name,
          description: entry.description,
          confidence: entry.confidence
        }))
      }
    };
  }

  async createDraft(input: {
    clientId: string;
    tbId: string;
    templateId: string;
  }): Promise<DraftworxResponse<{ draftUrl: string; summary: string }>> {
    const toolRunId = randomUUID();
    const body = await this.request<{ draftUrl: string; summary: string }>(`/drafts`, {
      method: "POST",
      body: JSON.stringify(input)
    });

    return {
      toolRunId,
      status: "succeeded",
      summary: body.summary,
      data: body
    };
  }
}
