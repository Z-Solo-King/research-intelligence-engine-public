"""Small, deterministic normalizers for already-observed values."""
from __future__ import annotations

from collections.abc import Mapping
import re

_STOCK_RULES = (
    (("instock", "in stock", "available", "/instock", "in-stock", "in_stock", "add to cart", "add-to-cart", "addtocart"), "In Stock"),
    (("outofstock", "out of stock", "sold out", "/outofstock", "out-of-stock", "unavailable", "out_of_stock"), "Out of Stock"),
    (("preorder", "pre-order", "pre book", "pre-book"), "Pre-Book"),
    (("limited", "partially out of stock", "partially_out_of_stock"), "Limited"),
    (("discontinued",), "Discontinued"),
)


def normalize_specs(value: object) -> Mapping[str, object]:
    """Normalize observed specification envelopes without inventing values."""
    if isinstance(value, Mapping):
        result: dict[str, object] = {}
        for key, item in value.items():
            if isinstance(item, Mapping):
                nested = item.get("value") or item.get("text") or item.get("displayValue")
                result[str(key)] = nested if nested is not None else dict(item)
            else:
                result[str(key)] = item
        return result
    if isinstance(value, (list, tuple)):
        result = {}
        for item in value:
            if isinstance(item, Mapping):
                key = item.get("key") or item.get("name") or item.get("label")
                observed = item.get("value") or item.get("text") or item.get("displayValue")
                if key is not None and observed is not None:
                    result[str(key)] = observed
            elif isinstance(item, (list, tuple)) and len(item) >= 2:
                result[str(item[0])] = item[1]
        return result
    return {}


def _clean_text(value: object) -> str:
    return " ".join(str(value).split()) if value is not None else ""


def normalize_stock(value: object) -> str:
    """Normalize explicit availability observations to a stable label."""
    if value is None:
        return "Unknown"
    if isinstance(value, bool):
        return "In Stock" if value else "Out of Stock"
    if isinstance(value, (int, float)):
        return "In Stock" if value > 0 else "Out of Stock"
    text = _clean_text(value).lower()
    text = re.sub(r"^(stock|availability|status)\s*[:=\-]\s*", "", text)
    if text.isdigit():
        return "In Stock" if int(text) > 0 else "Out of Stock"
    for needles, label in _STOCK_RULES:
        if any(needle in text for needle in needles):
            return label
    return _clean_text(value)[:80] or "Unknown"
