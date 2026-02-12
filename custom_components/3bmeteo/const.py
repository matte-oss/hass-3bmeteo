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
    # Clear/Sunny conditions
    1: "sunny",
    2: "sunny",
    3: "partlycloudy",  # poco nuvoloso
    4: "rainy",
    5: "sunny",
    6: "partlycloudy",  # velature sparse
    7: "cloudy",  # nubi sparse
    8: "rainy",  # pioggia e schiarite
    9: "rainy",
    10: "rainy",
    11: "cloudy",
    12: "cloudy",
    13: "cloudy",
    14: "cloudy",
    15: "cloudy",  # nuvoloso
    16: "cloudy",
    17: "cloudy",
    18: "cloudy",
    19: "rainy",
    20: "rainy",
    21: "rainy",
    22: "rainy",
    23: "pouring",  # pioggia intensa
    24: "pouring",
    25: "pouring",
    26: "pouring",
    27: "lightning-rainy",
    28: "lightning-rainy",  # temporale
    29: "lightning-rainy",
    30: "snowy",
    31: "snowy",
    32: "snowy",
    33: "snowy",
    34: "snowy",
    35: "snowy-rainy",
    36: "snowy-rainy",
    37: "snowy-rainy",
    38: "partlycloudy",  # nubi basse e schiarite
    39: "hail",
    40: "fog",
    41: "fog",
    42: "fog",
    43: "partlycloudy",  # parz nuvoloso
    44: "partlycloudy",
    45: "rainy",  # nubi sparse e rovesci
    46: "rainy",
    47: "rainy",
    48: "rainy",
    49: "rainy",
    50: "rainy",
    51: "partlycloudy",
    52: "cloudy",
    53: "cloudy",
    54: "cloudy",
    55: "cloudy",
    56: "cloudy",
    57: "cloudy",
    58: "cloudy",
    59: "cloudy",
    60: "rainy",
    61: "rainy",
    62: "rainy",
    63: "rainy",
    64: "rainy",
    65: "rainy",
    66: "rainy",
    67: "rainy",
    68: "rainy",
    69: "rainy",
    70: "pouring",
    71: "pouring",
    72: "pouring",
    73: "pouring",
    74: "pouring",
    75: "pouring",
    76: "lightning-rainy",
    77: "lightning-rainy",
    78: "lightning-rainy",
    79: "lightning-rainy",
    80: "rainy",
    81: "rainy",  # pioggia debole e schiarite
    82: "rainy",
    83: "rainy",
    84: "rainy",
    85: "rainy",
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


