"""Concrete D1 and provider-neutral artifact persistence for Cloudflare Workers."""

from datetime import datetime, timezone
import hashlib
import json

from backend.persistence.artifacts import artifact_store_from_env


class IdempotencyConflictError(RuntimeError):
    """Raised when an idempotency key is reused for a different request."""


def request_fingerprint(request) -> str:
    payload = {
        "question": request.question,
        "depth": request.depth or "standard",
        "require_citations": bool(request.require_citations),
        "max_sources": request.max_sources,
        "max_evidence_items": request.max_evidence_items,
        "strict_zero_cost_only": bool(request.strict_zero_cost_only),
        "source_urls": list(request.source_urls),
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(encoded.encode()).hexdigest()


class CloudflarePersistence:
    def __init__(self, env):
        self.env = env
        self.artifacts = artifact_store_from_env(env)

    async def create_run(self, run_id, request):
        now = datetime.now(timezone.utc).isoformat()
        await self.env.DB.prepare(
            """INSERT INTO research_runs
            (run_id, question, depth, require_citations, max_sources,
             max_evidence_items, strict_zero_cost_only, status, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
        ).bind(
            run_id, request.question, request.depth or "standard",
            int(request.require_citations), request.max_sources,
            request.max_evidence_items, int(request.strict_zero_cost_only),
            "planned", now, now,
        ).run()
        return run_id

    async def create_run_idempotent(self, request, idempotency_key: str):
        """Atomically claim an idempotency key and create its stable run."""
        if not idempotency_key or not idempotency_key.strip():
            raise ValueError("idempotency_key must not be empty")
        request_hash = request_fingerprint(request)
        run_id = f"run-{hashlib.sha256(idempotency_key.encode()).hexdigest()[:32]}"
        now = datetime.now(timezone.utc).isoformat()
        claim = self.env.DB.prepare(
            """INSERT INTO idempotency_keys(idempotency_key, run_id, request_hash, created_at)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(idempotency_key) DO NOTHING"""
        ).bind(idempotency_key, run_id, request_hash, now)
        create = self.env.DB.prepare(
            """INSERT INTO research_runs
            (run_id, question, depth, require_citations, max_sources,
             max_evidence_items, strict_zero_cost_only, status, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(run_id) DO NOTHING"""
        ).bind(
            run_id, request.question, request.depth or "standard",
            int(request.require_citations), request.max_sources,
            request.max_evidence_items, int(request.strict_zero_cost_only),
            "planned", now, now,
        )
        lookup = self.env.DB.prepare(
            "SELECT run_id, request_hash FROM idempotency_keys WHERE idempotency_key = ?"
        ).bind(idempotency_key)

        result = await self.env.DB.batch([claim, create, lookup])
        row = result[2].results[0] if result[2].results else None
        if row is None:
            raise RuntimeError("idempotency claim was not persisted")
        if row["request_hash"] != request_hash:
            raise IdempotencyConflictError("idempotency key was already used for a different request")
        return row["run_id"]

    async def get_run(self, run_id):
        return await self.env.DB.prepare(
            "SELECT * FROM research_runs WHERE run_id = ?"
        ).bind(run_id).first()

    async def set_run_status(self, run_id, status):
        if status not in {"planned", "running", "completed", "failed"}:
            raise ValueError("invalid run status")
        await self.env.DB.prepare(
            "UPDATE research_runs SET status = ?, updated_at = ? WHERE run_id = ?"
        ).bind(status, datetime.now(timezone.utc).isoformat(), run_id).run()

    async def put_artifact(self, key, content, content_type="application/octet-stream"):
        digest = hashlib.sha256(content).hexdigest()
        await self.artifacts.put(key, content, content_type=content_type)
        return {"key": key, "sha256": digest, "size": len(content)}

    async def get_artifact(self, key):
        return await self.artifacts.get(key)

    async def delete_artifact(self, key):
        await self.artifacts.delete(key)
