"""Regression tests for the E.ON Home/gridX authentication flow."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
from types import ModuleType
from unittest import IsolatedAsyncioTestCase
from unittest.mock import patch


COMPONENT_DIR = Path(__file__).parents[1] / "custom_components" / "gridx"
PACKAGE_NAME = "_gridx_auth_test_package"

package = ModuleType(PACKAGE_NAME)
package.__path__ = [str(COMPONENT_DIR)]
sys.modules.setdefault(PACKAGE_NAME, package)

spec = importlib.util.spec_from_file_location(
    f"{PACKAGE_NAME}.gridx_api", COMPONENT_DIR / "gridx_api.py"
)
assert spec is not None and spec.loader is not None
api_module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = api_module
spec.loader.exec_module(api_module)

GridXAPI = api_module.GridXAPI


class FakeResponse:
    """Minimal aiohttp response context manager."""

    def __init__(self, status: int, data):
        self.status = status
        self._data = data

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, traceback):
        return False

    def raise_for_status(self):
        if self.status >= 400:
            raise AssertionError(f"Unexpected HTTP {self.status}")

    async def json(self):
        return self._data


class FakeSession:
    """Record HTTP requests and return queued responses."""

    def __init__(self, *, post_responses=None, get_responses=None):
        self.post_responses = list(post_responses or [])
        self.get_responses = list(get_responses or [])
        self.requests = []

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, traceback):
        return False

    def post(self, url, *, json):
        self.requests.append(("POST", url, json))
        return self.post_responses.pop(0)

    def get(self, url, *, headers):
        self.requests.append(("GET", url, headers))
        return self.get_responses.pop(0)


def make_api(audience="my.gridx"):
    """Create an API instance with E.ON Home test credentials."""
    return GridXAPI(
        None,
        "user@example.com",
        "secret",
        "mG0Phmo7DmnvAqO7p6B0WOYBODppY3cc",
        "eon-home-authentication-db",
        audience,
    )


class GridXAuthenticationTests(IsolatedAsyncioTestCase):
    """Verify current token acquisition and recovery behavior."""

    async def test_login_migrates_audience_and_uses_access_token(self):
        session = FakeSession(
            post_responses=[
                FakeResponse(
                    200,
                    {
                        "access_token": "api-access-token",
                        "id_token": "identity-token",
                        "refresh_token": "refresh-token",
                        "expires_in": 3600,
                    },
                )
            ],
            get_responses=[FakeResponse(200, [{"system": {"id": "system-1"}}])],
        )
        api = make_api()

        with patch.object(api_module.aiohttp, "ClientSession", return_value=session):
            await api.authenticate()
            await api.get_gateway_id()

        login_payload = session.requests[0][2]
        self.assertEqual(login_payload["audience"], "https://api.gridx.de")
        self.assertEqual(
            login_payload["grant_type"],
            "http://auth0.com/oauth/grant-type/password-realm",
        )
        self.assertEqual(login_payload["scope"], "email openid offline_access")
        self.assertEqual(
            session.requests[1][2]["Authorization"], "Bearer api-access-token"
        )

    async def test_expired_access_token_is_refreshed(self):
        session = FakeSession(
            post_responses=[
                FakeResponse(
                    200,
                    {"access_token": "new-access-token", "expires_in": 3600},
                )
            ],
            get_responses=[FakeResponse(200, [{"system": {"id": "system-1"}}])],
        )
        api = make_api("https://api.gridx.de")
        api.access_token = "expired-access-token"
        api.refresh_token = "refresh-token"
        api._token_expires_at = 0

        with patch.object(api_module.aiohttp, "ClientSession", return_value=session):
            await api.get_gateway_id()

        refresh_payload = session.requests[0][2]
        self.assertEqual(refresh_payload["grant_type"], "refresh_token")
        self.assertEqual(refresh_payload["refresh_token"], "refresh-token")
        self.assertEqual(api.refresh_token, "refresh-token")
        self.assertEqual(
            session.requests[1][2]["Authorization"], "Bearer new-access-token"
        )

    async def test_unauthorized_request_refreshes_and_retries_once(self):
        session = FakeSession(
            post_responses=[
                FakeResponse(
                    200,
                    {"access_token": "new-access-token", "expires_in": 3600},
                )
            ],
            get_responses=[
                FakeResponse(401, {}),
                FakeResponse(200, [{"system": {"id": "system-1"}}]),
            ],
        )
        api = make_api("https://api.gridx.de")
        api.access_token = "rejected-access-token"
        api.refresh_token = "refresh-token"
        api._token_expires_at = float("inf")

        with patch.object(api_module.aiohttp, "ClientSession", return_value=session):
            await api.get_gateway_id()

        get_requests = [request for request in session.requests if request[0] == "GET"]
        self.assertEqual(len(get_requests), 2)
        self.assertEqual(
            get_requests[0][2]["Authorization"], "Bearer rejected-access-token"
        )
        self.assertEqual(
            get_requests[1][2]["Authorization"], "Bearer new-access-token"
        )

    async def test_rejected_refresh_falls_back_to_password_login(self):
        session = FakeSession(
            post_responses=[
                FakeResponse(403, {}),
                FakeResponse(
                    200,
                    {
                        "access_token": "password-login-token",
                        "refresh_token": "replacement-refresh-token",
                        "expires_in": 3600,
                    },
                ),
            ],
            get_responses=[FakeResponse(200, [{"system": {"id": "system-1"}}])],
        )
        api = make_api("https://api.gridx.de")
        api.access_token = "expired-access-token"
        api.refresh_token = "rejected-refresh-token"
        api._token_expires_at = 0

        with patch.object(api_module.aiohttp, "ClientSession", return_value=session):
            await api.get_gateway_id()

        post_requests = [
            request for request in session.requests if request[0] == "POST"
        ]
        self.assertEqual(post_requests[0][2]["grant_type"], "refresh_token")
        self.assertEqual(
            post_requests[1][2]["grant_type"],
            "http://auth0.com/oauth/grant-type/password-realm",
        )
        self.assertEqual(api.access_token, "password-login-token")


if __name__ == "__main__":
    import unittest

    unittest.main()
