"""Public deterministic utilities for observed-data normalization and mapping."""

from .field_routing import FIELD_ALIASES, FIELD_FAMILIES, RoutedField, route_field, route_fields
from .normalization import normalize_specs, normalize_stock
from .product_mapping import map_product
from .quality import PlausibilitySignal, evaluate_price_spec_plausibility

__all__ = [
    "FIELD_ALIASES",
    "FIELD_FAMILIES",
    "PlausibilitySignal",
    "RoutedField",
    "evaluate_price_spec_plausibility",
    "map_product",
    "normalize_specs",
    "normalize_stock",
    "route_field",
    "route_fields",
]
