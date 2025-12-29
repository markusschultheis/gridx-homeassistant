"""DataUpdateCoordinator for GridX integration."""
from datetime import timedelta
import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN
from .gridx_api import GridXAPI

_LOGGER = logging.getLogger(__name__)


class GridXCoordinator(DataUpdateCoordinator):
    """GridX data update coordinator."""

    def __init__(self, hass: HomeAssistant, api: GridXAPI) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(minutes=1),
        )
        self.api = api

    async def _async_update_data(self):
        """Fetch data from API."""
        try:
            _LOGGER.debug("GridXCoordinator fetching live data")
            data = await self.api.get_live_data()
            _LOGGER.debug("GridXCoordinator received data keys: %s", list(data.keys()) if isinstance(data, dict) else type(data))
            return data
        except Exception as err:
            raise UpdateFailed(f"Error communicating with API: {err}")
