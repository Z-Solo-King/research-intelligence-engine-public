# Foundation

Public contract core for the Z-Solo-King GitHub family.

This repository contains public-safe contracts, schemas, reusable deterministic primitives, and the public CI evidence path. Protected execution, governance, evaluation holdouts, credentials, and promotion authority live outside this public repository.

## Documentation first

`docs/DOCUMENTATION_INDEX.md` is the canonical navigation contract for humans and AI agents working on Foundation. Start there when entering an unfamiliar session.

The recommended order is:

1. `README.md`
2. `AI_CODEMAP.json`
3. `docs/DOCUMENTATION_INDEX.md`
4. `docs/FAMILY_CONTRACT.json`
5. `docs/FAMILY_ARCHITECTURE.md`
6. `docs/PUBLIC_DETERMINISTIC_CORE.md`
7. the relevant subsystem/workflow documentation

## Public deterministic core

`foundation_core/` is the canonical public implementation for deterministic observed-data routing, normalization, plausibility checks, and product mapping. See `docs/PUBLIC_DETERMINISTIC_CORE.md` for the exact boundary and maintenance rules.

The private Operations repository consumes this package at a pinned public revision. Private compatibility imports may remain temporarily, but public code is the source of truth and must not be forked privately.

## AI / human navigation

`AI_CODEMAP.json` is the compact machine-readable map of ownership, canonical modules, boundaries, and change methodology. Read it before scanning the repository broadly.

## Family documentation

`docs/FAMILY_CONTRACT.json` and `docs/FAMILY_ARCHITECTURE.md` define repository ownership and dependency direction.

`docs/RUN_RECORD_PUBLIC_BOUNDARY.md` defines which run/execution/evidence metadata may cross into the public-safe contract layer. Foundation does not own private chatbot run history.

## CI principle

Foundation owns the public, deterministic test surface and enforces complete branch coverage for its product code. Operations does not depend on GitHub-hosted private CI for routine validation; protected checks are executed through non-GitHub-hosted paths when required.
