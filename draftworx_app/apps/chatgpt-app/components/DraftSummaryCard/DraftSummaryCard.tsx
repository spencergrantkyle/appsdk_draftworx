import type { DraftSummaryProps } from "../types";

function DraftSummaryCard({
  toolRunId,
  status,
  draftUrl,
  summary,
  clientId,
  tbId,
  templateId,
  keyHighlights
}: DraftSummaryProps) {
  return (
    <section className="draftworx-card" data-tool-run={toolRunId}>
      <header className="draftworx-card__header">
        <h2 className="draftworx-card__title">Draft ready in Draftworx Cloud</h2>
        <p className="draftworx-card__summary">{summary}</p>
      </header>
      <div className="draftworx-card__content">
        <dl className="draftworx-definition-list">
          <div className="draftworx-definition-list__item">
            <dt>Client ID</dt>
            <dd><code>{clientId}</code></dd>
          </div>
          <div className="draftworx-definition-list__item">
            <dt>Trial balance ID</dt>
            <dd><code>{tbId}</code></dd>
          </div>
          <div className="draftworx-definition-list__item">
            <dt>Template</dt>
            <dd>{templateId}</dd>
          </div>
        </dl>
        <h3 className="draftworx-subheading">Key highlights</h3>
        <ul className="draftworx-list">
          {keyHighlights.map((highlight) => (
            <li key={highlight.label}>
              <strong>{highlight.label}:</strong> {highlight.value}
            </li>
          ))}
        </ul>
      </div>
      <footer className="draftworx-card__footer">
        <a className="draftworx-button" href={draftUrl} target="_blank" rel="noreferrer">
          Open in Draftworx
        </a>
        <span className={`draftworx-status draftworx-status--${status}`}>
          {status === "succeeded"
            ? "Draft successfully generated."
            : status === "failed"
            ? "Draft creation failed — retry from ChatGPT."
            : "Generating draft statements…"}
        </span>
      </footer>
    </section>
  );
}

export default DraftSummaryCard;
