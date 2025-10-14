# Draftworx Financial Draft Assistant Example

This example demonstrates how to adapt the Apps SDK gallery for Draftworx accountants. It combines a ChatGPT App manifest, Draftworx-specific widgets, and an MCP server that orchestrates the workflow from context capture to draft creation.

## Structure

```
draftworx_app/
  apps/chatgpt-app/
    manifest.json
    components/
      ContextCollector/
      ClientConfirmation/
      TBUploader/
      MappingReview/
      TemplateSelector/
      DraftSummaryCard/
      styles.css
  services/mcp/
    handlers/
    lib/
    db/
    server.ts
  tests/e2e/
  docs/
```

## Getting started

1. Install dependencies at the repo root (`pnpm install`).
2. Build the Apps SDK bundles (`pnpm run build`) to generate the `ui://draftworx/*.html` templates referenced by the manifest.
3. Start the Draftworx MCP server:

```bash
cd draftworx_app/services/mcp
pnpm install
pnpm start
```

Expose environment variables for Draftworx credentials before starting the server:

```bash
export DRAFTWORX_API_BASE_URL="https://api.draftworx.test"
export DRAFTWORX_API_KEY="sk_live_..."
```

The server listens on port `8010` and exposes the SSE stream at `/mcp`.

## Sequential flow

The MCP server enforces the required order:

1. `draftworx.collect_context`
2. `draftworx.create_client`
3. `draftworx.upload_trial_balance`
4. `draftworx.map_accounts`
5. `draftworx.recommend_template`
6. `draftworx.create_draft`

If a tool is invoked out of sequence, the server returns a descriptive error so the assistant can guide the user back on track.
