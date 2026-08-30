DOMAIN = "gridx"

CONF_CLIENT_ID = "client_id"
CONF_REALM = "realm"
CONF_AUDIENCE = "audience"

DEFAULT_CLIENT_ID = "mG0Phmo7DmnvAqO7p6B0WOYBODppY3cc"
DEFAULT_REALM = "eon-home-authentication-db"
DEFAULT_AUDIENCE = "https://api.gridx.de"
LEGACY_AUDIENCE = "my.gridx"

AUTH_URL = "https://gridx.eu.auth0.com/oauth/token"
GATEWAYS_URL = "https://api.gridx.de/gateways"
LIVE_URL = "https://api.gridx.de/systems/{}/live"

GRANT_TYPE = "http://auth0.com/oauth/grant-type/password-realm"
REFRESH_GRANT_TYPE = "refresh_token"
AUTH_SCOPE = "email openid offline_access"

# Token expiration offset (seconds before actual expiration to refresh)
TOKEN_EXPIRATION_OFFSET = 60
