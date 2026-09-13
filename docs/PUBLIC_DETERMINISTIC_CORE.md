# Public deterministic core

## Purpose

This repository owns the public-safe, deterministic portion of observed-data processing that can be tested independently of credentials, private acquisition policy, provider selection, evaluation holdouts, deployment authority, or private run history.

The current package is `foundation_core/`. Its responsibilities are deliberately narrow:

- canonical field alias routing
- observed specification normalization
- availability normalization
- deterministic plausibility signals
- stable mapping of an already-observed product record

The package performs no network access, credential handling, provider selection, challenge solving, proxy rotation, or private policy enforcement.

## Source of truth

`foundation_core/` is the canonical implementation for the deterministic functions listed above.

Operations retains compatibility import paths where necessary so the private runtime can transition without an API break. Compatibility modules must not fork or reimplement the public logic.

The private repository remains authoritative for acquisition, extraction strategy, platform adapters, execution planning, validation policy, replay controls, chatbot orchestration, resource controls, evaluation, promotion, and deployment.

## Package contract

Operations consumes an explicitly pinned Foundation commit through `scripts/sync_public_core.py`. The deployment path materializes that exact revision into an ignored generated package; Operations does not depend on a floating branch and does not use a Git URL dependency in Worker metadata.

The public package exposes only deterministic data functions. It treats input as observed data and must never invent a missing fact.

## Tests and coverage

Public CI compiles the complete public tree, installs the package, runs the full Foundation test suite with branch coverage, and enforces 100% coverage across the unit-testable product surface in `backend`, `foundation_core`, and `worker`.

The Cloudflare Worker-only `backend/persistence/artifacts.py` transport adapter is intentionally excluded from the unit coverage denominator because its network implementation is bound to the Cloudflare Workers runtime; the test suite still exercises the persistence interface and response-shape normalization around it. Runtime deployment/smoke validation remains the authoritative integration check for that adapter.

The public suite also checks:

- normalization branches and malformed inputs
- alias precedence and stable routing order
- deterministic product mapping
- provenance preservation
- plausibility signal boundaries
- package importability after installation
- absence of private control-plane references
- absence of credential material and protected directories

The 100% gate is a test-quality requirement, not a claim that every private runtime path is executed in public CI.

## Public/private boundary

Safe to publish:

- pure transformations over explicitly supplied values
- stable public data shapes
- deterministic parsing/normalization behavior
- generic quality signals that do not encode private decision authority
- tests containing synthetic or already-public-safe data

Keep private:

- network acquisition and source recovery
- provider/platform adapters
- credentials and endpoints that are not public contracts
- access-control handling and challenge bypass logic
- resource ledgers and quota authority
- trust-boundary policy
- private evaluation and holdouts
- promotion/canary/rollback authority
- private chatbot execution strategy and run records
- deployment secrets and operational authority

## Naming and organization

Public files use ordinary descriptive engineering names such as `field_routing.py`, `normalization.py`, `quality.py`, and `product_mapping.py`. The structure is intentionally straightforward and reviewable. It must not use deceptive names, misleading metadata, obfuscated code, or hidden functionality.

The goal is low cognitive overhead and clean separation of responsibilities, not concealment.
