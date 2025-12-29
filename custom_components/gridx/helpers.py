"""Helper functions for GridX integration calculations."""
import logging
from typing import Any, Optional, Dict
from datetime import datetime, timedelta

_LOGGER = logging.getLogger(__name__)


def calculate_self_consumption(
    production: Optional[float],
    grid_supply: Optional[float]
) -> Optional[float]:
    """
    Calculate self-consumption from production and grid supply.
    
    Self consumption = Production - Grid Supply
    
    Args:
        production: Total solar production in Wh
        grid_supply: Energy supplied to grid in Wh
        
    Returns:
        Self consumption in Wh, or None if calculation not possible
    """
    if production is None or grid_supply is None:
        return None
    try:
        return production - grid_supply
    except (TypeError, ValueError) as err:
        _LOGGER.warning("Cannot calculate self consumption: %s", err)
        return None


def calculate_self_sufficiency_rate(
    consumption: Optional[float],
    grid_consumption: Optional[float]
) -> Optional[float]:
    """
    Calculate self-sufficiency rate as percentage.
    
    Self sufficiency = ((Consumption - Grid Consumption) / Consumption) * 100
    
    Args:
        consumption: Total consumption in Wh
        grid_consumption: Energy consumed from grid in Wh
        
    Returns:
        Self sufficiency rate in %, or None if calculation not possible
    """
    if consumption is None or grid_consumption is None:
        return None
    if consumption == 0:
        return 0.0
    try:
        return ((consumption - grid_consumption) / consumption) * 100
    except (TypeError, ValueError, ZeroDivisionError) as err:
        _LOGGER.warning("Cannot calculate self sufficiency: %s", err)
        return None


def calculate_battery_efficiency(
    battery_charge: Optional[float],
    battery_discharge: Optional[float]
) -> Optional[float]:
    """
    Calculate battery efficiency as percentage.
    
    Battery efficiency = (Discharge / Charge) * 100
    
    Args:
        battery_charge: Energy charged to battery in Wh
        battery_discharge: Energy discharged from battery in Wh
        
    Returns:
        Battery efficiency in %, or None if calculation not possible
    """
    if battery_charge is None or battery_discharge is None:
        return None
    if battery_charge == 0:
        return 0.0
    try:
        return (battery_discharge / battery_charge) * 100
    except (TypeError, ValueError, ZeroDivisionError) as err:
        _LOGGER.warning("Cannot calculate battery efficiency: %s", err)
        return None


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


def safe_divide(numerator: Optional[float], denominator: Optional[float], default: float = 0.0) -> float:
    """
    Safely divide two numbers, returning default on error.
    
    Args:
        numerator: Number to divide
        denominator: Number to divide by
        default: Value to return on error
        
    Returns:
        Result of division or default value
    """
    if numerator is None or denominator is None:
        return default
    if denominator == 0:
        return default
    try:
        return numerator / denominator
    except (TypeError, ValueError, ZeroDivisionError):
        return default


def safe_multiply(value: Optional[float], factor: float) -> Optional[float]:
    """
    Safely multiply a value by a factor.
    
    Args:
        value: Value to multiply
        factor: Multiplication factor
        
    Returns:
        Result of multiplication or None on error
    """
    if value is None:
        return None
    try:
        return value * factor
    except (TypeError, ValueError):
        return None


def calculate_daily_delta(
    current_value: Optional[float],
    previous_value: Optional[float]
) -> Optional[float]:
    """
    Calculate daily delta between two cumulative values.
    
    Args:
        current_value: Current cumulative value
        previous_value: Previous cumulative value
        
    Returns:
        Delta value or None if calculation not possible
    """
    if current_value is None or previous_value is None:
        return None
    try:
        delta = current_value - previous_value
        # Ensure delta is non-negative (handles counter resets)
        return max(0.0, delta)
    except (TypeError, ValueError):
        return None


def format_energy_value(value: Optional[float], precision: int = 2) -> str:
    """
    Format energy value with appropriate unit (Wh, kWh, MWh).
    
    Args:
        value: Energy value in Wh
        precision: Decimal places
        
    Returns:
        Formatted string with unit
    """
    if value is None:
        return "Unknown"
    
    try:
        if value >= 1_000_000:
            return f"{value / 1_000_000:.{precision}f} MWh"
        elif value >= 1_000:
            return f"{value / 1_000:.{precision}f} kWh"
        else:
            return f"{value:.{precision}f} Wh"
    except (TypeError, ValueError):
        return "Unknown"


def is_daytime(sunrise: Optional[datetime], sunset: Optional[datetime]) -> bool:
    """
    Check if current time is between sunrise and sunset.
    
    Args:
        sunrise: Sunrise datetime
        sunset: Sunset datetime
        
    Returns:
        True if daytime, False otherwise
    """
    if sunrise is None or sunset is None:
        return False
    
    now = datetime.now(sunrise.tzinfo)
    return sunrise <= now <= sunset
