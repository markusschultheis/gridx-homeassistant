import logging

import voluptuous as vol
from homeassistant import config_entries

from .const import (
    CONF_AUDIENCE,
    CONF_CLIENT_ID,
    CONF_PROVIDER,
    CONF_REALM,
    DEFAULT_AUDIENCE,
    DOMAIN,
)
from .gridx_api import GridXAPI
from .providers import CUSTOM_PROVIDER, DEFAULT_PROVIDER, get_provider, provider_choices

_LOGGER = logging.getLogger(__name__)


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for gridX-backed OEM energy systems."""

    VERSION = 3

    def __init__(self) -> None:
        self._pending_credentials: dict[str, str] | None = None

    async def _validate(self, data: dict) -> str:
        """Validate authentication and return the first gridX system id."""

        api = GridXAPI(
            None,  # hass is not needed by the API client
            data["username"],
            data["password"],
            data[CONF_CLIENT_ID],
            data[CONF_REALM],
            data[CONF_AUDIENCE],
        )
        await api.authenticate()
        return await api.get_gateway_id()

    async def _create_validated_entry(self, data: dict):
        errors = {}
        try:
            system_id = await self._validate(data)
        except Exception as err:
            _LOGGER.error("gridX authentication/validation failed: %s", err)
            errors["base"] = "auth_failed"
        else:
            await self.async_set_unique_id(system_id)
            self._abort_if_unique_id_configured()
            provider = get_provider(data.get(CONF_PROVIDER))
            title = provider.label if provider is not None else "gridX Energy Management"
            return self.async_create_entry(title=title, data=data)
        return errors

    async def async_step_user(self, user_input=None):
        """Select an OEM provider and enter account credentials."""

        errors = {}
        if user_input is not None:
            provider_key = user_input[CONF_PROVIDER]
            credentials = {
                CONF_PROVIDER: provider_key,
                "username": user_input["username"],
                "password": user_input["password"],
            }
            provider = get_provider(provider_key)
            if provider is None:
                self._pending_credentials = credentials
                return await self.async_step_custom()

            data = {
                **credentials,
                CONF_CLIENT_ID: provider.client_id,
                CONF_REALM: provider.realm,
                CONF_AUDIENCE: provider.audience,
            }
            result = await self._create_validated_entry(data)
            if not isinstance(result, dict):
                return result
            errors = result

        schema = vol.Schema(
            {
                vol.Required(CONF_PROVIDER, default=DEFAULT_PROVIDER): vol.In(provider_choices()),
                vol.Required("username"): str,
                vol.Required("password"): str,
            }
        )
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    async def async_step_custom(self, user_input=None):
        """Configure an explicit Auth0 profile for an unlisted gridX OEM."""

        if self._pending_credentials is None:
            return await self.async_step_user()

        errors = {}
        if user_input is not None:
            data = {
                **self._pending_credentials,
                CONF_PROVIDER: CUSTOM_PROVIDER,
                CONF_CLIENT_ID: user_input[CONF_CLIENT_ID],
                CONF_REALM: user_input[CONF_REALM],
                CONF_AUDIENCE: user_input[CONF_AUDIENCE],
            }
            result = await self._create_validated_entry(data)
            if not isinstance(result, dict):
                self._pending_credentials = None
                return result
            errors = result

        schema = vol.Schema(
            {
                vol.Required(CONF_CLIENT_ID): str,
                vol.Required(CONF_REALM): str,
                vol.Required(CONF_AUDIENCE, default=DEFAULT_AUDIENCE): str,
            }
        )
        return self.async_show_form(step_id="custom", data_schema=schema, errors=errors)
