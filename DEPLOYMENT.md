# Deployment

This repository contains the public contract/Worker boundary. Production control-plane deployment details are intentionally kept outside the public repository.

## Runtime architecture

The public Worker uses:

- Cloudflare D1 for canonical graph/run metadata.
- Backblaze B2 S3-compatible object storage for artifacts.
- A Cloudflare Service Binding to the private control-plane Worker for readiness/control-plane calls.

No B2 credentials, authentication tokens, private service names, or private database identifiers belong in Git.

## Required deployment inputs

Supply these through the Cloudflare deployment environment rather than committing them:

- `AUTH_TOKEN`
- `B2_KEY_ID`
- `B2_APPLICATION_KEY`
- the production D1 database binding
- the Service Binding from `CONTROL_PLANE` to the private control-plane Worker

The public Wrangler configuration intentionally keeps the D1 database name/id and private service name as placeholders.

The non-secret B2 configuration is fixed to the zero-cost deployment target:

- bucket: `SoloKing`
- endpoint: `https://s3.eu-central-003.backblazeb2.com`

## Deployment order

Deploy the private control-plane Worker first, then deploy the public Worker. The public Worker should use the Service Binding rather than a normal HTTPS fetch to the private Worker. Cloudflare documents Service Bindings as the supported Worker-to-Worker mechanism. 

Smoke-test `/health` first. Test `/readiness` only after the Service Binding is configured, because readiness includes the control-plane health check.
