# Install in your agent

Repository: https://github.com/LVTD-LLC/shiprust-skills

First inspect the client's version, active profile and existing configuration.
Install only for the agent the user is using. Never replace whole config files
or change unrelated servers/approval policies. Use one install route, not both
plugin and duplicated standalone skills. Restart/reload only as the client
requires, then verify `get_account`, `list_options` and `list_projects`.

## Portable installation

```sh
git clone https://github.com/LVTD-LLC/shiprust-skills.git
cd shiprust-skills
python3 scripts/install.py --agent codex --dry-run
python3 scripts/install.py --agent codex
```

Replace codex with claude, cursor, openclaw, hermes, opencode or copilot. This
installs the complete skill, including references and REST helper, and **does
not configure MCP or credentials**. For a non-default profile use
`--skills-dir /absolute/path/to/active/skills`. Conflicting files stop the
install without overwrite; identical reinstall is safe. The agent should next
merge the matching configuration below itself as part of the requested setup.
Samples live in the repo's `configs/`; installed skills can follow the examples
below without retaining the clone. Do not install globally from a shared agent
without choosing the correct owner's profile.

## Credentials

Create a dedicated key at https://shiprust.com/settings. Use the client's
secret store or protected environment entry so both MCP and the agent's shell
receive `SHIPRUST_API_KEY`. A terminal session and a GUI app may have different
environments. Never place the value in Git or a command argument. On POSIX a
one-session, non-echoing prompt can populate the launch environment:

```sh
read -r -s -p 'ShipRust API key: ' SHIPRUST_API_KEY; printf '\n'
export SHIPRUST_API_KEY
# Launch your agent from this shell.
```

This Bash command does not persist the key. On Windows use the agent's protected
credential UI or a process-local secure prompt; do not paste it in shell history.
Never assume a sample's placeholder was expanded: test authenticated access.

## Claude Code — native plugin

```text
/plugin marketplace add LVTD-LLC/shiprust-skills
/plugin install shiprust-skills@shiprust
```

The root `.claude-plugin/plugin.json`, `.mcp.json` and skills are packaged together.
Set the runtime key before launching. Restart/start a fresh session, inspect
`/mcp`, then use `/shiprust-skills:shiprust`. No marketplace approval is needed
for this self-hosted catalog, but honor client trust prompts.

