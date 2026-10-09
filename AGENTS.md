# Maintaining ShipRust skills

This is public customer documentation, not the private ShipRust source code. Never publish the paid starter, private operations notes or credentials here.

Read README.md and skills/shiprust/SKILL.md. Keep API and MCP guidance aligned with https://shiprust.com/docs/api, https://shiprust.com/docs/mcp and the public /api/v1/options endpoint. Client formats differ: do not reuse environment interpolation blindly. Run `python3 -m unittest discover -s tests -v` and validate all JSON before a PR. Changes go through a branch and PR; update CHANGELOG.md. Do not claim a client was tested unless it actually was.

The Codex marketplace bundle is generated from canonical `skills/` and `configs/codex.mcp.json`. After edits, run `python3 scripts/build_codex_bundle.py`; tests reject drift. Do not edit mirrored skill files independently.
