from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.components.sensor import SensorDeviceClass
import logging
from .const import DOMAIN
from .entities import GridXSensor
from .calculated_sensors import CALCULATED_SENSOR_CLASSES

_LOGGER = logging.getLogger(__name__)

def flatten_dict(d, prefix=''):
    """Flatten a nested dict into a list of (key_path, value) tuples for numeric values."""
    items = []
    for k, v in d.items():
        new_key = f"{prefix}.{k}" if prefix else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key))
        elif isinstance(v, list):
            # Handle lists: if list of dicts, take the first item; if list of numbers, skip for now
            if v and isinstance(v[0], dict):
                items.extend(flatten_dict(v[0], f"{new_key}.0"))
        elif isinstance(v, (int, float)):
            items.append((new_key, v))
    return items

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    """Set up GridX sensors from a config entry."""
    try:
        # Get coordinator from hass.data
        coordinator = hass.data[DOMAIN]["coordinator"]
        
        # Use coordinator data (already fetched during initialization)
        data = coordinator.data
        if not data:
            _LOGGER.warning("No data available from coordinator yet")
            data = {}

        # Create sensors dynamically from API response
        sensors = []
        flattened = flatten_dict(data)
        if not flattened:
            _LOGGER.warning("No numeric values found in API response to create sensors")
        _LOGGER.debug("Flattened keys from API: %s", [k for k, _ in flattened])
        for key, _ in flattened:
            # Generate name from key
            name = key.replace(".", " ").title()
            
            # Determine unit and device_class based on keywords
            unit = None
            device_class = None
            key_lower = key.lower()
            if "power" in key_lower:
                unit = "W"
                device_class = SensorDeviceClass.POWER
            elif "rate" in key_lower:
                unit = "%"  # Rates are percentages
            elif any(word in key_lower for word in ["efficiency", "stateofcharge"]):
                unit = "%"
            elif any(word in key_lower for word in ["charge", "capacity", "production", "consumption", "supply", "grid", "photovoltaic", "directconsumption"]):
                unit = "Wh"
                device_class = SensorDeviceClass.ENERGY
            
            # Generate unique ID
            unique_id = f"gridx_{key.replace('.', '_')}"
            
            _LOGGER.debug("Creating sensor - key: %s, name: %s, unit: %s, device_class: %s", key, name, unit, device_class)
            sensors.append(GridXSensor(coordinator, name, unit, key, unique_id, device_class))
        
        _LOGGER.info("Created %d regular sensors", len(sensors))
        
        # Add calculated sensors
        for sensor_class in CALCULATED_SENSOR_CLASSES:
            try:
                # Handle both direct class and lambda functions
                if callable(sensor_class) and not isinstance(sensor_class, type):
                    sensors.append(sensor_class(coordinator))
                else:
                    sensors.append(sensor_class(coordinator))
            except Exception as err:
                sensor_name = getattr(sensor_class, '__name__', str(sensor_class))
                _LOGGER.warning("Failed to create calculated sensor %s: %s", sensor_name, err)
        
        _LOGGER.info("Total sensors created: %d", len(sensors))

        async_add_entities(sensors, update_before_add=True)
    except Exception as err:
        _LOGGER.error("Failed to setup GridX sensors: %s", err)
        raise
