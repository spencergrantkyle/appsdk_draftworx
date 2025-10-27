# Draftworx ChatGPT App Architecture

This example extends the Apps SDK gallery with a sequential Draftworx onboarding flow tailored for accountants and finance teams. The conversation state lives in the MCP server so that widgets can maintain continuity across tool runs and Draftworx keeps the authoritative record of clients, trial balances, mappings, and drafts.

## Components

- **ContextCollector** – Tracks which context fields are complete and prompts for missing ones.
- **ClientConfirmation** – Shows a confirmation checklist after the Draftworx client is created.
- **TBUploader** – Surfaces upload status, detected accounts, and versioning.
- **MappingReview** – Highlights confirmed mappings versus low-confidence accounts.
- **TemplateSelector** – Recommends the best reporting template and provides alternatives.
- **DraftSummaryCard** – Presents the final draft with an “Open in Draftworx” link.

Each component is bundled for use as an Apps SDK widget via the `ui://draftworx/*.html` templates referenced in the manifest and MCP server metadata.

## Sequential Flow

1. Collect reporting context with `draftworx.collect_context`.
2. Confirm the Draftworx client via `draftworx.create_client`.
3. Upload the trial balance using `draftworx.upload_trial_balance`.
4. Auto-map accounts with `draftworx.map_accounts`.
5. Recommend a template through `draftworx.recommend_template`.
6. Generate the draft handoff with `draftworx.create_draft`.

The MCP server enforces this order by validating session state before each handler runs.

## Telemetry

Minimal telemetry records every tool invocation with the toolRunId, status, timestamp, and any error message. This buffer can be extended to push events into Draftworx observability pipelines.

## Draftworx API integration

The `DraftworxClient` wraps REST endpoints:

- `POST /clients`
- `POST /trial-balances`
- `POST /trial-balances/{tbId}/map`
- `GET /templates`
- `POST /drafts`

Replace the placeholder `https://api.draftworx.test` base URL and provide an API key via the `DRAFTWORX_API_KEY` environment variable to call a live environment.
