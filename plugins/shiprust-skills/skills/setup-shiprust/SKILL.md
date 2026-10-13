---
name: setup-shiprust
description: Connect the current AI agent to the user's ShipRust account — install the ShipRust plugin or skill, store the user's ShipRust API key securely, connect the MCP server (or REST fallback) and verify access. Use when the user asks to set up ShipRust or pastes the setup prompt from their shiprust.com dashboard.
license: MIT
---

# Set up ShipRust

The user copied a setup prompt from their ShipRust dashboard. It usually contains
a fresh API key (`sr_` followed by 64 hex characters). Your job is to leave this
agent able to use ShipRust, then stop. **Do not create or delete projects** during
setup.

If you are reading this from GitHub before anything is installed, fetch linked
files from `https://raw.githubusercontent.com/LVTD-LLC/shiprust-skills/main/`.

## 1. Protect the key

- Treat the key like a password. Never print, echo, log, commit or repeat it, and
  never put it in a URL, command argument, screenshot or your final summary.
- Store it as `SHIPRUST_API_KEY` in this agent's protected environment or secret
  store, so both the MCP connection and the agent's shell receive it. Explain
  where you stored it, not what it is.
- Only ever send it to `https://shiprust.com`. Never to a generated app, another
  domain or a proxy.
- If the prompt has no key, use `SHIPRUST_API_KEY` from the environment. If that is
  missing too, ask the user to open https://shiprust.com/dashboard and copy the
  setup prompt again. Don't invent a key.

## 2. Install for this agent only

Detect the actual client and version. Install only for the agent the user is
using, without overwriting existing settings, disabling approvals or restarting a
shared service without permission. Prefer the native plugin:

- **Claude Code:** `/plugin marketplace add LVTD-LLC/shiprust-skills`, then
  `/plugin install shiprust-skills@shiprust`.
- **Codex:** check `codex plugin --help`, then
  `codex plugin marketplace add LVTD-LLC/shiprust-skills` and
  `codex plugin add shiprust-skills@shiprust`.
- **Cursor, OpenClaw, Hermes, OpenCode, VS Code / Copilot, ChatGPT and others:**
  follow [agent installation](../shiprust/references/agents.md).

Use the portable skill plus a separate MCP entry only when native plugins are
unavailable, and tell the user the specific reason. Never install both routes.
Native plugins already bundle the MCP server; do not register a duplicate.

## 3. Connect

- MCP: `https://shiprust.com/mcp`, Streamable HTTP, header
  `Authorization: Bearer <key>`. Interpolation syntax differs by client; follow
  [agent installation](../shiprust/references/agents.md) rather than a generic
  sample. Reload tools or start a fresh session if the client requires it.
- If MCP is unavailable or blocked, use the [REST API](../shiprust/references/api.md)
  and its dependency-free helper `scripts/shiprust_api.py` in the `shiprust`
  skill. It reads the same environment variable.

## 4. Verify (read-only)

Call `get_account`, `list_options` and `list_projects` (or `GET /api/v1/me`,
`/api/v1/options`, `/api/v1/projects`). A saved config or a successful tools list
is not proof; an authenticated `get_account` is. If the account has no paid
access, point the user to https://shiprust.com/billing; never buy anything.

## 5. Report

Keep it short: what you installed, where the key is stored (not its value),
which transport works, whether the account has access, and any remaining
limitation. Then tell the user they can ask for a project, for example
"Create a ShipRust project called Acme and run it locally." From then on, use the
[ShipRust skill](../shiprust/SKILL.md).
