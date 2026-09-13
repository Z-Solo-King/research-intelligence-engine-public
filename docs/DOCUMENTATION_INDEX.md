# Foundation Documentation Index

Status: **current on 2026-09-13**  
Role: public-safe contract, evidence and deterministic-core repository

## Read-first order

1. `README.md` — public purpose and boundary.
2. `AI_CODEMAP.json` — machine-readable ownership and canonical modules.
3. `docs/DOCUMENTATION_INDEX.md` — this navigation contract.
4. `docs/FAMILY_CONTRACT.json` — machine-readable family boundary.
5. `docs/FAMILY_ARCHITECTURE.md` — dependency direction and repository ownership.
6. `docs/PUBLIC_DETERMINISTIC_CORE.md` — exact public-safe implementation boundary.
7. `docs/RUN_RECORD_PUBLIC_BOUNDARY.md` — metadata that may cross into the public layer.
8. `DEPLOYMENT.md` and workflow definitions — current public runtime/CI operation.

## Canonical responsibilities

Foundation owns:

- public-safe contracts and schemas;
- deterministic observed-data primitives;
- public evidence structures and verification-safe representations;
- public API/Worker boundary code;
- public CI evidence for safe deterministic code.

Foundation does not own:

- private acquisition policy;
- provider credentials;
- protected resource/quota authority;
- private chatbot orchestration;
- private evaluation holdouts;
- promotion/rollback authority;
- private deployment control.

## Main documentation groups

### Architecture

- `docs/FAMILY_CONTRACT.json`
- `docs/FAMILY_ARCHITECTURE.md`
- `docs/FAMILY_MEMBER.md`
- `docs/FAMILY_CHANGE_METHODOLOGY.md`
- `docs/ARCHITECTURE_METHODS_2026-09-12.md`
- `docs/ARCHITECTURE_PATTERNS.md`

### Deterministic core

- `docs/PUBLIC_DETERMINISTIC_CORE.md`
- `docs/EVIDENCE_SELECTION_AND_CONTEXT_DENSITY.md`
- `foundation_core/`

### Public evidence/run boundary

- `docs/RUN_RECORD_PUBLIC_BOUNDARY.md`
- `docs/contracts/`

### Repository/security controls

- `docs/REPO_CONTROL_PATTERNS.md`
- `.github/copilot-instructions.md`
- `.github/workflows/`

## Relationship with Operations

The active family has two repositories:

```text
Foundation (public-safe contracts/deterministic core)
                 ↓
Operations (private orchestration/policy/execution)
```

Operations consumes the pinned Foundation deterministic core through its synchronization process. Foundation must remain independent of Operations and must never import private code or protected policy.

## Documentation update rule

Any change that affects a public contract, schema, deterministic algorithm, public/private boundary, workflow ownership, or dependency direction must update this index or the affected canonical document in the same change set.

Public documentation must describe what is safe to expose. Private implementation details belong in Operations.

When external facts are referenced—such as GitHub Actions behavior or platform APIs—verify current first-party documentation before encoding them as policy.
