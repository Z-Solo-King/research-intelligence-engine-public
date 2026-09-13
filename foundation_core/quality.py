"""Deterministic plausibility checks over observed product facts."""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
import re

from .field_routing import route_field
from .normalization import normalize_specs


@dataclass(frozen=True)
class PlausibilitySignal:
    code: str
    severity: str
    field: str
    message: str
    action: str = "cross_check"


_NUM = re.compile(r"\d+(?:\.\d+)?")


def _num(value: object) -> float | None:
    match = _NUM.search(str(value or ""))
    return float(match.group(0)) if match else None


def evaluate_price_spec_plausibility(raw: Mapping[str, object]) -> tuple[PlausibilitySignal, ...]:
    """Return explainable cross-check signals without changing observed values."""
    price = _num(raw.get("price"))
    if price is None:
        routed_price = route_field(raw, "price")
        price = _num(routed_price.value) if routed_price is not None else None
    if price is None:
        return ()

    specs = normalize_specs(raw.get("specs"))
    category_field = route_field(raw, "category")
    title_field = route_field(raw, "title")
    category = " ".join(
        str(value or "").lower()
        for value in (
            category_field.value if category_field is not None else None,
            raw.get("product_type"),
            title_field.value if title_field is not None else None,
        )
    )
    signals: list[PlausibilitySignal] = []
    panel = str(specs.get("panel") or specs.get("panel_type") or "").lower()
    refresh = _num(specs.get("refresh_rate") or specs.get("hz"))
    size = _num(specs.get("screen_size") or specs.get("display_size"))
    if ("monitor" in category or "display" in category) and "oled" in panel and price < 10000:
        signals.append(PlausibilitySignal("budget_oled_monitor", "high", "panel", "Unusually low OLED monitor price; verify exact model and panel."))
    if ("monitor" in category or "display" in category) and refresh is not None and size is not None and price < 25000 and refresh >= 500 and size >= 27:
        signals.append(PlausibilitySignal("extreme_refresh_price_combo", "medium", "refresh_rate", "Unusual high-refresh/price combination; verify model identity."))
    return tuple(signals)
