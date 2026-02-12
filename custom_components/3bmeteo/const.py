"""Constants for the 3BMeteo integration."""
from __future__ import annotations

from typing import Final

DOMAIN: Final = "3bmeteo"
DEFAULT_NAME: Final = "3BMeteo"

# API Configuration
API_BASE_URL: Final = "https://api.3bmeteo.com"
API_KEY: Final = "TVIBVd7cmCagdU3uob6Mof1hI9yM48scSSYZVrnw"

# Config Keys
CONF_LOCATION_ID: Final = "location_id"
CONF_LOCATION_NAME: Final = "location_name"
CONF_SECTOR_ID: Final = "sector_id"

# Update interval in minutes
UPDATE_INTERVAL: Final = 30

# Weather symbol ID to Home Assistant condition mapping
# Based on 3bmeteo symbol IDs observed in the API response
CONDITION_MAP: Final[dict[int, str]] = {
    1: "sunny",  # sereno
    2: "sunny",  # MISSING - sereno (variant)
    3: "partlycloudy",  # poco nuvoloso
    4: "partlycloudy",  # nubi sparse
    5: "lightning-rainy",  # possibili temporali
    6: "partlycloudy",  # velature sparse
    7: "partlycloudy",  # nubi sparse
    8: "rainy",  # pioggia debole e schiarite
    9: "lightning-rainy",  # nubi sparse e temporali
    10: "lightning-rainy",  # possibili temporali
    11: "lightning-rainy",  # MISSING - temporale forte e schiarite
    12: "cloudy",  # nuvoloso
    13: "snowy",  # nubi sparse e neve
    14: "partlycloudy",  # velature lievi
    15: "partlycloudy",  # velature estese
    16: "cloudy",  # coperto per nubi alte
    17: "cloudy",  # coperto
    18: "exceptional",  # gelicidio (freezing rain/ice)
    19: "rainy",  # pioviggine
    20: "rainy",  # pioggia debole
    21: "rainy",  # pioggia debole
    22: "rainy",  # MISSING - pioggia (variant)
    23: "rainy",  # pioggia
    24: "pouring",  # pioggia forte
    25: "pouring",  # pioggia molto forte
    26: "rainy",  # rovesci di pioggia
    27: "lightning-rainy",  # temporale forte
    28: "lightning-rainy",  # temporale
    29: "hail",  # temporale con grandine ✓ FOUND!
    30: "snowy",  # MISSING - temporale di neve
    31: "snowy-rainy",  # pioggia e neve
    32: "snowy-rainy",  # nevischio
    33: "snowy",  # neve debole
    34: "snowy",  # neve
    35: "snowy",  # neve
    36: "snowy",  # neve forte
    37: "snowy",  # MISSING - neve (variant)
    38: "partlycloudy",  # nubi basse e schiarite
    39: "cloudy",  # nubi basse
    40: "fog",  # nebbia a banchi
    41: "fog",  # nebbia
    42: "fog",  # MISSING - nebbia (variant)
    43: "partlycloudy",  # parz nuvoloso
    44: "fog",  # foschia
    45: "rainy",  # nubi sparse e rovesci
    46: "pouring",  # MISSING - rovesci forti
    47: "snowy",  # rovesci di neve
    48: "snowy-rainy",  # pioggia e neve
    49: "partlycloudy",  # MISSING - parzialmente nuvoloso (variant)
    50: "sunny",  # sereno
}

# Wind direction mapping
WIND_DIRECTION_MAP: Final[dict[str, float]] = {
    "N": 0,
    "NNE": 22.5,
    "NE": 45,
    "ENE": 67.5,
    "E": 90,
    "ESE": 112.5,
    "SE": 135,
    "SSE": 157.5,
    "S": 180,
    "SSO": 202.5,
    "SSW": 202.5,
    "SO": 225,
    "SW": 225,
    "OSO": 247.5,
    "WSW": 247.5,
    "O": 270,
    "W": 270,
    "ONO": 292.5,
    "WNW": 292.5,
    "NO": 315,
    "NW": 315,
    "NNO": 337.5,
    "NNW": 337.5,
}



