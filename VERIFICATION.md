# Verification

Version 1.0.1; vendor formats checked 2026-10-09. See the linked sources in
[agent installation](skills/shiprust/references/agents.md).

Automated checks cover Python helper and installer behavior, manifest paths,
JSON syntax, secret-free fixtures, Markdown links, and OpenAPI operation contracts.
OpenAPI additionally validates against the OpenAPI 3.1 schema.

Client configuration examples are vendor-documentation/source checked. They are
not a claim of an interactive install test in every agent/OS. This environment
cannot launch every listed client. Native manifests are distinct: Codex bearer
variable configuration, Claude environment expansion, and Cursor plugin inputs.

MCP and REST use ShipRust's existing hosted interfaces; a live public options
request and rejection of unauthenticated API/MCP requests are safe checks.
Authenticated behavior is also covered by ShipRust's router integration suite.
Never use a real customer's project for a destructive smoke test.

ChatGPT direct MCP is intentionally not advertised as working: the hosted
connector does not support ShipRust's current API-key auth. A private GPT Action
can use bearer API-key authentication with the included schema; its UI import
and binary ZIP handling must be checked in the user's account. Public
marketplace review/approval is not part of this repository publication.

## Checks completed for the initial release

- 17 Python tests passed; OpenAPI 3.1 validator passed.
- Codex plugin validator passed, and the actual Codex CLI registered the local
  marketplace and installed `shiprust-skills@shiprust` in an isolated profile.
- Claude Code marketplace validator passed; actual isolated-profile marketplace
  registration and plugin installation passed.
- Live public options returned two hosts and five capabilities per telemetry
  provider; unauthenticated REST account and MCP requests both returned 401.
- Other GUI clients and ChatGPT Actions import remain documentation-checked,
  not interactively tested here.

## Additional 1.0.1 checks

- Codex and Claude Code both installed from the published GitHub repository in
  isolated profiles (not just a local checkout).
- OpenClaw 2026.9.6 persisted an environment reference without the credential
  and discovered ShipRust's authenticated tools against a disposable local app.
  Its pre-save probe failed with the literal reference; save with `--no-probe`
  and then run the mandatory explicit probe after config loading.
- The bundled REST helper completed account lookup, create, get, ZIP download,
  list and authorized delete against that local app. No production writes.
