import type { ClientConfirmationProps } from "../types";

function toSentenceCase(value: string | undefined): string {
  if (!value) return "";
  return value.charAt(0).toUpperCase() + value.slice(1);
}

function ClientConfirmation({ toolRunId, status, clientId, summary, context }: ClientConfirmationProps) {
  const entries = Object.entries(context);
  return (
    <section className="draftworx-card" data-tool-run={toolRunId}>
      <header className="draftworx-card__header">
        <h2 className="draftworx-card__title">Confirm Draftworx client</h2>
        <p className="draftworx-card__summary">{summary}</p>
      </header>
      <div className="draftworx-card__content">
        <dl className="draftworx-definition-list">
          {entries.map(([key, value]) => (
            <div key={key} className="draftworx-definition-list__item">
              <dt>{toSentenceCase(key)}</dt>
              <dd>{value || <span className="draftworx-text-muted">Missing</span>}</dd>
            </div>
          ))}
        </dl>
        <footer className="draftworx-card__footer">
          <span className={`draftworx-status draftworx-status--${status}`}>
            {status === "succeeded" && clientId ? (
              <>Registered as <code>{clientId}</code></>
            ) : status === "failed" ? (
              <>Creation failed — retry from ChatGPT</>
            ) : (
              <>Confirming client…</>
            )}
          </span>
        </footer>
      </div>
    </section>
  );
}

export default ClientConfirmation;
