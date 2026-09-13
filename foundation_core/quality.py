"""Deterministic plausibility checks over observed product facts."""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
import re


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
        return ()
    specs = raw.get("specs") if isinstance(raw.get("specs"), Mapping) else {}
    category = " ".join(str(raw.get(key) or "").lower() for key in ("category", "product_type", "title"))
    signals: list[PlausibilitySignal] = []
    panel = str(specs.get("panel") or specs.get("panel_type") or "").lower()
    refresh = _num(specs.get("refresh_rate") or specs.get("hz"))
    size = _num(specs.get("screen_size") or specs.get("display_size"))
    if ("monitor" in category or "display" in category) and "oled" in panel and price < 10000:
        signals.append(PlausibilitySignal("budget_oled_monitor", "high", "panel", "Unusually low OLED monitor price; verify exact model and panel."))
    if ("monitor" in category or "display" in category) and refresh is not None and size is not None and price < 25000 and refresh >= 500 and size >= 27:
        signals.append(PlausibilitySignal("extreme_refresh_price_combo", "medium", "refresh_rate", "Unusual high-refresh/price combination; verify model identity."))
    return tuple(signals)
