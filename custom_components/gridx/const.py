from dataclasses import dataclass
from typing import Final


DOMAIN = "gridx"
PROJECT_URL = "https://github.com/markusschultheis/gridx-homeassistant"

CONF_PROVIDER = "provider"
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


@dataclass(frozen=True)
class Provider:
    """Authentication settings for a gridX-backed customer portal."""

    key: str
    label: str
    client_id: str
    realm: str


DEFAULT_PROVIDER: Final = "eon_home"

# Public Auth0 settings embedded in the multi-tenant gridX web application at
# https://homeone.gridx.de/. All providers use AUTH_URL, DEFAULT_AUDIENCE and
# AUTH_SCOPE; only client_id and realm differ. Internal gridX POC realms are
# intentionally excluded.
PROVIDERS: Final[dict[str, Provider]] = {
    "1komma5grad": Provider(
        key="1komma5grad",
        label="1KOMMA5°",
        client_id="CrqUiQt6VhwOgWHqkX40CgYNlhABF3dB",
        realm="1komma5grad-authentication-db",
    ),
    "bdl_next": Provider(
        key="bdl_next",
        label="Bdl Next",
        client_id="xVDQkuyCK9gRm4Di1uNAwpWjKLehUu1u",
        realm="bdl-next-authentication-db",
    ),
    "efa_home": Provider(
        key="efa_home",
        label="EFA-Home",
        client_id="VsgghMKZYiSku5OUo6B5MenBf8XmTA8z",
        realm="efa-home-authentication-db",
    ),
    "egs": Provider(
        key="egs",
        label="EGS",
        client_id="sBH1ahx8Bm5pqPbg21UEaG01Wiul46Lu",
        realm="egs-authentication-db",
    ),
    "empavo": Provider(
        key="empavo",
        label="empavo",
        client_id="SGi5e55lb4kPlx54sTwqmSx50agfGkkp",
        realm="empavo-authentication-db",
    ),
    "enviam": Provider(
        key="enviam",
        label="enviaM",
        client_id="ubZZBgnq9W9cNksekUuWWsw73bB3SVLv",
        realm="enviam-authentication-db",
    ),
    "eon_feh_nl": Provider(
        key="eon_feh_nl",
        label="E.ON FEH (Niederlande)",
        client_id="VpunLkvfSk0CYnfFeZPeceEPb88ihoEZ",
        realm="eon-feh-nl-authentication-db",
    ),
    "eon_home": Provider(
        key="eon_home",
        label="E.ON Home Manager",
        client_id=DEFAULT_CLIENT_ID,
        realm=DEFAULT_REALM,
    ),
    "evm": Provider(
        key="evm",
        label="EVM (Energieversorgung Mittelrhein)",
        client_id="63FyqwVC8z5s0Ej7fk4epfHhvr1rVJiD",
        realm="evm-authentication-db",
    ),
    "ewv": Provider(
        key="ewv",
        label="EWV (Energie- und Wasser-Versorgung)",
        client_id="0IYvvxIwlP4OxPF9PLwjZCem5U1yibgn",
        realm="ewv-authentication-db",
    ),
    "giedorf": Provider(
        key="giedorf",
        label="Giedorf",
        client_id="cUC6Lo5Rly2Vkx0KqwmPnb5KXGk8FK5R",
        realm="giedorf-authentication-db",
    ),
    "greenblocks": Provider(
        key="greenblocks",
        label="Greenblocks",
        client_id="EsfZCmULf0yhads5dwMNMEd5WFgEzeei",
        realm="greenblocks-authentication-db",
    ),
    "heimwatt": Provider(
        key="heimwatt",
        label="Heimwatt",
        client_id="EWf6tTifj13GK8GwrlnRkrKsMnh4LFLb",
        realm="heimwatt-authentication-db",
    ),
    "hemos": Provider(
        key="hemos",
        label="hemos",
        client_id="q9OlJhQGhkf0OzW356VLw6UzlR3qgWhh",
        realm="hemos-authentication-db",
    ),
    "ibc_homeone": Provider(
        key="ibc_homeone",
        label="IBC HomeOne Hub",
        client_id="F9aEJdfve0nL65yA0aWSdCwiWqDYIHgm",
        realm="ibc-homeone-authentication-db",
    ),
    "klarsolar": Provider(
        key="klarsolar",
        label="KlarSolar",
        client_id="48CcbpQ77QfqdSKkxsmFBl1yQTLZM219",
        realm="klarsolar-authentication-db",
    ),
    "lew": Provider(
        key="lew",
        label="LEW (Lechwerke)",
        client_id="4FDgJwNbBxwWBzvQHXjQqOsum8R7cKVR",
        realm="lew-authentication-db",
    ),
    "octopus": Provider(
        key="octopus",
        label="Octopus Energy",
        client_id="tBL5sAPBmZI2X9pA7lXX6rAiP7NXdOnu",
        realm="octopus-authentication-db",
    ),
    "pvgreen": Provider(
        key="pvgreen",
        label="PV Green",
        client_id="dbWuzhZqII1x0yX3SzzfHxsKxhZ91qzO",
        realm="pvgreen-authentication-db",
    ),
    "sonnen": Provider(
        key="sonnen",
        label="sonnen",
        client_id="Bcb0YhU9AhMvgEijBH0cb4vwLU5FwJ3M",
        realm="sonnen-authentication-db",
    ),
    "swnor": Provider(
        key="swnor",
        label="Stadtwerke Norderstedt",
        client_id="Ssg8OSIHDjquuyRKxIjBj6YWCfDcCyHj",
        realm="swnor-authentication-db",
    ),
    "upvolt": Provider(
        key="upvolt",
        label="upVolt",
        client_id="rcGfmimyTQONxjY3BAfUNvHMjI2RL4QD",
        realm="upvolt-authentication-db",
    ),
    "viessmann": Provider(
        key="viessmann",
        label="Viessmann GridBox (Legacy – Zugang eingestellt)",
        client_id="oZpr934Ikn8OZOHTJEcrgXkjio0I0Q7b",
        realm="viessmann-authentication-db",
    ),
    "zero_1": Provider(
        key="zero_1",
        label="Zero 1",
        client_id="7fMy9SJcViJzKqfcwYcjcgwMlbgbC7SH",
        realm="zero-1-authentication-db",
    ),
}


def provider_key_from_realm(realm: str | None) -> str | None:
    """Return the provider key matching an existing config entry realm."""
    if not realm:
        return None
    return next(
        (key for key, provider in PROVIDERS.items() if provider.realm == realm),
        None,
    )

# Token expiration offset (seconds before actual expiration to refresh)
TOKEN_EXPIRATION_OFFSET = 60
