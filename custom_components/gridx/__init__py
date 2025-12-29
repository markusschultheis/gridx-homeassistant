from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
import logging

from .const import DOMAIN, DATA_EXPIRES_AT, DATA_ID_TOKEN
from .coordinator import GridXCoordinator
from .gridx_api import GridXAPI

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up GridX integration from a config entry."""
    # Initialize data storage
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN].setdefault(DATA_EXPIRES_AT, 0)
    hass.data[DOMAIN].setdefault(DATA_ID_TOKEN, None)

    # Create API client
    api = GridXAPI(
        hass,
        entry.data["username"],
        entry.data["password"],
        entry.data["client_id"],
        entry.data["realm"],
        entry.data["audience"],
    )

    # Authenticate and get gateway ID before creating coordinator
    await api.authenticate()
    await api.get_gateway_id()
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


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data.pop(DOMAIN, None)
    return unload_ok
