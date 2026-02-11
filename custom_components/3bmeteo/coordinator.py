"""Data coordinator for 3BMeteo."""
from __future__ import annotations

from datetime import timedelta
import logging
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import TrBMeteoApiClient, TrBMeteoApiError
from .const import DOMAIN, UPDATE_INTERVAL

_LOGGER = logging.getLogger(__name__)


class TrBMeteoDataUpdateCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Class to manage fetching 3BMeteo data."""

    def __init__(
        self,
        hass: HomeAssistant,
        client: TrBMeteoApiClient,
        location_id: int,
        sector_id: int,
        location_name: str,
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{location_name}",
            update_interval=timedelta(minutes=UPDATE_INTERVAL),
        )
        self._client = client
        self._location_id = location_id
        self._sector_id = sector_id
        self._location_name = location_name

    @property
    def location_id(self) -> int:
        """Return the location ID."""
        return self._location_id

    @property
    def sector_id(self) -> int:
        """Return the sector ID."""
        return self._sector_id

    @property
    def location_name(self) -> str:
        """Return the location name."""
        return self._location_name

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from API."""
        try:
            # Fetch both daily and hourly forecasts
            daily_data = await self._client.get_weather(self._location_id, self._sector_id)
            if "localita" not in daily_data:
                raise UpdateFailed("Invalid response from API: missing localita")
            
            # Fetch hourly forecast (2 days)
            try:
                hourly_data = await self._client.get_hourly_forecast(
                    self._location_id, self._sector_id, days=2
                )
                # Merge hourly data into the response
                if "localita" in hourly_data and "previsione_giorno" in hourly_data["localita"]:
                    daily_data["hourly_forecast"] = hourly_data["localita"]["previsione_giorno"]
            except TrBMeteoApiError as err:
                _LOGGER.warning("Failed to fetch hourly forecast: %s", err)
                daily_data["hourly_forecast"] = []
            
            return daily_data
        except TrBMeteoApiError as err:
            raise UpdateFailed(f"Error communicating with API: {err}") from err
