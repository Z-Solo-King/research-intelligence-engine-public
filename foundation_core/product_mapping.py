"""Deterministic mapping of observed product records into a stable shape."""
from __future__ import annotations

from collections.abc import Mapping

from .field_routing import route_field
from .normalization import normalize_specs, normalize_stock
from .quality import evaluate_price_spec_plausibility


def _text(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _brand(value: object) -> str | None:
    if isinstance(value, Mapping):
        return _text(value.get("name") or value.get("brand"))
    return _text(value)


def _identifier(value: object, *, numeric: bool = False) -> str | None:
    text = _text(value)
    if text is None:
        return None
    if numeric:
        text = "".join(ch for ch in text if ch.isdigit())
    return text or None


def _images(value: object) -> tuple[str, ...]:
    if isinstance(value, Mapping):
        value = value.get("url") or value.get("src") or value.get("contentUrl")
    if isinstance(value, str):
        return (value,) if value else ()
    if isinstance(value, (list, tuple)):
        result: list[str] = []
        for item in value:
            if isinstance(item, Mapping):
                item = item.get("url") or item.get("src") or item.get("contentUrl")
            text = _text(item)
            if text:
                result.append(text)
        return tuple(result)
    return ()


def _routed(raw: Mapping[str, object], canonical: str) -> object:
    routed = route_field(raw, canonical)
    return routed.value if routed is not None else None


def _image_provenance(raw: Mapping[str, object], images: tuple[str, ...]) -> tuple[dict[str, object], ...]:
    source = raw.get("source")
    source_field = "images"
    source_url = None
    if isinstance(source, Mapping):
        if source.get("image") not in (None, "", (), []):
            source_field = "image"
        elif source.get("images") not in (None, "", (), []):
            source_field = "images"
        source_url = _text(source.get("source_url") or source.get("url"))
    return tuple(
        {"url": image, "source": "observed", "source_field": source_field, "source_url": source_url, "index": index}
        for index, image in enumerate(images)
    )


def _plausibility(raw: Mapping[str, object]) -> tuple[dict[str, object], ...]:
    return tuple(
        {"code": signal.code, "severity": signal.severity, "field": signal.field, "message": signal.message, "action": signal.action}
        for signal in evaluate_price_spec_plausibility(raw)
    )


def map_product(raw: Mapping[str, object]) -> dict[str, object]:
    """Map one observed record without fetching data or inventing facts."""
    offers = raw.get("offers")
    offer = offers if isinstance(offers, Mapping) else {}
    availability = _routed(raw, "availability") or offer.get("availability")
    images = _images(_routed(raw, "images"))
    return {
        "title": _text(_routed(raw, "title")),
        "sku": _identifier(_routed(raw, "sku")),
        "mpn": _identifier(_routed(raw, "mpn")),
        "gtin": _identifier(_routed(raw, "gtin"), numeric=True),
        "brand": _brand(_routed(raw, "brand")),
        "category": _text(_routed(raw, "category")),
        "description": _text(_routed(raw, "description")),
        "specs": normalize_specs(raw.get("specs")),
        "variant_id": _identifier(_routed(raw, "variant_id")),
        "price": _text(_routed(raw, "price") or offer.get("price") or offer.get("lowPrice")),
        "stock": normalize_stock(availability),
        "url": _text(_routed(raw, "url")),
        "images": images,
        "image_provenance": _image_provenance(raw, images),
        "plausibility": _plausibility(raw),
    }
