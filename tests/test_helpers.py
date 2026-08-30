"""Tests for gridX sensor value normalization."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
from types import ModuleType
from unittest import TestCase


COMPONENT_DIR = Path(__file__).parents[1] / "custom_components" / "gridx"
PACKAGE_NAME = "_gridx_helpers_test_package"

package = ModuleType(PACKAGE_NAME)
package.__path__ = [str(COMPONENT_DIR)]
sys.modules.setdefault(PACKAGE_NAME, package)

spec = importlib.util.spec_from_file_location(
    f"{PACKAGE_NAME}.helpers", COMPONENT_DIR / "helpers.py"
)
assert spec is not None and spec.loader is not None
helpers_module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = helpers_module
spec.loader.exec_module(helpers_module)

normalize_sensor_value = helpers_module.normalize_sensor_value


class SensorValueNormalizationTests(TestCase):
    """Verify conversions from gridX API units to Home Assistant units."""

    def test_grid_import_meter_reading_is_converted_from_ws_to_wh(self):
        self.assertEqual(
            normalize_sensor_value("gridMeterReadingPositive", 3_600_000),
            1000,
        )

    def test_grid_export_meter_reading_is_converted_from_ws_to_wh(self):
        self.assertEqual(
            normalize_sensor_value("gridMeterReadingNegative", 18_000_000),
            5000,
        )

    def test_nested_meter_reading_is_also_converted(self):
        self.assertEqual(
            normalize_sensor_value(
                "appliances.0.heatPumpMeterReadingPositive", 7_200_000
            ),
            2000,
        )

    def test_rate_normalization_is_preserved(self):
        self.assertEqual(normalize_sensor_value("selfConsumptionRate", 0.75), 75)

    def test_other_measurements_are_unchanged(self):
        self.assertEqual(normalize_sensor_value("photovoltaic", 4200), 4200)
        self.assertIsNone(normalize_sensor_value("gridMeterReadingPositive", None))
