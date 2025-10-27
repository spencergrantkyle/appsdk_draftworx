# Repository Guidelines EDIT

## Project Structure & Module Organization
The front-end widgets live in `src/`, with each widget isolated in its own folder exposing an `index.jsx` or `index.tsx`. Bundled assets are emitted into `assets/` by `build-all.mts`; never edit them manually. MCP backends are provided in `pizzaz_server_node/`, `pizzaz_server_python/`, and `solar-system_server_python/`, each serving the bundles produced under `assets/`. Shared TypeScript configs (`tsconfig*.json`) and Tailwind setup (`tailwind.config.ts`) sit at the repo root.

## Build, Test, and Development Commands
Install dependencies with `pnpm install` at the repo root. Use `pnpm run dev` to launch the Vite dev server against the widget gallery, and `pnpm run dev:host` when iterating on the host integration. Ship-ready bundles come from `pnpm run build`, while `pnpm run serve` previews the generated assets on port 4444. Type checking runs with `pnpm run tsc`, and the Pizzaz Node MCP server starts via `pnpm --filter pizzaz_server_node start`. Python servers rely on `uvicorn <server>.main:app --port <port>` after creating a virtualenv and installing the respective `requirements.txt`.

## Coding Style & Naming Conventions
Favor TypeScript or modern JSX modules with ES modules (`import`/`export`) and default exports named `App` for widget entrypoints. Use two-space indentation, trailing commas where valid, and double-quoted strings to match existing code. Keep component folders self-contained: colocate supporting CSS and JSON, and load global styles through `src/index.css`. Run `pnpm run build` before submitting to ensure new entry folders are auto-discovered by the globbing rules in `build-all.mts`.

## Testing Guidelines
The repository does not yet ship automated UI tests, so treat `pnpm run build` and a smoke run of the relevant MCP server as required pre-PR checks. When adding server logic, include lightweight request handlers or schema validations that can be exercised with unit tests (e.g., Jest or Pytest) placed alongside the server code. Document any manual verification steps (screenshots, recordings, or cURL transcripts) in the PR until an automated harness lands.

## Commit & Pull Request Guidelines
Write commit subjects in the imperative mood and keep them under 72 characters; scoped conventional commits such as `fix(vite): …` match the existing history. Each PR should summarize the change, link any relevant issues, and call out which widgets or servers were affected. Attach before/after screenshots or GIFs for UI-facing work and note the commands you ran (`pnpm run build`, server start scripts) in the PR checklist.

