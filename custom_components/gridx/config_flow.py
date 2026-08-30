import logging

import voluptuous as vol
from homeassistant import config_entries

from .const import (
    CONF_AUDIENCE,
    CONF_CLIENT_ID,
    CONF_REALM,
    DEFAULT_AUDIENCE,
    DEFAULT_CLIENT_ID,
    DEFAULT_REALM,
    DOMAIN,
)
from .gridx_api import GridXAPI

_LOGGER = logging.getLogger(__name__)


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for GridX PV system."""
    VERSION = 2

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            # Validate credentials by attempting authentication
            try:
                api = GridXAPI(
                    None,  # hass not needed for validation
                    user_input["username"],
                    user_input["password"],
                    user_input["client_id"],
                    user_input["realm"],
                    user_input["audience"],
                )
                # Test authentication
                await api.authenticate()
                return self.async_create_entry(title="GridX-Box Data Collector", data=user_input)
            except Exception as err:
                _LOGGER.error("Authentication failed: %s", err)
                errors["base"] = "auth_failed"

        schema = vol.Schema({
            vol.Required("username"): str,
            vol.Required("password"): str,
            vol.Required(CONF_CLIENT_ID, default=DEFAULT_CLIENT_ID): str,
            vol.Required(CONF_REALM, default=DEFAULT_REALM): str,
            vol.Required(CONF_AUDIENCE, default=DEFAULT_AUDIENCE): str,
        })

        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)
