# Hosted API and MCP

Authoritative guides: https://shiprust.com/docs/api and
https://shiprust.com/docs/mcp. Discover current choices with
`GET https://shiprust.com/api/v1/options` (public).

## Authentication and endpoints

Set `SHIPRUST_API_KEY` privately; every endpoint except options requires
`Authorization: Bearer <sr_ key>`. Cookies do not authenticate this API.
Keys inherit account access, are revocable and are limited to ten per account.

| REST path (under https://shiprust.com) | MCP equivalent | Response |
| --- | --- | --- |
| GET /api/v1/me | get_account | id, email, paid, created_at |
| GET /api/v1/options | list_options | hosts, capability keys, defaults, limits, template_version |
| GET /api/v1/projects | list_projects | projects array |
| POST /api/v1/projects | create_project | 201 project object |
| GET /api/v1/projects/{id} | get_project | project object |
| GET /api/v1/projects/{id}/download | no inline ZIP tool | ZIP bytes |
| DELETE /api/v1/projects/{id} | delete_project | 204, no body |

Creation, individual project reads and downloads require effective paid access.
Listing and deletion do not require payment; ownership is always enforced.
Delete removes the saved generator record, not downloaded code or a deployment.

## Create request

Only `name` is required (2–64 characters). `slug` derives from the name when
empty/omitted; max 40, lowercase `[a-z][a-z0-9-]*`, unique per account.
`description` defaults empty, max 1000 characters. `host` defaults `none`;
currently `none` and `caprover` are offered. Fetch options before relying on them.

`include_blog`, `include_docs`, `include_stripe`, `include_api` default true.
`include_mcp` follows `include_api` when omitted; explicit true needs API true.
`sentry_features` and `posthog_features` default to all available capabilities;
use `[]` to disable each integration. Currently:

- Sentry: sentry-errors, sentry-traces, sentry-logs, sentry-metrics, sentry-replay.
- PostHog: posthog-web, posthog-product, posthog-errors, posthog-logs, posthog-traces.

Unknown fields/capabilities are rejected. Do not send secrets to the generator.
Example request file `project.json` (non-secret):

```json
{
  "name": "Acme App",
  "host": "none",
  "include_blog": true,
  "include_docs": true,
  "include_stripe": false,
  "include_api": true,
  "include_mcp": true,
  "sentry_features": [],
  "posthog_features": []
}
```

From the installed skill directory, with the key already in the environment:

```sh
python3 scripts/shiprust_api.py account
python3 scripts/shiprust_api.py options
python3 scripts/shiprust_api.py projects
python3 scripts/shiprust_api.py create --file project.json
python3 scripts/shiprust_api.py project PROJECT_UUID
python3 scripts/shiprust_api.py download PROJECT_UUID --output acme-app.zip
# Destructive; only after explicit user authorization:
python3 scripts/shiprust_api.py delete PROJECT_UUID --confirm-delete
```

Project objects include id, name, slug, description, host, selected features,
template_version, created_at, url and download_url. REST URLs are relative to
https://shiprust.com; MCP returns absolute URLs. The download includes a
slug-named root directory and `.shiprust.toml`. Never print the ZIP as text.
The helper refuses overwrite and redirects, uses a timeout, and does not retry
writes. Account output contains private account data: don't paste it publicly.

## MCP transport

Endpoint: `POST https://shiprust.com/mcp`. Stateless Streamable HTTP, JSON-RPC 2.0,
JSON responses, no persistent session, no SSE, no resources or prompts.
Supported negotiated versions: 2025-06-18, 2025-03-26, 2024-11-05.
Send `Content-Type: application/json`, `Accept: application/json, text/event-stream`
and the bearer header. Initialize, send notifications/initialized, then list
and call tools. Use the negotiated MCP-Protocol-Version on subsequent calls.
Example initialize body:

```json
{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"shiprust-check","version":"1.0.0"}}}
```

A tools/call body:

```json
{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"get_account","arguments":{}}}
```

Inspect both JSON-RPC errors and tool-result `isError`. Correctable tool failures
carry structured status/message; invalid authentication is HTTP 401. HTTP 200
alone does not prove a successful operation. Unsupported version headers are 400.

## Error handling

REST errors are `{ "error": "message" }`: 400 malformed JSON, 401 key missing or
revoked, 402 access needed, 404 missing/not-owned project, 409 duplicate slug,
422 invalid input, 500 internal failure. A successful delete has no JSON body.
For read-only timeouts/5xx use bounded backoff. For ambiguous create/delete
outcomes, list/check current state before deciding whether another write is safe.
No idempotency-key contract, pagination, update, or upgrade endpoint is offered.
