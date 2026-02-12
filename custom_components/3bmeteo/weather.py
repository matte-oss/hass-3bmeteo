"""Weather platform for 3BMeteo integration."""
from __future__ import annotations

from datetime import datetime
import logging
from typing import Any

from homeassistant.components.weather import (
    ATTR_FORECAST_CONDITION,
    ATTR_FORECAST_NATIVE_PRECIPITATION,
    ATTR_FORECAST_NATIVE_TEMP,
    ATTR_FORECAST_NATIVE_TEMP_LOW,
    ATTR_FORECAST_NATIVE_WIND_SPEED,
    ATTR_FORECAST_PRECIPITATION_PROBABILITY,
    ATTR_FORECAST_TIME,
    ATTR_FORECAST_WIND_BEARING,
    Forecast,
    WeatherEntity,
    WeatherEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    UnitOfPressure,
    UnitOfSpeed,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    CONDITION_MAP,
    CONF_LOCATION_ID,
    CONF_LOCATION_NAME,
    DOMAIN,
    WIND_DIRECTION_MAP,
)
from .coordinator import TrBMeteoDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up 3BMeteo weather platform."""
    coordinator: TrBMeteoDataUpdateCoordinator = hass.data[DOMAIN][config_entry.entry_id]
    
    async_add_entities([TrBMeteoWeatherEntity(coordinator, config_entry)])


class TrBMeteoWeatherEntity(CoordinatorEntity[TrBMeteoDataUpdateCoordinator], WeatherEntity):
    """Implementation of a 3BMeteo weather entity."""

    _attr_has_entity_name = True
    _attr_name = None
    _attr_native_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_native_pressure_unit = UnitOfPressure.HPA
    _attr_native_wind_speed_unit = UnitOfSpeed.KILOMETERS_PER_HOUR
    _attr_supported_features = (
        WeatherEntityFeature.FORECAST_DAILY | WeatherEntityFeature.FORECAST_HOURLY
    )

    def __init__(
        self,
        coordinator: TrBMeteoDataUpdateCoordinator,
        config_entry: ConfigEntry,
    ) -> None:
        """Initialize the weather entity."""
        super().__init__(coordinator)
        
        self._config_entry = config_entry
        self._location_id = config_entry.data[CONF_LOCATION_ID]
        self._location_name = config_entry.data[CONF_LOCATION_NAME]
        
        self._attr_unique_id = f"{DOMAIN}_{self._location_id}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, str(self._location_id))},
            name=self._location_name,
            manufacturer="3BMeteo",
            model="Weather Forecast",
            entry_type=DeviceEntryType.SERVICE,
        )

    @property
    def _location_data(self) -> dict[str, Any] | None:
        """Return location data from coordinator."""
        if self.coordinator.data:
            return self.coordinator.data.get("localita")
        return None

    @property
    def _current_forecast(self) -> dict[str, Any] | None:
        """Return current day forecast data."""
        location = self._location_data
        if location and "previsione_giorno" in location:
            forecasts = location["previsione_giorno"]
            if forecasts:
                return forecasts[0]
        return None

    @property
    def _current_hourly(self) -> dict[str, Any] | None:
        """Return current hourly data."""
        from datetime import datetime
        
        if not self.coordinator.data:
            return None
            
        # Try to get hourly data from the dedicated hourly endpoint
        hourly_days = self.coordinator.data.get("hourly_forecast", [])
        if hourly_days:
            now = datetime.now()
            current_date = now.strftime("%Y-%m-%d")
            current_hour = now.hour
            
            for day_data in hourly_days:
                if day_data.get("data") == current_date:
                    hourly_list = day_data.get("previsione_oraria", [])
                    # Find the closest hour
                    for hourly in hourly_list:
                        if hourly.get("ora") == current_hour:
                            return hourly
                    # If exact hour not found, return the first one from today
                    if hourly_list:
                        return hourly_list[0]
        
        # Fallback to old method
        forecast = self._current_forecast
        if forecast and "previsione_oraria" in forecast:
            hourly = forecast["previsione_oraria"]
            if hourly:
                return hourly[0]
        return None

    def _get_condition(self, symbol_id: int | None, is_night: bool = False) -> str | None:
        """Map 3bmeteo symbol ID to Home Assistant condition.
        
        Args:
            symbol_id: The 3BMeteo weather symbol ID
            is_night: Whether it's nighttime (default: False)
            
        Returns:
            Home Assistant weather condition string
        """
        if symbol_id is None:
            return None
        condition = CONDITION_MAP.get(symbol_id, "cloudy")
        # Map sunny to clear-night during nighttime
        if condition == "sunny" and is_night:
            return "clear-night"
        return condition

    def _get_wind_bearing(self, direction: str | None) -> float | None:
        """Convert wind direction string to bearing."""
        if direction is None:
            return None
        return WIND_DIRECTION_MAP.get(direction.upper())

    @property
    def condition(self) -> str | None:
        """Return the current condition."""
        # Check if we have hourly data with notte field
        hourly = self._current_hourly
        if hourly:
            notte = hourly.get("notte")
            is_night = False
            if notte is not None:
                try:
                    is_night = int(notte) == 1
                except (ValueError, TypeError):
                    pass
            # Try to get symbol from hourly data
            symbol_id = hourly.get("id_simbolo")
            if symbol_id:
                try:
                    symbol_int = int(symbol_id)
                    condition = self._get_condition(symbol_int, is_night)
                    _LOGGER.debug("Current condition: symbol %s (night=%s) mapped to %s", symbol_id, is_night, condition)
                    return condition
                except (ValueError, TypeError) as e:
                    _LOGGER.warning("Failed to convert symbol_id '%s' to int: %s", symbol_id, e)
        
        # Fallback to daily forecast (don't use nighttime flag for daily forecast)
        forecast = self._current_forecast
        if forecast:
            tempo = forecast.get("tempo_medio", {})
            symbol_id = tempo.get("id_simbolo")
            if symbol_id:
                try:
                    symbol_int = int(symbol_id)
                    condition = self._get_condition(symbol_int, is_night=False)
                    _LOGGER.debug("Current condition: symbol %s mapped to %s", symbol_id, condition)
                    return condition
                except (ValueError, TypeError) as e:
                    _LOGGER.warning("Failed to convert symbol_id '%s' to int: %s", symbol_id, e)
        return None

    @property
    def native_temperature(self) -> float | None:
        """Return the current temperature."""
        hourly = self._current_hourly
        if hourly:
            temp_data = hourly.get("temperatura", {})
            if isinstance(temp_data, dict):
                return temp_data.get("gradi")
            return temp_data
        
        # Fallback to average of min/max
        forecast = self._current_forecast
        if forecast:
            tempo = forecast.get("tempo_medio", {})
            t_min = tempo.get("t_min")
            t_max = tempo.get("t_max")
            if t_min is not None and t_max is not None:
                return (t_min + t_max) / 2
        return None

    @property
    def native_apparent_temperature(self) -> float | None:
        """Return the apparent/feels-like temperature."""
        hourly = self._current_hourly
        if hourly:
            return hourly.get("tpercepita") or hourly.get("windchill")
        return None

    @property
    def humidity(self) -> int | None:
        """Return the humidity."""
        hourly = self._current_hourly
        if hourly:
            hr = hourly.get("hr")
            if hr is not None:
                try:
                    return int(hr)
                except (ValueError, TypeError):
                    pass
        
        # Fallback to daily
        forecast = self._current_forecast
        if forecast:
            tempo = forecast.get("tempo_medio", {})
            return tempo.get("hr")
        return None

    @property
    def native_pressure(self) -> float | None:
        """Return the pressure."""
        hourly = self._current_hourly
        if hourly:
            return hourly.get("pr")
        
        forecast = self._current_forecast
        if forecast:
            tempo = forecast.get("tempo_medio", {})
            return tempo.get("pr")
        return None

    @property
    def native_wind_speed(self) -> float | None:
        """Return the wind speed."""
        hourly = self._current_hourly
        if hourly:
            vento = hourly.get("vento", {})
            if vento:
                intensita = vento.get("intensita")
                if intensita:
                    try:
                        return float(intensita)
                    except (ValueError, TypeError):
                        pass
        
        forecast = self._current_forecast
        if forecast:
            tempo = forecast.get("tempo_medio", {})
            vento = tempo.get("vento", {})
            if vento:
                intensita = vento.get("intensita")
                if intensita:
                    try:
                        return float(intensita)
                    except (ValueError, TypeError):
                        pass
        return None

    @property
    def wind_bearing(self) -> float | None:
        """Return the wind bearing."""
        hourly = self._current_hourly
        if hourly:
            vento = hourly.get("vento", {})
            if vento:
                return self._get_wind_bearing(vento.get("direzione"))
        
        forecast = self._current_forecast
        if forecast:
            tempo = forecast.get("tempo_medio", {})
            vento = tempo.get("vento", {})
            if vento:
                return self._get_wind_bearing(vento.get("direzione"))
        return None

    @property
    def native_wind_gust_speed(self) -> float | None:
        """Return the wind gust speed."""
        hourly = self._current_hourly
        if hourly:
            return hourly.get("raffica")
        
        forecast = self._current_forecast
        if forecast:
            tempo = forecast.get("tempo_medio", {})
            return tempo.get("raffica")
        return None

    @property
    def attribution(self) -> str:
        """Return the attribution."""
        return "Data provided by 3BMeteo"

    async def async_forecast_daily(self) -> list[Forecast] | None:
        """Return the daily forecast."""
        location = self._location_data
        if not location:
            return None
        
        forecasts = location.get("previsione_giorno", [])
        if not forecasts:
            return None

        result: list[Forecast] = []
        for day_forecast in forecasts:
            tempo = day_forecast.get("tempo_medio", {})
            data = day_forecast.get("data")
            
            if not data:
                continue

            vento = tempo.get("vento", {})
            symbol_id = tempo.get("id_simbolo")
            
            condition = None
            if symbol_id:
                try:
                    symbol_int = int(symbol_id)
                    condition = self._get_condition(symbol_int)
                    _LOGGER.debug("Daily forecast for %s: symbol %s mapped to %s", data, symbol_id, condition)
                except (ValueError, TypeError) as e:
                    _LOGGER.warning("Failed to convert symbol_id '%s' to int for date %s: %s", symbol_id, data, e)

            forecast: Forecast = {
                ATTR_FORECAST_TIME: f"{data}T00:00:00",
                ATTR_FORECAST_CONDITION: condition,
                ATTR_FORECAST_NATIVE_TEMP: tempo.get("t_max"),
                ATTR_FORECAST_NATIVE_TEMP_LOW: tempo.get("t_min"),
                ATTR_FORECAST_PRECIPITATION_PROBABILITY: tempo.get("probabilita_prec"),
                ATTR_FORECAST_NATIVE_PRECIPITATION: tempo.get("precipitazioni"),
            }

            if vento:
                try:
                    wind_speed = float(vento.get("intensita", 0))
                    forecast[ATTR_FORECAST_NATIVE_WIND_SPEED] = wind_speed
                except (ValueError, TypeError):
                    pass
                forecast[ATTR_FORECAST_WIND_BEARING] = self._get_wind_bearing(
                    vento.get("direzione")
                )

            result.append(forecast)

        return result

    async def async_forecast_hourly(self) -> list[Forecast] | None:
        """Return the hourly forecast."""
        if not self.coordinator.data:
            return None

        # Get hourly forecasts from the dedicated hourly endpoint
        hourly_days = self.coordinator.data.get("hourly_forecast", [])
        
        result: list[Forecast] = []

        for day_data in hourly_days:
            date_str = day_data.get("data", "")
            hourly_list = day_data.get("previsione_oraria", [])
            
            for hourly in hourly_list:
                ora = hourly.get("ora")
                if ora is None:
                    continue

                temp_data = hourly.get("temperatura", {})
                if isinstance(temp_data, dict):
                    temperature = temp_data.get("gradi")
                else:
                    temperature = temp_data

                vento = hourly.get("vento", {})
                symbol_id = hourly.get("id_simbolo")
                
                # Check if it's nighttime
                is_night = False
                notte = hourly.get("notte")
                if notte is not None:
                    try:
                        is_night = int(notte) == 1
                    except (ValueError, TypeError):
                        pass
                
                condition = None
                if symbol_id:
                    try:
                        symbol_int = int(symbol_id)
                        condition = self._get_condition(symbol_int, is_night)
                        _LOGGER.debug("Hourly forecast for %s %02d:00: symbol %s (night=%s) mapped to %s", date_str, ora, symbol_id, is_night, condition)
                    except (ValueError, TypeError) as e:
                        _LOGGER.warning("Failed to convert symbol_id '%s' to int for %s %02d:00: %s", symbol_id, date_str, ora, e)

                forecast: Forecast = {
                    ATTR_FORECAST_TIME: f"{date_str}T{ora:02d}:00:00",
                    ATTR_FORECAST_CONDITION: condition,
                    ATTR_FORECAST_NATIVE_TEMP: temperature,
                    ATTR_FORECAST_PRECIPITATION_PROBABILITY: hourly.get("probabilita_prec"),
                    ATTR_FORECAST_NATIVE_PRECIPITATION: hourly.get("precipitazioni"),
                }

                if vento:
                    try:
                        wind_speed = float(vento.get("intensita", 0))
                        forecast[ATTR_FORECAST_NATIVE_WIND_SPEED] = wind_speed
                    except (ValueError, TypeError):
                        pass
                    forecast[ATTR_FORECAST_WIND_BEARING] = self._get_wind_bearing(
                        vento.get("direzione")
                    )

                result.append(forecast)

        return result if result else None
