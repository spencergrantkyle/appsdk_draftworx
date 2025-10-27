export type SessionKey = string;

export interface DraftworxSessionState {
  toolRunSequence: string[];
  context?: {
    entityType?: string;
    jurisdiction?: string;
    yearEnd?: string;
    framework?: string;
    completed?: boolean;
  };
  clientId?: string;
  tbId?: string;
  versionTag?: string;
  templateId?: string;
}

class SessionStore {
  private readonly sessions = new Map<SessionKey, DraftworxSessionState>();

  get(sessionId: SessionKey): DraftworxSessionState {
    if (!this.sessions.has(sessionId)) {
      this.sessions.set(sessionId, { toolRunSequence: [] });
    }

    return this.sessions.get(sessionId)!;
  }

  update(sessionId: SessionKey, update: Partial<DraftworxSessionState>): DraftworxSessionState {
    const current = this.get(sessionId);
    const next: DraftworxSessionState = {
      ...current,
      ...update,
      context: {
        ...current.context,
        ...update.context
      }
    };
    this.sessions.set(sessionId, next);
    return next;
  }

  pushToolRun(sessionId: SessionKey, toolRunId: string) {
    const state = this.get(sessionId);
    state.toolRunSequence.push(toolRunId);
  }
}

export const sessionStore = new SessionStore();
