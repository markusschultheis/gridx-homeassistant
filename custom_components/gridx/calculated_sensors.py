"""Calculated sensor entities for GridX integration."""
from typing import Any, Optional
from datetime import datetime
from homeassistant.components.sensor import SensorEntity, SensorStateClass, SensorDeviceClass, RestoreSensor
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.event import async_track_time_change
from homeassistant.core import callback
from .const import DOMAIN
from .helpers import extract_nested_value


class GridXCalculatedSensor(CoordinatorEntity, SensorEntity):
    """Base class for calculated GridX sensors."""

    def __init__(
        self,
        coordinator: Any,
        name: str,
        unique_id: str,
        unit: Optional[str],
        device_class: Optional[SensorDeviceClass] = None,
        state_class: Optional[SensorStateClass] = None,
    ) -> None:
        """Initialize the calculated sensor."""
        super().__init__(coordinator)
        self._attr_name = name
        self._attr_unique_id = unique_id
        self._attr_native_unit_of_measurement = unit
        self._attr_device_class = device_class
        self._attr_state_class = state_class or SensorStateClass.MEASUREMENT
        
        # Set device info to group with other GridX sensors
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.api.gateway_id)},
            name="GridX System",
            manufacturer="GridX",
            model="GridX Gateway",
        )

    @property
    def available(self) -> bool:
        """Return if the sensor is available."""
        return self.coordinator.last_update_success


class BatteryChargePowerSensor(GridXCalculatedSensor):
    """Sensor for battery charging power (positive when charging)."""

    def __init__(self, coordinator: Any) -> None:
        """Initialize the battery charge power sensor."""
        super().__init__(
            coordinator=coordinator,
            name="GridX Battery Charge Power",
            unique_id="gridx_battery_charge_power",
            unit="W",
            device_class=SensorDeviceClass.POWER,
        )

    @property
    def native_value(self) -> Optional[float]:
        """Return battery power (positive = charging, negative = discharging)."""
        if self.coordinator.data is None:
            return None
        
        battery_power = extract_nested_value(self.coordinator.data, "battery.power")
        return battery_power


class BatteryEnergyStoredSensor(GridXCalculatedSensor):
    """Sensor for actual energy stored in battery (capacity * state of charge)."""

    def __init__(self, coordinator: Any) -> None:
        """Initialize the battery energy stored sensor."""
        super().__init__(
            coordinator=coordinator,
            name="GridX Battery Energy Stored",
            unique_id="gridx_battery_energy_stored",
            unit="Wh",
            device_class=SensorDeviceClass.ENERGY_STORAGE,
            state_class=SensorStateClass.MEASUREMENT,
        )

    @property
    def native_value(self) -> Optional[float]:
        """Calculate actual energy stored in battery."""
        if self.coordinator.data is None:
            return None
        
        # Use remainingCharge if available, otherwise calculate from capacity and SOC
        remaining_charge = extract_nested_value(self.coordinator.data, "battery.remainingCharge")
        if remaining_charge is not None:
            return remaining_charge
        
        capacity = extract_nested_value(self.coordinator.data, "battery.capacity")
        soc = extract_nested_value(self.coordinator.data, "battery.stateOfCharge")
        
        if capacity is None or soc is None:
            return None
        
        try:
            return (capacity * soc) / 100
        except (TypeError, ValueError, ZeroDivisionError):
            return None


class GridExportRateSensor(GridXCalculatedSensor):
    """Sensor for grid export rate (production / consumption ratio)."""

    def __init__(self, coordinator: Any) -> None:
        """Initialize the grid export rate sensor."""
        super().__init__(
            coordinator=coordinator,
            name="GridX Grid Export Rate",
            unique_id="gridx_grid_export_rate",
            unit="%",
        )

    @property
    def native_value(self) -> Optional[float]:
        """Calculate what percentage of production is exported to grid."""
        if self.coordinator.data is None:
            return None
        
        production = extract_nested_value(self.coordinator.data, "production")
        self_consumption = extract_nested_value(self.coordinator.data, "selfConsumption")
        
        if production is None or self_consumption is None:
            return None
        
        if production == 0:
            return 0.0
        
        try:
            grid_export = production - self_consumption
            return (grid_export / production) * 100
        except (TypeError, ValueError, ZeroDivisionError):
            return None


