import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed

from .const import (
    CONF_AUDIENCE,
    CONF_CLIENT_ID,
    CONF_REALM,
    DEFAULT_AUDIENCE,
    DEFAULT_CLIENT_ID,
    DEFAULT_REALM,
    DOMAIN,
    LEGACY_AUDIENCE,
)
from .coordinator import GridXCoordinator
from .gridx_api import GridXAPI, GridXAuthenticationError

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up GridX integration from a config entry."""
    # Initialize data storage
    hass.data.setdefault(DOMAIN, {})

    # Create API client
    api = GridXAPI(
        hass,
        entry.data["username"],
        entry.data["password"],
        entry.data.get(CONF_CLIENT_ID, DEFAULT_CLIENT_ID),
        entry.data.get(CONF_REALM, DEFAULT_REALM),
        entry.data.get(CONF_AUDIENCE, DEFAULT_AUDIENCE),
    )

    # Authenticate and get gateway ID before creating coordinator
    try:
        await api.authenticate()
        await api.get_gateway_id()
    except GridXAuthenticationError as err:
        raise ConfigEntryAuthFailed("GridX authentication failed") from err
    _LOGGER.debug("GridX API authenticated, gateway_id: %s", api.gateway_id)

    # Create coordinator
    coordinator = GridXCoordinator(hass, api)
    hass.data[DOMAIN]["coordinator"] = coordinator

    # Perform initial data fetch
    await coordinator.async_config_entry_first_refresh()
    _LOGGER.debug("Initial coordinator refresh completed")

    # Forward sensor setup
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_migrate_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Migrate legacy Auth0 audience settings to the gridX API audience."""
    if entry.version > 2:
        return False

    if entry.version < 2:
        data = dict(entry.data)
        if data.get(CONF_AUDIENCE) in (None, LEGACY_AUDIENCE):
            data[CONF_AUDIENCE] = DEFAULT_AUDIENCE
        data.setdefault(CONF_CLIENT_ID, DEFAULT_CLIENT_ID)
        data.setdefault(CONF_REALM, DEFAULT_REALM)
        hass.config_entries.async_update_entry(entry, data=data, version=2)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data.pop(DOMAIN, None)
    return unload_ok
