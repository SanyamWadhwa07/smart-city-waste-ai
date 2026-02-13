"""
Configurable taxonomy mappings for waste classification.

This module provides bidirectional mappings between:
- Detector labels (from BowerApp YOLO) → Material categories
- Material categories → Bin types
- Bin types → Backend route names

Mappings can be customized via JSON config files or environment variables.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Dict, Optional

# ============================================================================
# DETECTOR LABEL → MATERIAL CATEGORY MAPPING
# ============================================================================
# Maps raw detector output labels to normalized material categories
# Based on turhancan97/yolov8-segment-trash-detection output classes
# Classes: Glass, Metal, Paper, Plastic, Waste

DETECTOR_TO_MATERIAL: Dict[str, str] = {
    # Direct mappings from segmentation model
    "Glass": "glass",
    "glass": "glass",
    "Metal": "metal",
    "metal": "metal",
    "Paper": "paper",
    "paper": "paper",
    "Plastic": "plastic",
    "plastic": "plastic",
    "Waste": "landfill",
    "waste": "landfill",
    
    # Additional mappings for compatibility (lowercase variants)
    "bottle": "plastic",
    "plastic_bottle": "plastic",
    "plastic_bag": "plastic",
    "plastic_container": "plastic",
    "plastic_cup": "plastic",
    "plastic_lid": "plastic",
    "cup": "plastic",
    "straw": "plastic",
    "wrapper": "plastic",
    
    "newspaper": "paper",
    "magazine": "paper",
    "cardboard": "paper",
    "carton": "paper",
    "paper_bag": "paper",
    "tissue": "paper",
    "paper_cup": "paper",
    
    "can": "metal",
    "metal_can": "metal",
    "aluminum_can": "metal",
    "tin_can": "metal",
    "foil": "metal",
    "metal_lid": "metal",
    
    "jar": "glass",
    "glass_bottle": "glass",
    "glass_jar": "glass",
    
    "food": "organic",
    "food_waste": "organic",
    "food_scrap": "organic",
    "fruit": "organic",
    "vegetable": "organic",
    "organic": "organic",
    "biological": "organic",
    
    "battery": "hazardous",
    "electronics": "hazardous",
    "lightbulb": "hazardous",
    
    "clothes": "textile",
    "fabric": "textile",
    "shoes": "textile",
    
    "trash": "landfill",
    "other": "landfill",
}

# ============================================================================
# MATERIAL CATEGORY → BIN TYPE MAPPING
# ============================================================================
# Maps material categories to user-friendly bin colors/types

MATERIAL_TO_BIN: Dict[str, str] = {
    "plastic": "BLUE_BIN",
    "paper": "GREEN_BIN",
    "metal": "YELLOW_BIN",
    "glass": "WHITE_BIN",
    "organic": "BROWN_BIN",
    "hazardous": "RED_BIN",
    "textile": "PURPLE_BIN",
    "landfill": "GRAY_BIN",
}

# ============================================================================
# BIN TYPE → BACKEND ROUTE MAPPING
# ============================================================================
# Maps user-friendly bin names to backend route identifiers
# These route names match the existing Decision schema validation

BIN_TO_ROUTE: Dict[str, str] = {
    "BLUE_BIN": "PLASTIC_BIN",
    "GREEN_BIN": "PAPER_BIN",
    "YELLOW_BIN": "METAL_BIN",
    "WHITE_BIN": "GLASS_BIN",
    "BROWN_BIN": "ORGANIC",
    "RED_BIN": "HAZARDOUS",
    "PURPLE_BIN": "LANDFILL",  # Textiles default to landfill
    "GRAY_BIN": "LANDFILL",
}

# Special route for uncertain/low-confidence detections
MANUAL_REVIEW_ROUTE = "MANUAL_REVIEW"

# ============================================================================
# REVERSE MAPPINGS (for validation and lookups)
# ============================================================================

def _build_reverse_mapping(forward: Dict[str, str]) -> Dict[str, list[str]]:
    """Build reverse mapping (many-to-one becomes one-to-many)."""
    reverse = {}
    for key, value in forward.items():
        if value not in reverse:
            reverse[value] = []
        reverse[value].append(key)
    return reverse

MATERIAL_TO_DETECTORS = _build_reverse_mapping(DETECTOR_TO_MATERIAL)
BIN_TO_MATERIALS = _build_reverse_mapping(MATERIAL_TO_BIN)
ROUTE_TO_BINS = _build_reverse_mapping(BIN_TO_ROUTE)

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_material_from_detector(detector_label: str) -> str:
    """
    Convert detector label to material category.
    
    Args:
        detector_label: Raw label from detector (e.g., "bottle", "can")
        
    Returns:
        Material category (e.g., "plastic", "metal")
        Returns "landfill" if label not found.
    """
    normalized = detector_label.lower().strip()
    return DETECTOR_TO_MATERIAL.get(normalized, "landfill")


def get_bin_from_material(material: str) -> str:
    """
    Convert material category to bin recommendation.
    
    Args:
        material: Material category (e.g., "plastic", "metal")
        
    Returns:
        Bin type (e.g., "BLUE_BIN", "YELLOW_BIN")
        Returns "GRAY_BIN" if material not found.
    """
    normalized = material.lower().strip()
    return MATERIAL_TO_BIN.get(normalized, "GRAY_BIN")


def get_route_from_bin(bin_type: str) -> str:
    """
    Convert bin type to backend route name.
    
    Args:
        bin_type: Bin identifier (e.g., "BLUE_BIN", "GREEN_BIN")
        
    Returns:
        Route name (e.g., "PLASTIC_BIN", "PAPER_BIN")
        Returns "LANDFILL" if bin not found.
    """
    normalized = bin_type.upper().strip()
    return BIN_TO_ROUTE.get(normalized, "LANDFILL")


def get_final_route(
    material: str,
    uncertain: bool = False,
    contaminated: bool = False
) -> tuple[str, str]:
    """
    Get final route and bin recommendation from material, with override logic.
    
    Args:
        material: Material category
        uncertain: Whether detection is uncertain
        contaminated: Whether contamination is detected
        
    Returns:
        Tuple of (route_name, bin_type)
        
    Examples:
        >>> get_final_route("plastic")
        ("PLASTIC_BIN", "BLUE_BIN")
        
        >>> get_final_route("plastic", uncertain=True)
        ("MANUAL_REVIEW", "MANUAL_REVIEW")
    """
    # Override: uncertain or contaminated items go to manual review
    if uncertain or contaminated:
        return (MANUAL_REVIEW_ROUTE, "MANUAL_REVIEW")
    
    # Normal flow: material → bin → route
    bin_type = get_bin_from_material(material)
    route = get_route_from_bin(bin_type)
    
    return (route, bin_type)


def load_custom_mappings(config_path: Optional[str] = None) -> bool:
    """
    Load custom mappings from JSON config file.
    
    Allows runtime customization of taxonomy without code changes.
    
    Args:
        config_path: Path to JSON config file. If None, looks for
                    TAXONOMY_CONFIG_PATH environment variable or
                    "taxonomy_config.json" in current directory.
                    
    Returns:
        True if custom mappings loaded successfully, False otherwise.
        
    Expected JSON format:
        {
            "detector_to_material": {"new_label": "material"},
            "material_to_bin": {"new_material": "BIN_TYPE"},
            "bin_to_route": {"NEW_BIN": "ROUTE_NAME"}
        }
    """
    global DETECTOR_TO_MATERIAL, MATERIAL_TO_BIN, BIN_TO_ROUTE
    
    if config_path is None:
        config_path = os.getenv("TAXONOMY_CONFIG_PATH", "taxonomy_config.json")
    
    config_file = Path(config_path)
    if not config_file.exists():
        return False
    
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        # Update mappings (merge with defaults)
        if "detector_to_material" in config:
            DETECTOR_TO_MATERIAL.update(config["detector_to_material"])
        
        if "material_to_bin" in config:
            MATERIAL_TO_BIN.update(config["material_to_bin"])
        
        if "bin_to_route" in config:
            BIN_TO_ROUTE.update(config["bin_to_route"])
        
        # Rebuild reverse mappings
        global MATERIAL_TO_DETECTORS, BIN_TO_MATERIALS, ROUTE_TO_BINS
        MATERIAL_TO_DETECTORS = _build_reverse_mapping(DETECTOR_TO_MATERIAL)
        BIN_TO_MATERIALS = _build_reverse_mapping(MATERIAL_TO_BIN)
        ROUTE_TO_BINS = _build_reverse_mapping(BIN_TO_ROUTE)
        
        return True
        
    except Exception as e:
        # Silently fail - use defaults
        return False


# ============================================================================
# VALIDATION HELPERS
# ============================================================================

def is_valid_detector_label(label: str) -> bool:
    """Check if detector label is recognized."""
    return label.lower().strip() in DETECTOR_TO_MATERIAL


def is_valid_material(material: str) -> bool:
    """Check if material category is recognized."""
    return material.lower().strip() in MATERIAL_TO_BIN


def is_valid_bin(bin_type: str) -> bool:
    """Check if bin type is recognized."""
    return bin_type.upper().strip() in BIN_TO_ROUTE


def get_all_detector_labels() -> list[str]:
    """Get list of all recognized detector labels."""
    return sorted(DETECTOR_TO_MATERIAL.keys())


def get_all_materials() -> list[str]:
    """Get list of all material categories."""
    return sorted(set(DETECTOR_TO_MATERIAL.values()))


def get_all_bins() -> list[str]:
    """Get list of all bin types."""
    return sorted(MATERIAL_TO_BIN.values())


def get_all_routes() -> list[str]:
    """Get list of all route names."""
    return sorted(set(BIN_TO_ROUTE.values()))


# ============================================================================
# COMPATIBILITY WITH EXISTING TIER2_TO_TIER1_MAPPING
# ============================================================================
# For backward compatibility with existing dual_agent.py

def get_legacy_tier1_material(tier2_label: str) -> str:
    """
    Convert Tier-2 classifier label to legacy Tier-1 material category.
    
    Maps fine-grained classifier output to 6-class detector categories
    used by existing dual_agent.py logic.
    
    Returns one of: BIODEGRADABLE, CARDBOARD, GLASS, METAL, PAPER, PLASTIC
    """
    # Map to material first
    material = get_material_from_detector(tier2_label)
    
    # Map material to legacy tier-1 categories
    legacy_mapping = {
        "plastic": "PLASTIC",
        "paper": "PAPER",
        "metal": "METAL",
        "glass": "GLASS",
        "organic": "BIODEGRADABLE",
        "hazardous": "METAL",  # Default hazardous to metal bin
        "textile": "BIODEGRADABLE",  # Default textiles to biodegradable
        "landfill": "PLASTIC",  # Default unknown to plastic (most common)
    }
    
    return legacy_mapping.get(material, "PLASTIC")
