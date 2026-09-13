"""Deterministic routing of observed aliases into canonical fields."""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass


@dataclass(frozen=True)
class RoutedField:
    """One observed value routed to a canonical field."""

    family: str
    canonical: str
    value: object
    source: str


FIELD_ALIASES: dict[str, tuple[str, ...]] = {
    "title": ("title", "name"),
    "sku": ("sku", "productCode"),
    "mpn": ("mpn", "manufacturerPartNumber"),
    "gtin": ("gtin", "gtin13", "gtin14", "ean", "upc"),
    "brand": ("brand", "manufacturer"),
    "category": ("category", "categoryName"),
    "description": ("description", "summary", "shortDescription"),
    "variant_id": ("variant_id", "variantId", "id"),
    "price": ("price", "salePrice", "currentPrice", "amount"),
    "availability": ("availability", "stock", "stockStatus"),
    "url": ("url", "link", "productUrl", "productPageUrl"),
    "images": ("images", "image", "imageUrl", "thumbnail"),
}

FIELD_FAMILIES: dict[str, str] = {
    "title": "identity",
    "sku": "identity",
    "mpn": "identity",
    "gtin": "identity",
    "brand": "identity",
    "category": "taxonomy",
    "description": "descriptive",
    "variant_id": "variant",
    "price": "commercial",
    "availability": "commercial",
    "url": "navigation",
    "images": "media",
}


def route_field(raw: Mapping[str, object], canonical: str) -> RoutedField | None:
    """Resolve the first explicit non-empty alias for one canonical field."""
    aliases = FIELD_ALIASES.get(canonical)
    if aliases is None:
        raise KeyError(f"unknown canonical field: {canonical}")
    family = FIELD_FAMILIES[canonical]
    for source in aliases:
        value = raw.get(source)
        if value is None or value == "" or value == () or value == []:
            continue
        return RoutedField(family, canonical, value, source)
    return None


def route_fields(raw: Mapping[str, object]) -> tuple[RoutedField, ...]:
    """Route all supported canonical fields in stable declaration order."""
    return tuple(field for canonical in FIELD_ALIASES if (field := route_field(raw, canonical)) is not None)
