# From ZIP to running product

Follow the README and AGENTS.md inside **the downloaded project**, not the
private shiprust.com repository. This guide supplies orientation, not a copy of
the paid starter or a promise that every template revision is identical.

## Local setup

1. Inspect `.shiprust.toml` and `Cargo.toml` to identify chosen features/host.
2. Install a supported stable Rust toolchain and Docker Compose. Use the
   project's toolchain pin if present. Check port conflicts before starting DBs.
3. In the extracted project, follow its README, typically:

```sh
docker compose up -d
cp .env.example .env
cargo run
```

Do not overwrite an existing `.env`. Postgres migrations run at startup; point
local `DATABASE_URL` at the local database, never production. Open
http://localhost:3000 and check `/healthz` plus relevant routes.

## Credentials and optional features

- Signup needs the customer's Mailgun domain, domain-scoped sending key,
  `MAIL_FROM`, and an independent random `EMAIL_VERIFICATION_KEY` (at least
  32 characters). With all absent, signup is disabled; partial config can stop
  startup. The six-character verification flow is mandatory, not a bug to bypass.
- Stripe needs the customer's account, prices and webhook configuration. Follow
  the generated billing guide, use test mode locally, and do not copy ShipRust's
  site purchase/product identifiers. Creating a project never charges Stripe.
- Sentry and PostHog need the customer's own credentials/config. Selected Cargo
  features do not mean collection is configured. Keep server secrets out of
  client assets; preserve scrubbing and replay/privacy defaults.
- Generated API keys are created in the **generated app's** settings. Do not
  reuse `SHIPRUST_API_KEY`. Generated `/mcp` starts with `get_account`, not
  ShipRust's project generator tools. Add business tools with authorization and
  ownership checks; never expose arbitrary SQL or shell execution.

## Development discipline

The app is server-rendered Axum + Maud; SQLx checks queries; shared infrastructure
lives under `crates/`, product behavior under `app/`. Avoid adding an unnecessary
JavaScript build pipeline. Follow project AGENTS.md for module boundaries.

- Add new migrations instead of editing applied ones.
- After SQL changes regenerate and commit `.sqlx/` using the project's commands.
- Run format, clippy, relevant tests, SQLx prepare/check and offline compilation
  required by the project. Run affected feature combinations when changing flags.
- Read README for workers/background jobs; use durable jobs for suitable
  retryable external effects, not to bypass synchronous authentication checks.
- Preserve `.shiprust.toml` and customer edits. There is no automatic in-place
  upgrade endpoint. Compare a separately downloaded revision and port selected
  changes through reviewed diffs/migrations.

## Deploy

Read the generated hosting overlay/README. `host: caprover` includes deployment
assets; `host: none` does not provision a host. Build the Docker image from the
project, provision Postgres with durable storage/backups, set SITE_URL to the
actual HTTPS origin, and configure the selected services independently.

Keep runtime credentials in the deployment platform's secret mechanism, not
images, source or workflow literals. For CapRover use the CLI/API, preserve the
existing app definition and operator settings, and verify the target instance.
Do not create billable infrastructure, change production DNS, or deploy without
user authorization. Once authorized: run the project checks, back up before DB
migrations, deploy, verify health/exact revision and signup/billing paths as
applicable. Have a rollback plan compatible with already-applied migrations;
never casually downgrade a binary across schema changes.

Official product guides:
- https://shiprust.com/docs/downloading-your-codebase
- https://shiprust.com/docs/caprover
- https://shiprust.com/docs/docker
