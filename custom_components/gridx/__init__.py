import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed

from .const import (
    CONF_AUDIENCE,
    CONF_CLIENT_ID,
    CONF_PROVIDER,
    CONF_REALM,
    DEFAULT_AUDIENCE,
    DEFAULT_CLIENT_ID,
    DEFAULT_REALM,
    DOMAIN,
    LEGACY_AUDIENCE,
)
from .coordinator import GridXCoordinator
from .gridx_api import GridXAPI, GridXAuthenticationError
from .providers import get_provider, provider_from_auth

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]


def _resolved_auth(data) -> tuple[str, str, str]:
    """Resolve provider-managed Auth0 values while preserving custom entries."""

    provider = get_provider(data.get(CONF_PROVIDER))
    if provider is not None:
        return provider.client_id, provider.realm, provider.audience

    return (
        data.get(CONF_CLIENT_ID, DEFAULT_CLIENT_ID),
        data.get(CONF_REALM, DEFAULT_REALM),
        data.get(CONF_AUDIENCE) or DEFAULT_AUDIENCE,
    )


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up a gridX-backed OEM integration from a config entry."""

    hass.data.setdefault(DOMAIN, {})
    client_id, realm, audience = _resolved_auth(entry.data)

    api = GridXAPI(
        hass,
        entry.data["username"],
        entry.data["password"],
        client_id,
        realm,
        audience,
    )

    try:
        await api.authenticate()
        await api.get_gateway_id()
    except GridXAuthenticationError as err:
        raise ConfigEntryAuthFailed("GridX authentication failed") from err
    _LOGGER.debug(
        "GridX API authenticated, provider=%s gateway_id=%s",
        entry.data.get(CONF_PROVIDER, "legacy"),
        api.gateway_id,
    )

    coordinator = GridXCoordinator(hass, api)
    hass.data[DOMAIN]["coordinator"] = coordinator

    await coordinator.async_config_entry_first_refresh()
    _LOGGER.debug("Initial coordinator refresh completed")

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_migrate_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Migrate legacy Auth0 settings to provider-aware config version 3."""

    if entry.version > 3:
        return False
    if entry.version == 3:
        return True

    data = dict(entry.data)
    data.setdefault(CONF_CLIENT_ID, DEFAULT_CLIENT_ID)
    data.setdefault(CONF_REALM, DEFAULT_REALM)

    provider_key = data.get(CONF_PROVIDER) or provider_from_auth(
        data.get(CONF_CLIENT_ID), data.get(CONF_REALM)
    )
    provider = get_provider(provider_key)
    data[CONF_PROVIDER] = provider_key

    audience = data.get(CONF_AUDIENCE)
    if provider_key == "eon_home":
        # The old integration was E.ON-centric and migrated `my.gridx` to the
        # current API audience. Keep that proven behavior for E.ON only.
        if audience in (None, "", LEGACY_AUDIENCE):
            data[CONF_AUDIENCE] = DEFAULT_AUDIENCE
    elif provider is not None:
        # Known non-E.ON OEM profiles use their registry-authored audience.
        # Runtime also resolves from the registry, so stale stored values cannot
        # silently force an E.ON-specific token mode onto another provider.
        data[CONF_AUDIENCE] = provider.audience
    elif audience in (None, ""):
        # Unknown/custom historical entries retain any explicit audience. Only
        # a truly absent value receives the current integration default.
        data[CONF_AUDIENCE] = DEFAULT_AUDIENCE

    hass.config_entries.async_update_entry(entry, data=data, version=3)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""

    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data.pop(DOMAIN, None)
    return unload_ok
