"""Helpers used by the GridX integration."""

from typing import Any, Dict


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
