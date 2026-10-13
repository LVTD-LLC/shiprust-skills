# Changelog

## 1.1.0 — 2026-10-14

- Add the `setup-shiprust` skill. The shiprust.com dashboard now copies a short prompt that points here and includes a fresh API key; the setup details live in the skill instead of the prompt.
- The `shiprust` skill's setup section now defers to `setup-shiprust`.

## 1.0.2 — 2026-10-09

- Make the native Codex plugin the default in the copyable setup prompt, README and agent instructions; require a specific reason for the standalone fallback.
- Document plugin verification and migration from duplicate standalone installations while preserving credentials.

## 1.0.1 — 2026-10-09

- Fix OpenClaw environment-reference setup: save without the pre-save probe, then require an explicit authenticated probe. Verified on OpenClaw 2026.9.6 using an isolated profile and disposable local app.
- Verify public GitHub marketplace installs in Codex and Claude Code and the complete REST helper generation/download/deletion workflow against the local app.

## 1.0.0 — 2026-10-09

- Official portable ShipRust skill with onboarding, MCP, REST, local development and deployment guidance.
- Claude Code, Codex and Cursor plugin manifests; native MCP configurations for OpenClaw, Hermes, OpenCode and VS Code.
- Non-destructive skill installer, credential-safe API helper, OpenAPI schema for ChatGPT Actions, and automated checks.