class PeriodEnergySensor(CoordinatorEntity, RestoreSensor):
    """Base class for period-based energy tracking sensors."""

    def __init__(
        self,
        coordinator: Any,
        name: str,
        unique_id: str,
        period: str,  # 'daily', 'weekly', 'monthly'
        device_class: SensorDeviceClass,
    ) -> None:
        """Initialize the period energy sensor."""
        super().__init__(coordinator)
        self._attr_name = name
        self._attr_unique_id = unique_id
        self._attr_native_unit_of_measurement = "kWh"
        self._attr_device_class = device_class
        self._attr_state_class = SensorStateClass.TOTAL
        self._period = period
        self._last_value = 0.0
        self._last_reset = datetime.now()
        self._accumulated = 0.0
        
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.api.gateway_id)},
            name="GridX System",
            manufacturer="GridX",
            model="GridX Gateway",
        )

    async def async_added_to_hass(self) -> None:
        """Restore last state."""
        await super().async_added_to_hass()
        if (last_state := await self.async_get_last_state()) is not None:
            try:
                self._accumulated = float(last_state.state)
            except (ValueError, TypeError):
                self._accumulated = 0.0
            
            if last_state.attributes.get("last_reset"):
                try:
                    self._last_reset = datetime.fromisoformat(last_state.attributes["last_reset"])
                except (ValueError, TypeError):
                    self._last_reset = datetime.now()
        
        # Schedule periodic reset
        if self._period == "daily":
            async_track_time_change(self.hass, self._handle_reset, hour=0, minute=0, second=0)
        elif self._period == "weekly":
            # Reset on Monday at midnight
            async_track_time_change(self.hass, self._handle_reset_weekly, hour=0, minute=0, second=0)
        elif self._period == "monthly":
            # Reset on 1st of month at midnight
            async_track_time_change(self.hass, self._handle_reset_monthly, hour=0, minute=0, second=0)

    @callback
    def _handle_reset(self, now: datetime) -> None:
        """Reset daily counter."""
        self._accumulated = 0.0
        self._last_reset = now
        self.async_write_ha_state()

    @callback
    def _handle_reset_weekly(self, now: datetime) -> None:
        """Reset weekly counter on Monday."""
        if now.weekday() == 0:  # Monday
            self._accumulated = 0.0
            self._last_reset = now
            self.async_write_ha_state()

    @callback
    def _handle_reset_monthly(self, now: datetime) -> None:
        """Reset monthly counter on 1st of month."""
        if now.day == 1:
            self._accumulated = 0.0
            self._last_reset = now
            self.async_write_ha_state()

    @property
    def native_value(self) -> Optional[float]:
        """Return the accumulated energy."""
        return round(self._accumulated, 3) if self._accumulated is not None else None

    @property
    def extra_state_attributes(self) -> dict:
        """Return extra attributes."""
        return {
            "last_reset": self._last_reset.isoformat(),
            "period": self._period,
        }

    @property
    def available(self) -> bool:
        """Return if sensor is available."""
        return self.coordinator.last_update_success


class BatteryChargeSensor(PeriodEnergySensor):
    """Base class for battery charge sensors."""

    def __init__(self, coordinator: Any, period: str) -> None:
        """Initialize battery charge sensor."""
        period_name = period.capitalize()
        super().__init__(
            coordinator=coordinator,
            name=f"GridX Battery Charge {period_name}",
            unique_id=f"gridx_battery_charge_{period}",
            period=period,
            device_class=SensorDeviceClass.ENERGY,
        )

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        if self.coordinator.data is None:
            return
        
        # Get current battery power (positive = charging, negative = discharging)
        current_power = extract_nested_value(self.coordinator.data, "battery.power") or 0.0
        
        # Only accumulate positive power (charging)
        if current_power > 0:
            # Convert W to kWh: (power in W * update_interval in seconds) / 3600 / 1000
            energy_kwh = (current_power * 60) / 3600000  # Assuming 1-minute updates
            self._accumulated += energy_kwh
        
        self.async_write_ha_state()


