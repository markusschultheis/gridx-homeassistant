"""Async client for the E.ON Home/gridX cloud API."""

from __future__ import annotations

import asyncio
import logging
import time
from typing import Any

import aiohttp

from .const import (
    AUTH_SCOPE,
    AUTH_URL,
    DEFAULT_AUDIENCE,
    GATEWAYS_URL,
    GRANT_TYPE,
    LEGACY_AUDIENCE,
    LIVE_URL,
    REFRESH_GRANT_TYPE,
    TOKEN_EXPIRATION_OFFSET,
)

_LOGGER = logging.getLogger(__name__)


class GridXAuthenticationError(Exception):
    """Raised when Auth0 or the gridX API rejects authentication."""


class GridXAPI:
    """API client for E.ON Home/gridX PV systems."""

    def __init__(self, hass, username, password, client_id, realm, audience):
        """Initialize the gridX API client."""
        self.hass = hass
        self.username = username
        self.password = password
        self.client_id = client_id
        self.realm = realm
        # Normalize legacy config entries even before Home Assistant migration runs.
        self.audience = (
            DEFAULT_AUDIENCE if audience in (None, "", LEGACY_AUDIENCE) else audience
        )
        self.gateway_id: str | None = None
        self.access_token: str | None = None
        self.id_token: str | None = None
        self.refresh_token: str | None = None
        self._token_expires_at = 0.0
        self._auth_lock = asyncio.Lock()

    @property
    def token_valid(self) -> bool:
        """Return whether the current API access token is still valid."""
        return bool(self.bearer_token) and time.monotonic() < self._token_expires_at

    @property
    def bearer_token(self) -> str | None:
        """Return the API bearer token, preferring the OAuth access token."""
        return self.access_token or self.id_token

    def _store_token_response(
        self, data: dict[str, Any], *, preserve_refresh_token: bool = False
    ) -> None:
        """Validate and store an Auth0 token response."""
        access_token = data.get("access_token")
        id_token = data.get("id_token")

        # The current gridX API expects access_token. The id_token fallback keeps
        # the adapter usable during a staged rollout or with a legacy OEM tenant.
        if not isinstance(access_token, str) or not access_token:
            if not isinstance(id_token, str) or not id_token:
                raise GridXAuthenticationError(
                    "Authentication response did not contain a token"
                )
            _LOGGER.warning(
                "Auth0 response did not contain an access_token; using legacy "
                "id_token compatibility mode"
            )
            access_token = None

        expires_in = data.get("expires_in", 3600)
        try:
            expires_in = max(1, int(expires_in))
        except (TypeError, ValueError):
            expires_in = 3600
        refresh_offset = min(TOKEN_EXPIRATION_OFFSET, max(1, expires_in // 10))

        refresh_token = data.get("refresh_token")
        if not isinstance(refresh_token, str) or not refresh_token:
            refresh_token = self.refresh_token if preserve_refresh_token else None

        self.access_token = access_token
        self.id_token = id_token if isinstance(id_token, str) else None
        self.refresh_token = refresh_token
        self._token_expires_at = time.monotonic() + max(
            1, expires_in - refresh_offset
        )

    async def _request_token(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Request a token from Auth0 and validate the response envelope."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(AUTH_URL, json=payload) as response:
                    if response.status in (400, 401, 403):
                        raise GridXAuthenticationError(
                            f"Authentication was rejected with HTTP {response.status}"
                        )
                    response.raise_for_status()
                    data = await response.json()
        except GridXAuthenticationError:
            raise
        except aiohttp.ClientError as err:
            _LOGGER.error("Authentication request failed: %s", err)
            raise

        if not isinstance(data, dict):
            raise GridXAuthenticationError(
                "Authentication response was not a JSON object"
            )
        return data

    async def authenticate(self, *, force: bool = False) -> None:
        """Authenticate with the current password-realm flow."""
        if self.token_valid and not force:
            return

        async with self._auth_lock:
            if self.token_valid and not force:
                return

            payload = {
                "grant_type": GRANT_TYPE,
                "username": self.username,
                "password": self.password,
                "audience": self.audience,
                "client_id": self.client_id,
                "scope": AUTH_SCOPE,
                "realm": self.realm,
            }
            data = await self._request_token(payload)
            self._store_token_response(data)
            _LOGGER.debug("GridX authentication succeeded")

    async def _refresh_access_token(self) -> None:
        """Exchange the refresh token for a new gridX API access token."""
        async with self._auth_lock:
            if self.token_valid:
                return
            if not self.refresh_token:
                raise GridXAuthenticationError("No refresh token is available")

            payload = {
                "grant_type": REFRESH_GRANT_TYPE,
                "refresh_token": self.refresh_token,
                "client_id": self.client_id,
            }
            try:
                data = await self._request_token(payload)
            except (GridXAuthenticationError, aiohttp.ClientError):
                # A rotating refresh token must not be replayed if the server may
                # have consumed it before the response failed.
                self.refresh_token = None
                raise
            self._store_token_response(data, preserve_refresh_token=True)
            _LOGGER.debug("GridX access token refreshed")

    async def _ensure_token(self) -> None:
        """Ensure that a usable access token is available."""
        if self.token_valid:
            return

        if self.refresh_token:
            try:
                await self._refresh_access_token()
                return
            except (GridXAuthenticationError, aiohttp.ClientError) as err:
                _LOGGER.debug(
                    "GridX token refresh failed; falling back to password login: %s",
                    err,
                )
                self.refresh_token = None

        await self.authenticate()

    async def _authenticated_get(self, url: str) -> Any:
        """Perform a GET request and recover once from a rejected token."""
        for attempt in range(2):
            await self._ensure_token()
            token = self.bearer_token
            if token is None:
                raise GridXAuthenticationError("No bearer token is available")

            headers = {"Authorization": f"Bearer {token}"}
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, headers=headers) as response:
                        if response.status in (401, 403):
                            if attempt == 0:
                                self._token_expires_at = 0.0
                                continue
                            raise GridXAuthenticationError(
                                "GridX rejected the refreshed access token"
                            )
                        response.raise_for_status()
                        return await response.json()
            except GridXAuthenticationError:
                raise
            except aiohttp.ClientError as err:
                _LOGGER.error("GridX API request failed: %s", err)
                raise

        raise GridXAuthenticationError("GridX authentication failed")

    async def get_gateway_id(self) -> str:
        """Retrieve the first gateway's system ID from the gridX API."""
        data = await self._authenticated_get(GATEWAYS_URL)
        try:
            gateway_id = data[0]["system"]["id"]
        except (IndexError, KeyError, TypeError) as err:
            _LOGGER.error("Invalid gateway data structure: %s", err)
            raise ValueError("Invalid gateway data structure") from err

        if not isinstance(gateway_id, str) or not gateway_id:
            raise ValueError("Gateway system ID is missing")
        self.gateway_id = gateway_id
        return gateway_id

    async def get_live_data(self) -> Any:
        """Retrieve current measurements from the gridX API."""
        if self.gateway_id is None:
            await self.get_gateway_id()
        return await self._authenticated_get(LIVE_URL.format(self.gateway_id))
