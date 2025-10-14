import type { ContextCollectorProps, ContextField } from "../types";

const requiredOrder: ContextField["key"][] = [
  "jurisdiction",
  "entityType",
  "yearEnd",
  "framework"
];

function formatKey(key: ContextField["key"]): string {
  switch (key) {
    case "jurisdiction":
      return "Jurisdiction";
    case "entityType":
      return "Entity type";
    case "yearEnd":
      return "Year-end date";
    case "framework":
      return "Reporting framework";
    default:
      return key;
  }
}

function ContextCollector({ toolRunId, summary, fields, missingFields }: ContextCollectorProps) {
  const orderedFields = [...fields].sort(
    (a, b) => requiredOrder.indexOf(a.key) - requiredOrder.indexOf(b.key)
  );

  return (
    <section className="draftworx-card" data-tool-run={toolRunId}>
      <header className="draftworx-card__header">
        <h2 className="draftworx-card__title">Draftworx context checklist</h2>
        <p className="draftworx-card__summary">{summary}</p>
      </header>
      <div className="draftworx-card__content">
        <ol className="draftworx-steps" aria-label="Context collection status">
          {orderedFields.map((field) => {
            const isMissing = missingFields.includes(field.key);
            return (
              <li key={field.key} className="draftworx-steps__item">
                <div className="draftworx-steps__marker" data-state={isMissing ? "pending" : "complete"}>
                  {isMissing ? "⏳" : "✅"}
                </div>
                <div className="draftworx-steps__body">
                  <div className="draftworx-steps__label">{formatKey(field.key)}</div>
                  <div className="draftworx-steps__value">
                    {field.value ? (
                      <code>{field.value}</code>
                    ) : (
                      <span className="draftworx-text-muted">Awaiting input</span>
                    )}
                  </div>
                  {field.helperText && (
                    <p className="draftworx-helper">{field.helperText}</p>
                  )}
                </div>
              </li>
            );
          })}
        </ol>
        {missingFields.length > 0 ? (
          <div className="draftworx-alert" role="status">
            Provide the missing information so we can create the client in Draftworx.
          </div>
        ) : (
          <div className="draftworx-alert draftworx-alert--success" role="status">
            All required fields captured. Ready to create the Draftworx client.
          </div>
        )}
      </div>
    </section>
  );
}

export default ContextCollector;
