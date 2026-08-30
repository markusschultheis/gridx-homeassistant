"""Known gridX-backed OEM provider profiles.

The public gridX HomeOne frontend is multi-tenant. OEM portals share the
Auth0 tenant and gridX API; ``client_id`` and ``realm`` select the tenant.
The identifiers below are public application configuration, not credentials.

Cross-checked against the public HomeOne provider inventory used by
lackas/ha-gridx on 2026-08-30.
"""

from __future__ import annotations

from dataclasses import dataclass

from .const import DEFAULT_AUDIENCE, GRIDX_ID_TOKEN_AUDIENCE

DEFAULT_PROVIDER = "eon_home"
CUSTOM_PROVIDER = "custom"


@dataclass(frozen=True, slots=True)
class GridXProvider:
    """Authentication profile for a gridX-backed OEM portal."""

    key: str
    label: str
    client_id: str
    realm: str
    audience: str = GRIDX_ID_TOKEN_AUDIENCE
    legacy: bool = False


PROVIDERS: dict[str, GridXProvider] = {
    "1komma5grad": GridXProvider(
        "1komma5grad",
        "1KOMMA5°",
        "CrqUiQt6VhwOgWHqkX40CgYNlhABF3dB",
        "1komma5grad-authentication-db",
    ),
    "bdl_next": GridXProvider(
        "bdl_next",
        "Bdl Next",
        "xVDQkuyCK9gRm4Di1uNAwpWjKLehUu1u",
        "bdl-next-authentication-db",
    ),
    "efa_home": GridXProvider(
        "efa_home",
        "EFA-Home",
        "VsgghMKZYiSku5OUo6B5MenBf8XmTA8z",
        "efa-home-authentication-db",
    ),
    "egs": GridXProvider(
        "egs",
        "EGS",
        "sBH1ahx8Bm5pqPbg21UEaG01Wiul46Lu",
        "egs-authentication-db",
    ),
    "empavo": GridXProvider(
        "empavo",
        "empavo",
        "SGi5e55lb4kPlx54sTwqmSx50agfGkkp",
        "empavo-authentication-db",
    ),
    "enviam": GridXProvider(
        "enviam",
        "enviaM",
        "ubZZBgnq9W9cNksekUuWWsw73bB3SVLv",
        "enviam-authentication-db",
    ),
    "eon_feh_nl": GridXProvider(
        "eon_feh_nl",
        "E.ON FEH (NL)",
        "VpunLkvfSk0CYnfFeZPeceEPb88ihoEZ",
        "eon-feh-nl-authentication-db",
    ),
    "eon_home": GridXProvider(
        "eon_home",
        "E.ON Home Manager",
        "mG0Phmo7DmnvAqO7p6B0WOYBODppY3cc",
        "eon-home-authentication-db",
        audience=DEFAULT_AUDIENCE,
    ),
    "evm": GridXProvider(
        "evm",
        "EVM",
        "63FyqwVC8z5s0Ej7fk4epfHhvr1rVJiD",
        "evm-authentication-db",
    ),
    "ewv": GridXProvider(
        "ewv",
        "EWV",
        "0IYvvxIwlP4OxPF9PLwjZCem5U1yibgn",
        "ewv-authentication-db",
    ),
    "giedorf": GridXProvider(
        "giedorf",
        "Giedorf",
        "cUC6Lo5Rly2Vkx0KqwmPnb5KXGk8FK5R",
        "giedorf-authentication-db",
    ),
    "greenblocks": GridXProvider(
        "greenblocks",
        "Greenblocks",
        "EsfZCmULf0yhads5dwMNMEd5WFgEzeei",
        "greenblocks-authentication-db",
    ),
    "heimwatt": GridXProvider(
        "heimwatt",
        "Heimwatt",
        "EWf6tTifj13GK8GwrlnRkrKsMnh4LFLb",
        "heimwatt-authentication-db",
    ),
    "hemos": GridXProvider(
        "hemos",
        "hemos",
        "q9OlJhQGhkf0OzW356VLw6UzlR3qgWhh",
        "hemos-authentication-db",
    ),
    "ibc_homeone": GridXProvider(
        "ibc_homeone",
        "IBC HomeOne Hub",
        "F9aEJdfve0nL65yA0aWSdCwiWqDYIHgm",
        "ibc-homeone-authentication-db",
    ),
    "klarsolar": GridXProvider(
        "klarsolar",
        "KlarSolar",
        "48CcbpQ77QfqdSKkxsmFBl1yQTLZM219",
        "klarsolar-authentication-db",
    ),
    "lew": GridXProvider(
        "lew",
        "LEW (Lechwerke)",
        "4FDgJwNbBxwWBzvQHXjQqOsum8R7cKVR",
        "lew-authentication-db",
    ),
    "octopus": GridXProvider(
        "octopus",
        "Octopus Energy",
        "tBL5sAPBmZI2X9pA7lXX6rAiP7NXdOnu",
        "octopus-authentication-db",
    ),
    "pvgreen": GridXProvider(
        "pvgreen",
        "PV Green",
        "dbWuzhZqII1x0yX3SzzfHxsKxhZ91qzO",
        "pvgreen-authentication-db",
    ),
    "sonnen": GridXProvider(
        "sonnen",
        "sonnen",
        "Bcb0YhU9AhMvgEijBH0cb4vwLU5FwJ3M",
        "sonnen-authentication-db",
    ),
    "swnor": GridXProvider(
        "swnor",
        "Stadtwerke Norderstedt",
        "Ssg8OSIHDjquuyRKxIjBj6YWCfDcCyHj",
        "swnor-authentication-db",
    ),
    "upvolt": GridXProvider(
        "upvolt",
        "upVolt",
        "rcGfmimyTQONxjY3BAfUNvHMjI2RL4QD",
        "upvolt-authentication-db",
    ),
    "viessmann": GridXProvider(
        "viessmann",
        "Viessmann GridBox (Legacy)",
        "oZpr934Ikn8OZOHTJEcrgXkjio0I0Q7b",
        "viessmann-authentication-db",
        legacy=True,
    ),
    "zero_1": GridXProvider(
        "zero_1",
        "Zero 1",
        "7fMy9SJcViJzKqfcwYcjcgwMlbgbC7SH",
        "zero-1-authentication-db",
    ),
}


def get_provider(key: str | None) -> GridXProvider | None:
    """Return a known provider profile or ``None`` for custom/unknown keys."""

    if not key or key == CUSTOM_PROVIDER:
        return None
    return PROVIDERS.get(key)


def provider_from_auth(client_id: str | None, realm: str | None) -> str:
    """Map legacy explicit Auth0 settings to a known provider key when possible."""

    for key, provider in PROVIDERS.items():
        if provider.client_id == client_id and provider.realm == realm:
            return key
    return CUSTOM_PROVIDER


def provider_choices() -> dict[str, str]:
    """Return providers offered for new setup plus an explicit custom option."""

    active = sorted(
        (provider for provider in PROVIDERS.values() if not provider.legacy),
        key=lambda provider: provider.label.casefold(),
    )
    choices = {provider.key: provider.label for provider in active}
    choices[CUSTOM_PROVIDER] = "Benutzerdefiniertes gridX-Profil"
    return choices
