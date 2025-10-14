import type { TemplateRecommendationProps } from "../types";

function formatConfidence(value: number): string {
  return `${Math.round(value * 100)}% match`;
}

function TemplateSelector({
  toolRunId,
  status,
  templateId,
  confidence,
  rationale,
  options
}: TemplateRecommendationProps) {
  return (
    <section className="draftworx-card" data-tool-run={toolRunId}>
      <header className="draftworx-card__header">
        <h2 className="draftworx-card__title">Recommended reporting template</h2>
        <p className="draftworx-card__summary">{rationale}</p>
      </header>
      <div className="draftworx-card__content">
        <div className="draftworx-template">
          <div className="draftworx-template__badge">{formatConfidence(confidence)}</div>
          <div className="draftworx-template__body">
            <h3>{templateId}</h3>
            <p className="draftworx-text-muted">
              Draftworx selected this template based on jurisdiction, entity type, and framework.
            </p>
          </div>
        </div>
        <details className="draftworx-details">
          <summary>Alternative templates</summary>
          <ul className="draftworx-list">
            {options.map((option) => (
              <li key={option.id}>
                <strong>{option.name}</strong>
                <div className="draftworx-text-muted">{option.description}</div>
              </li>
            ))}
          </ul>
        </details>
      </div>
      <footer className="draftworx-card__footer">
        <span className={`draftworx-status draftworx-status--${status}`}>
          {status === "succeeded"
            ? "Template locked for draft creation."
            : status === "failed"
            ? "Template recommendation failed — select manually."
            : "Waiting on Draftworx recommendation…"}
        </span>
      </footer>
    </section>
  );
}

export default TemplateSelector;
