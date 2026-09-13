# Deployment

This repository contains the public contract/Worker boundary. Production control-plane implementation details remain in the private `operations` repository.

## Current verified production state

As of 2026-09-13, the Cloudflare production deployment has been manually verified end to end:

- private control-plane Worker deployed;
- public Worker deployed;
- public Worker URL: `https://research-intelligence-engine-public.soloking-research-intelligence.workers.dev`;
- `/health` returns HTTP 200;
- `/readiness` returns HTTP 200;
- public Worker uses a Cloudflare Service Binding to the private control plane;
- Backblaze B2 is the artifact-storage provider under the strict zero-cost target.

The public Worker was deployed with Python Worker tooling (`pywrangler`), not plain `wrangler deploy`.

## GitHub Actions status

The public deployment workflow is `.github/workflows/deploy.yml` and supports both `push` to `main` and `workflow_dispatch`.

The workflow dynamically resolves the live D1 database ID from Cloudflare instead of relying on a stale hard-coded UUID. It runs public tests, applies D1 migrations, and deploys the Python Worker.

Older failed workflow runs are historical and came from earlier deployment configuration problems. A fresh green GitHub Actions run is useful CI evidence but is not required to keep the already-verified Cloudflare deployment live.

## Runtime architecture

The public Worker uses:

- Cloudflare D1 for canonical graph/run metadata.
- Backblaze B2 S3-compatible object storage for artifacts.
- A Cloudflare Service Binding to the private control-plane Worker for readiness/control-plane calls.

No B2 credentials, authentication tokens, private service names, or private database identifiers belong in Git.

## Required deployment inputs

Supply these through the deployment environment or secret store rather than committing them:

- `AUTH_TOKEN`
- `B2_KEY_ID`
- `B2_APPLICATION_KEY`
- the production D1 database binding
- the Service Binding from `CONTROL_PLANE` to the private control-plane Worker

The public repository's committed Wrangler configuration intentionally keeps production identifiers/configuration sanitized. Production deployment generation must never commit credentials or stale resource IDs.

The non-secret B2 configuration is fixed to the zero-cost deployment target:

- bucket: `SoloKing`
- endpoint: `https://s3.eu-central-003.backblazeb2.com`

## Deployment order

Deploy the private control-plane Worker first, then deploy the public Worker. The public Worker should use the Service Binding rather than a normal HTTPS fetch to the private Worker.

Smoke-test `/health` first. Test `/readiness` only after the Service Binding is configured, because readiness includes the control-plane health check.

## Important operational lessons

- Never hard-code an obsolete D1 `database_id`; resolve or verify the current ID.
- Never deploy a generated Wrangler config containing `REPLACE_WITH_*` placeholders.
- For Python Workers use `pywrangler deploy`.
- Keep secrets out of Git and handoff documents.
- Keep the strict `$0` policy fail-closed; do not add paid fallbacks to make deployment convenient.
