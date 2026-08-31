import logging

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers.selector import (
    SelectOptionDict,
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
)

from .const import (
    CONF_PROVIDER,
    DEFAULT_AUDIENCE,
    DEFAULT_PROVIDER,
    DOMAIN,
    PROVIDERS,
)
from .gridx_api import GridXAPI

_LOGGER = logging.getLogger(__name__)


def _provider_selector() -> SelectSelector:
    """Return a dropdown containing every known gridX customer portal."""
    options = [
        SelectOptionDict(value=provider.key, label=provider.label)
        for provider in sorted(PROVIDERS.values(), key=lambda item: item.label.lower())
    ]
    return SelectSelector(
        SelectSelectorConfig(options=options, mode=SelectSelectorMode.DROPDOWN)
    )


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for GridX PV system."""
    VERSION = 3

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            # Validate credentials by attempting authentication
            try:
                provider = PROVIDERS[user_input[CONF_PROVIDER]]
                api = GridXAPI(
                    None,  # hass not needed for validation
                    user_input["username"],
                    user_input["password"],
                    provider.client_id,
                    provider.realm,
                    DEFAULT_AUDIENCE,
                )
                await api.authenticate()
                await api.get_gateway_id()
                return self.async_create_entry(
                    title=f"GridX – {provider.label}",
                    data={
                        CONF_PROVIDER: provider.key,
                        "username": user_input["username"],
                        "password": user_input["password"],
                    },
                )
            except Exception as err:
                _LOGGER.error("Authentication failed: %s", err)
                errors["base"] = "auth_failed"

        schema = vol.Schema(
            {
                vol.Required(
                    CONF_PROVIDER, default=DEFAULT_PROVIDER
                ): _provider_selector(),
                vol.Required("username"): str,
                vol.Required("password"): str,
            }
        )

        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)
