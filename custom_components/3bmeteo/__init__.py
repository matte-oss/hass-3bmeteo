"""The 3BMeteo integration."""
from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import TrBMeteoApiClient
from .const import CONF_LOCATION_ID, CONF_LOCATION_NAME, CONF_SECTOR_ID, DOMAIN
from .coordinator import TrBMeteoDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.WEATHER]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up 3BMeteo from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    session = async_get_clientsession(hass)
    client = TrBMeteoApiClient(session)

    location_id = entry.data[CONF_LOCATION_ID]
    sector_id = entry.data.get(CONF_SECTOR_ID, 1)
    location_name = entry.data.get(CONF_LOCATION_NAME, f"Location {location_id}")

    coordinator = TrBMeteoDataUpdateCoordinator(
        hass,
        client,
        location_id,
        sector_id,
        location_name,
    )

    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
