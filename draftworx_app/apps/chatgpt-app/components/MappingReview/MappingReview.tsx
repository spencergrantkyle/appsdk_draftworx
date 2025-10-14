import type { MappingReviewProps } from "../types";

function MappingReview({
  toolRunId,
  status,
  confirmedMappings,
  unresolvedAccounts,
  confidenceThreshold
}: MappingReviewProps) {
  return (
    <section className="draftworx-card" data-tool-run={toolRunId}>
      <header className="draftworx-card__header">
        <h2 className="draftworx-card__title">Account mapping review</h2>
        <p className="draftworx-card__summary">
          Auto-mapping confidence threshold: {Math.round(confidenceThreshold * 100)}%
        </p>
      </header>
      <div className="draftworx-card__content draftworx-grid">
        <div>
          <h3 className="draftworx-subheading">Confirmed mappings</h3>
          <ul className="draftworx-list">
            {confirmedMappings.length === 0 ? (
              <li className="draftworx-text-muted">No confirmed mappings yet.</li>
            ) : (
              confirmedMappings.map((mapping) => (
                <li key={`${mapping.source}-${mapping.target}`}>
                  <strong>{mapping.source}</strong> → {mapping.target} ({Math.round(mapping.confidence * 100)}%)
                </li>
              ))
            )}
          </ul>
        </div>
        <div>
          <h3 className="draftworx-subheading">Needs review</h3>
          <ul className="draftworx-list">
            {unresolvedAccounts.length === 0 ? (
              <li className="draftworx-text-muted">No low-confidence mappings.</li>
            ) : (
              unresolvedAccounts.map((account) => (
                <li key={account.account}>
                  <div className="draftworx-list__item">
                    <div>
                      <strong>{account.account}</strong>
                      <div className="draftworx-text-muted">
                        {Math.round(account.confidence * 100)}% confidence
                      </div>
                    </div>
                    {account.suggestedTarget && (
                      <div className="draftworx-suggestion">Suggested: {account.suggestedTarget}</div>
                    )}
                  </div>
                </li>
              ))
            )}
          </ul>
        </div>
      </div>
      <footer className="draftworx-card__footer">
        <span className={`draftworx-status draftworx-status--${status}`}>
          {status === "succeeded"
            ? "Mappings synced to Draftworx."
            : status === "failed"
            ? "Mapping failed — review flagged accounts."
            : "Waiting for Draftworx mapping results…"}
        </span>
      </footer>
    </section>
  );
}

export default MappingReview;
