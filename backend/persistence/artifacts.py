"""Provider-neutral artifact persistence backed by Backblaze B2 S3 API."""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import hmac
import re
from urllib.parse import quote, urlparse


class ArtifactStore:
    async def put(self, key: str, content: bytes, *, content_type: str = "application/octet-stream") -> None:
        raise NotImplementedError

    async def get(self, key: str) -> bytes | None:
        raise NotImplementedError

    async def delete(self, key: str) -> None:
        raise NotImplementedError


class B2ArtifactStore(ArtifactStore):
    """Minimal B2 S3-compatible client using AWS Signature V4."""

    def __init__(self, bucket: str, endpoint: str, key_id: str, application_key: str):
        if not bucket or not endpoint or not key_id or not application_key:
            raise ValueError("B2 bucket, endpoint, key id, and application key are required")
        parsed = urlparse(endpoint.rstrip("/"))
        if parsed.scheme != "https" or not parsed.netloc:
            raise ValueError("B2 endpoint must be an HTTPS URL")
        self.bucket = bucket
        self.endpoint = endpoint.rstrip("/")
        self.host = parsed.netloc
        match = re.match(r"^s3\.([^.]+)\.backblazeb2\.com$", self.host)
        if not match:
            raise ValueError("B2 endpoint must look like https://s3.<region>.backblazeb2.com")
        self.region = match.group(1)
        self.key_id = key_id
        self.application_key = application_key

    def _url(self, key: str) -> str:
        if not key or key.startswith("/"):
            raise ValueError("artifact key must be a non-empty relative path")
        return f"{self.endpoint}/{quote(self.bucket, safe='')}/{quote(key, safe='/~.-_')}"

    @staticmethod
    def _hmac(key: bytes, value: str) -> bytes:
        return hmac.new(key, value.encode(), hashlib.sha256).digest()

    def _authorization(self, method: str, uri: str, payload: bytes, now: datetime, content_type: str | None):
        amz_date = now.strftime("%Y%m%dT%H%M%SZ")
        date = now.strftime("%Y%m%d")
        payload_hash = hashlib.sha256(payload).hexdigest()
        headers = {
            "host": self.host,
            "x-amz-content-sha256": payload_hash,
            "x-amz-date": amz_date,
        }
        if content_type:
            headers["content-type"] = content_type
        canonical_headers = "".join(f"{name}:{headers[name].strip()}\n" for name in sorted(headers))
        signed_headers = ";".join(sorted(headers))
        parsed = urlparse(uri)
        canonical_request = "\n".join([
            method,
            parsed.path or "/",
            parsed.query,
            canonical_headers,
            signed_headers,
            payload_hash,
        ])
        credential_scope = f"{date}/{self.region}/s3/aws4_request"
        string_to_sign = "\n".join([
            "AWS4-HMAC-SHA256",
            amz_date,
            credential_scope,
            hashlib.sha256(canonical_request.encode()).hexdigest(),
        ])
        date_key = self._hmac(("AWS4" + self.application_key).encode(), date)
        region_key = self._hmac(date_key, self.region)
        service_key = self._hmac(region_key, "s3")
        signing_key = self._hmac(service_key, "aws4_request")
        signature = hmac.new(signing_key, string_to_sign.encode(), hashlib.sha256).hexdigest()
        authorization = (
            "AWS4-HMAC-SHA256 "
            f"Credential={self.key_id}/{credential_scope}, "
            f"SignedHeaders={signed_headers}, Signature={signature}"
        )
        return headers, authorization

    @staticmethod
    def _workers_fetch():
        """Load the Cloudflare runtime adapter only inside an actual Worker."""
        try:
            from workers import fetch
        except ImportError as exc:
            raise RuntimeError("Cloudflare Workers runtime is required for artifact persistence") from exc
        return fetch

    async def _request(self, method: str, key: str, body: bytes = b"", content_type: str | None = None):
        url = self._url(key)
        headers, authorization = self._authorization(method, url, body, datetime.now(timezone.utc), content_type)
        headers["authorization"] = authorization
        fetch = self._workers_fetch()
        response = await fetch(url, method=method, headers=headers, body=body if method == "PUT" else None)
        return response

    async def put(self, key: str, content: bytes, *, content_type: str = "application/octet-stream") -> None:
        response = await self._request("PUT", key, content, content_type)
        if not (200 <= response.status < 300):
            detail = await response.text()
            raise RuntimeError(f"B2 PUT failed ({response.status}): {detail[:500]}")

    async def get(self, key: str) -> bytes | None:
        response = await self._request("GET", key)
        if response.status == 404:
            return None
        if not (200 <= response.status < 300):
            detail = await response.text()
            raise RuntimeError(f"B2 GET failed ({response.status}): {detail[:500]}")
        return bytes(await response.arrayBuffer())

    async def delete(self, key: str) -> None:
        response = await self._request("DELETE", key)
        if not (200 <= response.status < 300):
            detail = await response.text()
            raise RuntimeError(f"B2 DELETE failed ({response.status}): {detail[:500]}")


def artifact_store_from_env(env) -> B2ArtifactStore:
    return B2ArtifactStore(
        bucket=getattr(env, "B2_BUCKET", ""),
        endpoint=getattr(env, "B2_ENDPOINT", ""),
        key_id=getattr(env, "B2_KEY_ID", ""),
        application_key=getattr(env, "B2_APPLICATION_KEY", ""),
    )
