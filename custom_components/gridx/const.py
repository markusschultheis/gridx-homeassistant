DOMAIN = "gridx"
PROJECT_URL = "https://github.com/markusschultheis/gridx-homeassistant"

CONF_PROVIDER = "provider"
CONF_CLIENT_ID = "client_id"
CONF_REALM = "realm"
CONF_AUDIENCE = "audience"

# Backward-compatible E.ON Home defaults for legacy entries without provider metadata.
DEFAULT_CLIENT_ID = "mG0Phmo7DmnvAqO7p6B0WOYBODppY3cc"
DEFAULT_REALM = "eon-home-authentication-db"
DEFAULT_AUDIENCE = "https://api.gridx.de"

# `my.gridx` is legacy for the migrated E.ON Home profile, but it is still the
# audience used by the current public multi-OEM implementation in lackas/ha-gridx.
# Keep the historical name as an alias because existing tests/config migration
# code already imports it.
GRIDX_ID_TOKEN_AUDIENCE = "my.gridx"
LEGACY_AUDIENCE = GRIDX_ID_TOKEN_AUDIENCE

AUTH_URL = "https://gridx.eu.auth0.com/oauth/token"
GATEWAYS_URL = "https://api.gridx.de/gateways"
LIVE_URL = "https://api.gridx.de/systems/{}/live"

GRANT_TYPE = "http://auth0.com/oauth/grant-type/password-realm"
REFRESH_GRANT_TYPE = "refresh_token"
AUTH_SCOPE = "email openid offline_access"

# Token expiration offset (seconds before actual expiration to refresh)
TOKEN_EXPIRATION_OFFSET = 60
