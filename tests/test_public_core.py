from __future__ import annotations

import pytest

from foundation_core import (
    RoutedField,
    evaluate_price_spec_plausibility,
    map_product,
    normalize_specs,
    normalize_stock,
    route_field,
    route_fields,
)


def test_route_field_uses_aliases_and_stable_metadata() -> None:
    routed = route_field({"name": "Widget", "title": ""}, "title")
    assert routed == RoutedField("identity", "title", "Widget", "name")
    assert route_field({"title": None}, "title") is None
    with pytest.raises(KeyError):
        route_field({}, "unknown")


def test_route_fields_preserves_declaration_order() -> None:
    routed = route_fields({"name": "A", "price": "10", "url": "https://example.test"})
    assert [item.canonical for item in routed] == ["title", "price", "url"]


def test_specs_normalize_mapping_and_nested_fallbacks() -> None:
    assert normalize_specs({"size": {"value": "27"}, "panel": {"text": "OLED"}, "raw": {"other": 1}}) == {
        "size": "27",
        "panel": "OLED",
        "raw": {"other": 1},
    }
    assert normalize_specs({"size": {"displayValue": "27"}}) == {"size": "27"}
    assert normalize_specs({"size": {"value": None, "text": None, "displayValue": None}}) == {
        "size": {"value": None, "text": None, "displayValue": None}
    }


def test_specs_normalize_sequences() -> None:
    value = [
        {"name": "Width", "value": 1},
        {"label": "Height", "text": 2},
        {"key": "Depth", "displayValue": 3},
        ["Weight", 4],
        ["Ignored"],
        "Ignored",
    ]
    assert normalize_specs(value) == {"Width": 1, "Height": 2, "Depth": 3, "Weight": 4}
    assert normalize_specs([{"name": "Missing"}]) == {}
    assert normalize_specs(None) == {}


def test_stock_normalization_covers_explicit_and_fallback_values() -> None:
    assert normalize_stock(None) == "Unknown"
    assert normalize_stock(True) == "In Stock"
    assert normalize_stock(False) == "Out of Stock"
    assert normalize_stock(3) == "In Stock"
    assert normalize_stock(0) == "Out of Stock"
    assert normalize_stock("status: 2") == "In Stock"
    assert normalize_stock("availability: 0") == "Out of Stock"
    assert normalize_stock("in stock") == "In Stock"
    assert normalize_stock("sold out") == "Out of Stock"
    assert normalize_stock("pre-order") == "Pre-Book"
    assert normalize_stock("limited") == "Limited"
    assert normalize_stock("discontinued") == "Discontinued"
    assert normalize_stock("  custom state  ") == "custom state"
    assert normalize_stock(" ") == "Unknown"
    assert normalize_stock("x" * 100) == "x" * 80


def test_quality_signals_cover_missing_and_matching_conditions() -> None:
    assert evaluate_price_spec_plausibility({}) == ()
    assert evaluate_price_spec_plausibility({"price": "10"}) == ()
    assert evaluate_price_spec_plausibility({"price": "9999", "category": "monitor", "specs": {"panel": "OLED"}})[0].code == "budget_oled_monitor"
    signals = evaluate_price_spec_plausibility(
        {"price": "24999", "category": "display", "specs": {"panel_type": "LCD", "hz": "500", "display_size": "27"}}
    )
    assert [signal.code for signal in signals] == ["extreme_refresh_price_combo"]
    assert evaluate_price_spec_plausibility({"price": "10", "category": "display", "specs": {"hz": "n/a", "display_size": "n/a"}}) == ()


def test_map_product_normalizes_observed_shape_without_inventing() -> None:
    raw = {
        "name": " Widget ",
        "productCode": " SKU-1 ",
        "manufacturerPartNumber": " MPN-2 ",
        "ean": "AB123-CD4",
        "manufacturer": {"name": "Brand"},
        "categoryName": "Monitor",
        "summary": " Description ",
        "specs": [{"name": "panel", "value": "OLED"}],
        "variantId": " V-1 ",
        "offers": {"lowPrice": "9999", "availability": "In Stock"},
        "productPageUrl": " https://example.test/p ",
        "image": {"src": "https://example.test/i.png"},
        "source": {"image": "one", "source_url": "https://example.test"},
    }
    mapped = map_product(raw)
    assert mapped["title"] == "Widget"
    assert mapped["sku"] == "SKU-1"
    assert mapped["mpn"] == "MPN-2"
    assert mapped["gtin"] == "1234"
    assert mapped["brand"] == "Brand"
    assert mapped["specs"] == {"panel": "OLED"}
    assert mapped["stock"] == "In Stock"
    assert mapped["images"] == ("https://example.test/i.png",)
    assert mapped["image_provenance"] == ({
        "url": "https://example.test/i.png",
        "source": "observed",
        "source_field": "image",
        "source_url": "https://example.test",
        "index": 0,
    },)
    assert mapped["plausibility"][0]["code"] == "budget_oled_monitor"


def test_map_product_handles_alternate_images_and_offer_fallbacks() -> None:
    raw = {
        "title": "X",
        "offers": {"price": "20"},
        "images": [{"url": "u1"}, {"contentUrl": "u2"}, None, "u3"],
        "source": {"images": ["u1"]},
    }
    mapped = map_product(raw)
    assert mapped["price"] == "20"
    assert mapped["images"] == ("u1", "u2", "u3")
    assert all(item["source_field"] == "images" for item in mapped["image_provenance"])


def test_map_product_handles_empty_or_non_mapping_inputs_for_optional_sections() -> None:
    mapped = map_product({"images": "", "offers": "", "source": ""})
    assert mapped["stock"] == "Unknown"
    assert mapped["title"] is None
    assert mapped["images"] == ()
    assert mapped["image_provenance"] == ()
    assert mapped["plausibility"] == ()


def test_public_package_has_no_network_dependency() -> None:
    import foundation_core
    assert foundation_core.__all__
