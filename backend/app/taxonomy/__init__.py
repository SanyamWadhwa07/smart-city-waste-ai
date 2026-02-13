"""Taxonomy mappings for waste classification system."""

from .mappings import (
    DETECTOR_TO_MATERIAL,
    MATERIAL_TO_BIN,
    BIN_TO_ROUTE,
    MANUAL_REVIEW_ROUTE,
    get_material_from_detector,
    get_bin_from_material,
    get_route_from_bin,
    get_final_route,
    load_custom_mappings,
)

__all__ = [
    "DETECTOR_TO_MATERIAL",
    "MATERIAL_TO_BIN",
    "BIN_TO_ROUTE",
    "MANUAL_REVIEW_ROUTE",
    "get_material_from_detector",
    "get_bin_from_material",
    "get_route_from_bin",
    "get_final_route",
    "load_custom_mappings",
]
