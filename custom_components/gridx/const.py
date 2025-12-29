DOMAIN = "gridx"

CONF_CLIENT_ID = "client_id"
CONF_REALM = "realm"
CONF_AUDIENCE = "audience"

AUTH_URL = "https://gridx.eu.auth0.com/oauth/token"
GATEWAYS_URL = "https://api.gridx.de/gateways"
LIVE_URL = "https://api.gridx.de/systems/{}/live"

GRANT_TYPE = "http://auth0.com/oauth/grant-type/password-realm"

# Token expiration offset (seconds before actual expiration to refresh)
TOKEN_EXPIRATION_OFFSET = 52200

# Data storage keys
DATA_EXPIRES_AT = "expires_at"
DATA_ID_TOKEN = "id_token"
