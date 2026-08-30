"""Regression tests for gridX OEM provider selection."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
from types import ModuleType
import unittest


COMPONENT_DIR = Path(__file__).parents[1] / "custom_components" / "gridx"
PACKAGE_NAME = "_gridx_provider_test_package"

package = ModuleType(PACKAGE_NAME)
package.__path__ = [str(COMPONENT_DIR)]
sys.modules.setdefault(PACKAGE_NAME, package)

for module_name in ("const", "providers"):
    spec = importlib.util.spec_from_file_location(
        f"{PACKAGE_NAME}.{module_name}", COMPONENT_DIR / f"{module_name}.py"
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)

providers = sys.modules[f"{PACKAGE_NAME}.providers"]


class ProviderRegistryTests(unittest.TestCase):
    def test_eon_home_remains_default(self):
        self.assertEqual(providers.DEFAULT_PROVIDER, "eon_home")
        profile = providers.get_provider("eon_home")
        self.assertIsNotNone(profile)
        self.assertEqual(profile.realm, "eon-home-authentication-db")
        self.assertEqual(profile.audience, "https://api.gridx.de")

    def test_active_oem_profiles_are_available(self):
        for key in ("1komma5grad", "octopus", "sonnen", "lew", "ibc_homeone"):
            with self.subTest(provider=key):
                profile = providers.get_provider(key)
                self.assertIsNotNone(profile)
                self.assertFalse(profile.legacy)
                self.assertEqual(profile.audience, "my.gridx")

    def test_retired_viessmann_realm_is_not_offered_for_new_setup(self):
        profile = providers.get_provider("viessmann")
        self.assertIsNotNone(profile)
        self.assertTrue(profile.legacy)
        self.assertEqual(profile.audience, "my.gridx")
        self.assertNotIn("viessmann", providers.provider_choices())

    def test_legacy_eon_auth_is_mapped_to_provider(self):
        self.assertEqual(
            providers.provider_from_auth(
                "mG0Phmo7DmnvAqO7p6B0WOYBODppY3cc",
                "eon-home-authentication-db",
            ),
            "eon_home",
        )

    def test_unknown_auth_profile_remains_custom(self):
        self.assertEqual(
            providers.provider_from_auth("unknown-client", "unknown-realm"),
            providers.CUSTOM_PROVIDER,
        )
        self.assertIsNone(providers.get_provider(providers.CUSTOM_PROVIDER))


if __name__ == "__main__":
    unittest.main()
