# ShipRust skills

Official AI-agent toolkit for [ShipRust](https://shiprust.com): connect your
account, generate a Rust SaaS project, download it, and help build and deploy it.
**Public skills and configuration only — not the paid starter source.**

## Give this to your agent

> Set up ShipRust for me by following the directions at https://github.com/LVTD-LLC/shiprust-skills. Install the native ShipRust plugin for the AI agent I am using. For Codex, first run `codex plugin marketplace add LVTD-LLC/shiprust-skills` and `codex plugin add shiprust-skills@shiprust`; use the standalone skill and MCP setup only if native plugins are unavailable, and explain why. Use the documented REST API if MCP is unavailable. Use SHIPRUST_API_KEY from my environment, or help me add it securely if it is missing. Verify my account and list the available project options. Do not create or delete projects yet. Never print or commit my API key.

Agents: start with **[skills/shiprust/SKILL.md](skills/shiprust/SKILL.md)** and
**[installation instructions](skills/shiprust/references/agents.md)**. If browsing
GitHub fails, fetch the corresponding file from
`https://raw.githubusercontent.com/LVTD-LLC/shiprust-skills/main/`.

Create your API key in [Settings](https://shiprust.com/settings). Keys are shown
once; the creation page can copy a prompt with that key for a trusted private
agent conversation. Prefer the agent's protected environment/secret entry.
A key gives the agent your account's access. Never paste it into public chats.

## Install

**Codex: install the native plugin first.** It bundles the skill, references,
REST helper and MCP server; do not also install the standalone skill or register
a duplicate MCP server.

```sh
codex plugin marketplace add LVTD-LLC/shiprust-skills
codex plugin add shiprust-skills@shiprust
codex plugin list --marketplace shiprust --json
```

Provide `SHIPRUST_API_KEY` securely to the Codex runtime, then start a fresh
chat and verify the account. Installation alone does not configure credentials.
If this Codex version does not support native plugins, explain that limitation
and use the portable fallback below. Do not silently choose the fallback on a
plugin-capable Codex installation.

Claude Code's native plugin:

```text
/plugin marketplace add LVTD-LLC/shiprust-skills
/plugin install shiprust-skills@shiprust
```

Portable fallback for clients without native plugin support (Python 3.10+; no dependencies):

```sh
git clone https://github.com/LVTD-LLC/shiprust-skills.git
cd shiprust-skills
python3 scripts/install.py --agent codex --dry-run
python3 scripts/install.py --agent codex
```

For this portable fallback, have the agent merge its matching MCP config and verify the connection.
The installer deliberately does not overwrite configurations, collect keys,
change approvals, or restart services. See the complete
[client instructions](skills/shiprust/references/agents.md) for exact paths,
environment setup, native commands, verification and update behavior.

| Client | Included path | MCP configuration |
| --- | --- | --- |
| Codex | Native plugin (default); portable skill only when plugins are unavailable | [Codex TOML](configs/codex.toml), [plugin MCP](configs/codex.mcp.json) |
| Claude Code | Native plugin + self-hosted marketplace | [.mcp.json](.mcp.json) |
| Cursor | `.cursor-plugin/plugin.json` or portable skill | [standalone config](configs/cursor.mcp.json), [plugin config](mcp.json) |
| OpenClaw | Native skill pack, no JS extension needed | [managed MCP fragment](configs/openclaw.json) |
| Hermes | Native skills tap or portable skill | [YAML fragment](configs/hermes.yaml) |
| OpenCode | Native Agent Skill | [JSON fragment](configs/opencode.json) |
| VS Code / Copilot | Portable Agent Skill | [MCP + protected input](configs/vscode.mcp.json) |
| ChatGPT | Private GPT Actions REST fallback | [OpenAPI schema](openapi.json); manual setup required |
| Other agents | Complete `skills/shiprust` directory | Streamable HTTP + bearer header or REST helper |

No claim of public marketplace approval/listing is made. Native packaging and
installation differ by client/version. ChatGPT's direct hosted MCP connector
requires OAuth for authenticated access; ShipRust currently uses API keys.
Use the documented private GPT Actions path or Codex, not an unauthenticated
connector. Plain chat cannot install local tools. See
[compatibility details and vendor sources](skills/shiprust/references/agents.md).

## What is included

- A portable skill covering onboarding, generation, safe downloads, working on
  existing apps, feature configuration, local checks and deployment.
- Native plugin manifests and secret-free MCP config fragments.
- [MCP/REST reference](skills/shiprust/references/api.md), full
  [OpenAPI schema](openapi.json), and a dependency-free
  [API helper](skills/shiprust/scripts/shiprust_api.py).
- [Development guide](skills/shiprust/references/development.md) explaining the
  generated app, mail verification, Stripe, observability, migrations and hosting.

Hosted MCP: `https://shiprust.com/mcp` (Streamable HTTP).
Hosted REST: `https://shiprust.com/api/v1`.
Both use `Authorization: Bearer <key>` and enforce the same account/ownership
rules. Creating, reading an individual project and downloading need effective
paid access. `GET /api/v1/options` is public. New project defaults enable
optional integrations but do not provide their credentials.

The generated app has its **own** API/MCP and keys. Never send your ShipRust key
to that app, another domain or a proxy. Read its README and AGENTS.md after
extracting; this toolkit does not replace project-specific instructions.

## Verify and maintain

```sh
python3 -m unittest discover -s tests -v
python3 skills/shiprust/scripts/shiprust_api.py options
```

Tests exercise installer conflict/idempotency handling, request safety,
authentication, response handling, configuration formats, local references and
OpenAPI contracts. Live read-only API/MCP checks and validation results are in
[VERIFICATION.md](VERIFICATION.md). Never equate a valid file with a working
connection in every client. Report issues in this repository without credentials
or private account/project details. Changes go through PRs; see [CHANGELOG.md](CHANGELOG.md).

MIT licensed for this toolkit only; ShipRust-generated code has its own license.