class BatteryDischargeSensor(PeriodEnergySensor):
    """Base class for battery discharge sensors."""

    def __init__(self, coordinator: Any, period: str) -> None:
        """Initialize battery discharge sensor."""
        period_name = period.capitalize()
        super().__init__(
            coordinator=coordinator,
            name=f"GridX Battery Discharge {period_name}",
            unique_id=f"gridx_battery_discharge_{period}",
            period=period,
            device_class=SensorDeviceClass.ENERGY,
        )

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        if self.coordinator.data is None:
            return
        
        # Get current battery power (positive = charging, negative = discharging)
        current_power = extract_nested_value(self.coordinator.data, "battery.power") or 0.0
        
        # Only accumulate negative power (discharging), convert to positive
        if current_power < 0:
            energy_kwh = (abs(current_power) * 60) / 3600000  # Assuming 1-minute updates
            self._accumulated += energy_kwh
        
        self.async_write_ha_state()


class GridImportSensor(PeriodEnergySensor):
    """Base class for grid import sensors."""

    def __init__(self, coordinator: Any, period: str) -> None:
        """Initialize grid import sensor."""
        period_name = period.capitalize()
        super().__init__(
            coordinator=coordinator,
            name=f"GridX Grid Import {period_name}",
            unique_id=f"gridx_grid_import_{period}",
            period=period,
            device_class=SensorDeviceClass.ENERGY,
        )

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        if self.coordinator.data is None:
            return
        
        # Get grid power (positive = import, negative = export)
        grid_power = extract_nested_value(self.coordinator.data, "grid") or 0.0
        
        # Only accumulate positive power (importing from grid)
        if grid_power > 0:
            energy_kwh = (grid_power * 60) / 3600000  # Assuming 1-minute updates
            self._accumulated += energy_kwh
        
        self.async_write_ha_state()


class GridExportSensor(PeriodEnergySensor):
    """Base class for grid export sensors."""

    def __init__(self, coordinator: Any, period: str) -> None:
        """Initialize grid export sensor."""
        period_name = period.capitalize()
        super().__init__(
            coordinator=coordinator,
            name=f"GridX Grid Export {period_name}",
            unique_id=f"gridx_grid_export_{period}",
            period=period,
            device_class=SensorDeviceClass.ENERGY,
        )

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        if self.coordinator.data is None:
            return
        
        # Calculate export: production - self consumption
        production = extract_nested_value(self.coordinator.data, "production") or 0.0
        self_consumption = extract_nested_value(self.coordinator.data, "selfConsumption") or 0.0
        grid_export = max(0, production - self_consumption)
        
        if grid_export > 0:
            energy_kwh = (grid_export * 60) / 3600000  # Assuming 1-minute updates
            self._accumulated += energy_kwh
        
        self.async_write_ha_state()


# List of all calculated sensor classes
CALCULATED_SENSOR_CLASSES = [
    BatteryChargePowerSensor,
    BatteryEnergyStoredSensor,
    GridExportRateSensor,
    # Daily sensors
    lambda coord: BatteryChargeSensor(coord, "daily"),
    lambda coord: BatteryDischargeSensor(coord, "daily"),
    lambda coord: GridImportSensor(coord, "daily"),
    lambda coord: GridExportSensor(coord, "daily"),
    # Weekly sensors
    lambda coord: BatteryChargeSensor(coord, "weekly"),
    lambda coord: BatteryDischargeSensor(coord, "weekly"),
    lambda coord: GridImportSensor(coord, "weekly"),
    lambda coord: GridExportSensor(coord, "weekly"),
    # Monthly sensors
    lambda coord: BatteryChargeSensor(coord, "monthly"),
    lambda coord: BatteryDischargeSensor(coord, "monthly"),
    lambda coord: GridImportSensor(coord, "monthly"),
    lambda coord: GridExportSensor(coord, "monthly"),
]
