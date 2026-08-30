"""Helpers used by the GridX integration."""

from typing import Any, Dict

WATT_SECONDS_PER_WATT_HOUR = 3600


def extract_nested_value(data: Dict[str, Any], key_path: str) -> Any:
    """
    Extract value from nested dictionary using dot notation.
    Supports list indices (e.g., "foo.0.bar").
    
    Args:
        data: Dictionary to extract from
        key_path: Dot-separated path (e.g., "power.ac.total")
        
    Returns:
        Extracted value or None if path not found
    """
    if not data or not key_path:
        return None
        
    keys = key_path.split(".")
    value = data
    
    for key in keys:
        if isinstance(value, dict):
            value = value.get(key)
        elif isinstance(value, list) and key.isdigit():
            idx = int(key)
            if 0 <= idx < len(value):
                value = value[idx]
            else:
                return None
        else:
            return None
            
    return value


def normalize_sensor_value(key_path: str, value: Any) -> Any:
    """Normalize raw gridX values to the unit exposed by Home Assistant."""
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        return value

    normalized_key = key_path.lower().replace("_", "")

    # The gridX API documents all *MeterReading* fields in watt-seconds (Ws).
    # Home Assistant exposes these cumulative energy readings in watt-hours.
    if "meterreading" in normalized_key:
        return value / WATT_SECONDS_PER_WATT_HOUR

    # Rate fields have historically been returned as either 0..1 or 0..100.
    if normalized_key.endswith("rate") and 0.0 <= value <= 1.0:
        return value * 100

    return value
