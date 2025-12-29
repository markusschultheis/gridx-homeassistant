import aiohttp
import logging
import time
from .const import (
    AUTH_URL,
    GATEWAYS_URL,
    LIVE_URL,
    GRANT_TYPE,
    DOMAIN,
    DATA_ID_TOKEN,
    DATA_EXPIRES_AT,
    TOKEN_EXPIRATION_OFFSET,
)

_LOGGER = logging.getLogger(__name__)

class GridXAPI:
    """API client for GridX PV systems."""

    def __init__(self, hass, username, password, client_id, realm, audience):
        """Initialize the GridX API client."""
        self.hass = hass
        self.username = username
        self.password = password
        self.client_id = client_id
        self.realm = realm
        self.audience = audience
        self.gateway_id = None
        self.id_token = None
                
    async def authenticate(self):
        """Authenticate and obtain access token."""
        payload = {
            "grant_type": GRANT_TYPE,
            "username": self.username,
            "password": self.password,
            "audience": self.audience,
            "client_id": self.client_id,
            "scope": "email openid offline_access",
            "realm": self.realm
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(AUTH_URL, json=payload) as response:
                    response.raise_for_status()
                    data = await response.json()
                    self.id_token = data.get("id_token")
                    if self.hass:
                        self.hass.data[DOMAIN][DATA_ID_TOKEN] = self.id_token
                        self.hass.data[DOMAIN][DATA_EXPIRES_AT] = data.get("expires_in") + time.time() - TOKEN_EXPIRATION_OFFSET
        except aiohttp.ClientError as err:
            _LOGGER.error("Authentication request failed: %s", err)
            raise
        except Exception as err:
            _LOGGER.error("Authentication failed: %s", err)
            raise

    async def get_gateway_id(self):
        """Retrieve the gateway ID from the API."""
        headers = {"Authorization": f"Bearer {self.id_token}"}
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(GATEWAYS_URL, headers=headers) as response:
                    response.raise_for_status()
                    data = await response.json()
                    self.gateway_id = data[0]["system"]["id"]
        except aiohttp.ClientError as err:
            _LOGGER.error("Failed to retrieve gateway ID: %s", err)
            raise
        except (IndexError, KeyError) as err:
            _LOGGER.error("Invalid gateway data structure: %s", err)
            raise

    async def get_live_data(self):
        """Retrieve live data from the GridX API."""
        now = time.time()

        # Ensure we have a token and gateway id
        if self.id_token is None:
            await self.authenticate()
        if self.gateway_id is None:
            await self.get_gateway_id()

        # Validate token and gateway_id after retry
        if self.id_token is None:
            raise RuntimeError("Failed to obtain authentication token")
        if self.gateway_id is None:
            raise RuntimeError("Failed to obtain gateway ID")

        if now > self.hass.data[DOMAIN][DATA_EXPIRES_AT]:
            _LOGGER.info("Token expired, re-authenticating")
            await self.authenticate()

        headers = {"Authorization": f"Bearer {self.id_token}"}
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(LIVE_URL.format(self.gateway_id), headers=headers) as response:
                    response.raise_for_status()
                    return await response.json()
        except aiohttp.ClientError as err:
            _LOGGER.error("Failed to retrieve live data: %s", err)
            raise
