export interface TelemetryEvent {
  toolRunId: string;
  toolName: string;
  status: "pending" | "succeeded" | "failed";
  timestamp: string;
  error?: string;
}

class TelemetryBuffer {
  private readonly events: TelemetryEvent[] = [];

  record(event: TelemetryEvent) {
    this.events.push(event);
  }

  recent(limit = 20): TelemetryEvent[] {
    return this.events.slice(-limit);
  }
}

export const telemetryBuffer = new TelemetryBuffer();
