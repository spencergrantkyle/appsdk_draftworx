import type { TrialBalanceUploadProps } from "../types";

function formatCurrency(value: number): string {
  return new Intl.NumberFormat("en-US", { style: "currency", currency: "USD" }).format(value);
}

function TrialBalanceUploader({
  toolRunId,
  status,
  uploadSummary,
  detectedAccounts,
  versionTag,
  allowedTypes,
  fileName
}: TrialBalanceUploadProps) {
  return (
    <section className="draftworx-card" data-tool-run={toolRunId}>
      <header className="draftworx-card__header">
        <h2 className="draftworx-card__title">Upload trial balance</h2>
        <p className="draftworx-card__summary">{uploadSummary}</p>
      </header>
      <div className="draftworx-card__content">
        <div className="draftworx-upload">
          <div className="draftworx-upload__meta">
            <div>
              <span className="draftworx-label">Accepted formats</span>
              <p className="draftworx-text-muted">{allowedTypes.join(", ")}</p>
            </div>
            <div>
              <span className="draftworx-label">Version tag</span>
              <code>{versionTag}</code>
            </div>
          </div>
          <div className="draftworx-upload__status" data-status={status}>
            {status === "succeeded" ? (
              <>
                ✅ Uploaded <strong>{fileName ?? "trial-balance"}</strong>
              </>
            ) : status === "failed" ? (
              <>⚠️ Upload failed — please retry with a CSV, XLSX, or ZIP.</>
            ) : (
              <>Waiting for secure upload…</>
            )}
          </div>
        </div>
        <table className="draftworx-table">
          <caption>Detected accounts</caption>
          <thead>
            <tr>
              <th scope="col">Account</th>
              <th scope="col" className="text-right">Balance</th>
            </tr>
          </thead>
          <tbody>
            {detectedAccounts.length === 0 ? (
              <tr>
                <td colSpan={2} className="draftworx-text-muted text-center">
                  No accounts detected yet.
                </td>
              </tr>
            ) : (
              detectedAccounts.map((account) => (
                <tr key={account.account}>
                  <td>{account.account}</td>
                  <td className="text-right">{formatCurrency(account.balance)}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </section>
  );
}

export default TrialBalanceUploader;
