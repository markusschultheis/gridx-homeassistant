from homeassistant.components.sensor import SensorEntity, SensorDeviceClass
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN
from typing import Any, Optional


class GridXSensor(CoordinatorEntity, SensorEntity):
    """Representation of a GridX sensor."""

    def __init__(self, coordinator: Any, name: str, unit: Optional[str], key: str, unique_id: str, device_class: Optional[SensorDeviceClass]) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._key = key
        self._unique_id = unique_id
        self._device_class = device_class
        self._attr_native_unit_of_measurement = unit
        self._attr_name = name  # For entity registry support and user renaming
        
        # Set device info once with the gateway_id from coordinator
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.api.gateway_id)},
            name="GridX API Connector",
            manufacturer="Markus Schultheis (c) 2024-2025",
            model="GridX-Box Data Collector",
        )

    @property
    def native_value(self) -> Optional[float]:
        """Return the current value from coordinator data."""
        if self.coordinator.data is None:
            return None
        value = self.extract_value(self.coordinator.data)
        return value

    @property
    def unique_id(self) -> str:
        """Return the unique ID of the sensor."""
        return self._unique_id

    @property
    def device_class(self) -> Optional[SensorDeviceClass]:
        """Return the device class."""
        return self._device_class

    @property
    def available(self) -> bool:
        """Return if the sensor is available."""
        return self.coordinator.last_update_success

    def extract_value(self, data: Any) -> Any:
        """Extract the desired value from the API response."""
        keys = self._key.split(".")
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

        # Normalize rate fields (API may send either 0..1 or 0..100)
        if isinstance(value, (int, float)):
            key_lower = self._key.lower().replace("_", "")
            if key_lower.endswith("rate") and 0.0 <= value <= 1.0:
                return value * 100

        return value
