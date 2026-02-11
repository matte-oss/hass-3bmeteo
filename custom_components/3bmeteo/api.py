"""API client for 3BMeteo."""
from __future__ import annotations

import logging
from typing import Any

import aiohttp

from .const import API_BASE_URL, API_KEY

_LOGGER = logging.getLogger(__name__)


class TrBMeteoApiError(Exception):
    """Exception for API errors."""


class TrBMeteoApiClient:
    """API client for 3BMeteo weather service."""

    def __init__(self, session: aiohttp.ClientSession) -> None:
        """Initialize the API client."""
        self._session = session

    async def get_weather(
        self, location_id: int, sector_id: int, language: str = "it"
    ) -> dict[str, Any]:
        """Get weather data for a location.

        Args:
            location_id: The 3bmeteo location ID
            sector_id: The sector ID for the location
            language: Language code (default: it)

        Returns:
            Weather data dictionary

        Raises:
            TrBMeteoApiError: If the API request fails
        """
        url = (
            f"{API_BASE_URL}/mobilev3/api_previsioni/home/"
            f"{location_id}/{sector_id}/{language}/1/1"
        )
        params = {
            "format": "json2",
            "X-API-KEY": API_KEY,
        }
        headers = {
            "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 13)",
            "Accept-Encoding": "gzip,deflate",
        }

        try:
            async with self._session.get(
                url, params=params, headers=headers, timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                if response.status != 200:
                    raise TrBMeteoApiError(
                        f"API request failed with status {response.status}"
                    )
                data = await response.json()
                return data
        except aiohttp.ClientError as err:
            raise TrBMeteoApiError(f"Error connecting to API: {err}") from err
        except Exception as err:
            raise TrBMeteoApiError(f"Unexpected error: {err}") from err

    async def get_hourly_forecast(
        self, location_id: int, sector_id: int, language: str = "it", days: int = 2
    ) -> dict[str, Any]:
        """Get hourly forecast data for a location.

        Args:
            location_id: The 3bmeteo location ID
            sector_id: The sector ID for the location
            language: Language code (default: it)
            days: Number of days to fetch (default: 2)

        Returns:
            Hourly forecast data dictionary

        Raises:
            TrBMeteoApiError: If the API request fails
        """
        url = (
            f"{API_BASE_URL}/mobilev3/api_previsioni/orario/"
            f"{location_id}/{sector_id}/0/{days}/{language}/"
        )
        params = {
            "format": "json2",
            "X-API-KEY": API_KEY,
        }
        headers = {
            "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 13)",
            "Accept-Encoding": "gzip,deflate",
        }

        try:
            async with self._session.get(
                url, params=params, headers=headers, timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                if response.status != 200:
                    raise TrBMeteoApiError(
                        f"API request failed with status {response.status}"
                    )
                data = await response.json()
                return data
        except aiohttp.ClientError as err:
            raise TrBMeteoApiError(f"Error connecting to API: {err}") from err
        except Exception as err:
            raise TrBMeteoApiError(f"Unexpected error: {err}") from err

    async def search_location(self, query: str, language: str = "it") -> list[dict[str, Any]]:
        """Search for a location by name.

        Args:
            query: Location name to search for
            language: Language code (default: it)

        Returns:
            List of matching locations

        Raises:
            TrBMeteoApiError: If the API request fails
        """
        # Endpoint: /mobilev3/api_localita/ricerca_elastic_search/{query}/{lang}/{country}/offset/limit
        url = (
            f"{API_BASE_URL}/mobilev3/api_localita/ricerca_elastic_search/"
            f"{query}/{language}/it/0/20"
        )
        params = {
            "format": "json2",
            "X-API-KEY": API_KEY,
        }
        headers = {
            "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 13)",
            "Accept-Encoding": "gzip,deflate",
        }

        try:
            async with self._session.get(
                url, params=params, headers=headers, timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                if response.status != 200:
                    raise TrBMeteoApiError(
                        f"API request failed with status {response.status}"
                    )
                data = await response.json()
                # Response format: {"localita": [...]}
                if isinstance(data, dict) and "localita" in data:
                    return data["localita"] if isinstance(data["localita"], list) else [data["localita"]]
                elif isinstance(data, list):
                    return data
                return []
        except aiohttp.ClientError as err:
            raise TrBMeteoApiError(f"Error connecting to API: {err}") from err
        except Exception as err:
            raise TrBMeteoApiError(f"Unexpected error: {err}") from err

    async def validate_location(self, location_id: int, sector_id: int) -> bool:
        """Validate that a location exists and returns data.

        Args:
            location_id: The 3bmeteo location ID
            sector_id: The sector ID

        Returns:
            True if location is valid
        """
        try:
            data = await self.get_weather(location_id, sector_id)
            return "localita" in data
        except TrBMeteoApiError:
            return False