Standalone alternative: install the skill and merge this into project `.mcp.json`
(or the client's supported user scope):

```json
{"mcpServers":{"shiprust":{"type":"http","url":"https://shiprust.com/mcp","headers":{"Authorization":"Bearer ${SHIPRUST_API_KEY}"}}}}
```

Sources: [plugins](https://code.claude.com/docs/en/plugin-marketplaces),
[MCP](https://code.claude.com/docs/en/mcp).

## OpenAI Codex — native plugin or skill + MCP

The native Codex bundle under `plugins/shiprust-skills/` has its own
`.mcp.json` using `bearer_token_env_var`, avoiding Claude's different format.
On Codex versions with plugin marketplace support:

```sh
codex plugin marketplace add LVTD-LLC/shiprust-skills
codex plugin add shiprust-skills@shiprust
```

Start a new thread after installing. The marketplace is maintained by ShipRust,
not OpenAI's reviewed public directory. If plugins are unavailable, use the
portable skill and native MCP route below (do not install both).

The portable installer plus native MCP registration is the explicit CLI path:

```sh
python3 scripts/install.py --agent codex
codex mcp add shiprust --url https://shiprust.com/mcp --bearer-token-env-var SHIPRUST_API_KEY
```

If `shiprust` exists, inspect/merge it instead of replacing it. Equivalent block
for the active `$CODEX_HOME/config.toml` (default `~/.codex/config.toml`):

```toml
[mcp_servers.shiprust]
url = "https://shiprust.com/mcp"
bearer_token_env_var = "SHIPRUST_API_KEY"
```

The portable skill default is `~/.agents/skills/shiprust`. Verify with
`codex mcp list`, start a fresh thread and call the read-only tools. A plugin
manifest in GitHub does not mean it is listed in OpenAI's public directory.
Sources: [MCP](https://developers.openai.com/codex/mcp),
[plugin packaging](https://developers.openai.com/plugins/build/plugins).

## ChatGPT — API-key Actions fallback, not direct MCP

Ordinary ChatGPT conversations cannot install filesystem skills. ChatGPT's
hosted MCP connection does not accept custom API-key headers; ShipRust currently
has no OAuth server. Do **not** choose "No authentication" or put the key in a URL.

Where custom GPT Actions are available, create a **private** GPT, add the skill
instructions, and import the repository's `openapi.json` as an Action schema.
Set Action authentication to **API Key → Bearer** and enter the key only in that
protected field. Test `getAccount`, `listOptions` and `listProjects`. Review
write confirmations. This is a manual account/UI step; a repository prompt
cannot install a private GPT on the user's behalf. Keep it private: the key
has the full access of its owner, not the access of someone you share it with.

The schema includes project metadata and download endpoints; clients may not
handle an authenticated ZIP response as a usable artifact. In that case use
the browser dashboard download or hand off to Codex/a terminal agent. A plain
chat with no Actions can explain the steps but cannot perform authenticated
operations. Codex with a configured execution environment is the full path.

Sources: [GPT Action authentication](https://developers.openai.com/api/docs/actions/authentication),
[hosted MCP authentication limitations](https://developers.openai.com/plugins/build/auth).

## Cursor — plugin and native MCP

The root `.cursor-plugin/plugin.json` declares the SHIPRUST_API_KEY variable;
`mcp.json` uses `${SHIPRUST_API_KEY}` for plugin-variable substitution. Import
this plugin through Cursor's available local/team plugin installation flow.
It is **not** automatically listed in Cursor's reviewed public marketplace.

Portable fallback: install with `--agent cursor`, then merge
`configs/cursor.mcp.json` into `~/.cursor/mcp.json` (or `.cursor/mcp.json` in
this project). Standalone MCP interpolation is different:

```json
{"mcpServers":{"shiprust":{"url":"https://shiprust.com/mcp","headers":{"Authorization":"Bearer ${env:SHIPRUST_API_KEY}"}}}}
```

Reload Cursor's tools and verify the account. Sources:
[plugins](https://cursor.com/docs/reference/plugins),
[MCP](https://cursor.com/docs/mcp).

## OpenClaw — skill pack and managed MCP connection

Install with `--agent openclaw` or select the active workspace's `skills/`
directory explicitly. OpenClaw uses Agent Skills; a JavaScript extension is not
needed. On versions with native HTTP MCP, use the scoped CLI (literal shell
single quotes preserve the env reference):

```sh
openclaw mcp add shiprust --url https://shiprust.com/mcp --transport streamable-http --header 'Authorization=Bearer ${SHIPRUST_API_KEY}'
openclaw mcp probe shiprust --json
```

Inspect existing server first. Equivalent config fragment (`configs/openclaw.json`):

```json
{"mcp":{"servers":{"shiprust":{"url":"https://shiprust.com/mcp","transport":"streamable-http","headers":{"Authorization":"Bearer ${SHIPRUST_API_KEY}"}}}}}
```

The gateway runtime must receive the secret, not only the operator's shell.
Prefer its supported secret resolver/environment setup. Older builds that do
not support HTTP MCP should use the skill's REST helper, not a second gateway
or an untrusted credential proxy. After config reload start a fresh agent turn.
Sources: [skills](https://docs.openclaw.ai/tools/skills),
[MCP](https://docs.openclaw.ai/tools/mcp).

## Hermes — native skill tap and MCP

```sh
hermes skills tap add LVTD-LLC/shiprust-skills
hermes skills install LVTD-LLC/shiprust-skills/shiprust
```

Or use the portable installer with `--agent hermes`. Merge this into the active
profile's `~/.hermes/config.yaml`, preserving the rest:

```yaml
mcp_servers:
  shiprust:
    url: https://shiprust.com/mcp
    headers:
      Authorization: "Bearer ${SHIPRUST_API_KEY}"
```

Current Hermes resolves environment placeholders in MCP config. Supply the key
to the active profile's protected environment, then start a new session and
check actual account calls. For older versions without that expansion, use
REST rather than saving a literal placeholder or exposing the key.
Sources: [skills](https://hermes-agent.nousresearch.com/docs/user-guide/features/skills/),
[MCP](https://hermes-agent.nousresearch.com/docs/user-guide/features/mcp/),
[environment interpolation source](https://github.com/NousResearch/hermes-agent/blob/main/tools/mcp_tool_config.py).

## OpenCode — native skill and MCP

Install with `--agent opencode` and merge the repository's `configs/opencode.json`
into the active `~/.config/opencode/opencode.json` or project `opencode.json`:

```json
{"mcp":{"shiprust":{"type":"remote","url":"https://shiprust.com/mcp","oauth":false,"headers":{"Authorization":"Bearer {env:SHIPRUST_API_KEY}"}}}}
```

Disable OAuth for this server because ShipRust uses bearer keys. Preserve JSONC
comments if the existing file is JSONC. Verify with `opencode mcp list` and a
new session's account tool. Sources: [skills](https://opencode.ai/docs/skills/),
[MCP](https://opencode.ai/docs/mcp-servers/).

## VS Code / GitHub Copilot and other agents

Copy the complete skill into a supported skills location (`--agent copilot`
uses `~/.copilot/skills`) and merge `configs/vscode.mcp.json` into the workspace's
`.vscode/mcp.json`. Its `inputs` prompt stores no key in the repository; mark it
password input. See [VS Code MCP](https://code.visualstudio.com/docs/copilot/customization/mcp-servers).
Other Agent Skills clients can load this entire skill directory and use a
native Streamable HTTP server with a bearer header, or the REST helper.
Never assume a `.mcp.json` file has the same schema/interpolation everywhere.

## Updates and verification scope

Update the clone with a reviewed release/ref. Plugin managers have their own
update flow; the portable installer refuses changed installed files so you can
review local customizations before replacing them. Revoke leaked/unused keys
in ShipRust Settings. Removing a plugin does not revoke its key.

These formats are based on vendor documentation checked on 2026-10-09.
Automated tests cover assets and helper behavior; a specific client/OS is only
verified when its install and authenticated calls have actually been exercised.
