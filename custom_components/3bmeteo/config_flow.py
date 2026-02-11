"""Config flow for 3BMeteo integration."""
from __future__ import annotations

import logging
from typing import Any

import aiohttp
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import TrBMeteoApiClient, TrBMeteoApiError
from .const import (
    CONF_LOCATION_ID,
    CONF_LOCATION_NAME,
    CONF_SECTOR_ID,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


class TrBMeteoConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for 3BMeteo."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._locations: list[dict[str, Any]] = []

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            search_query = user_input.get("location_search", "").strip()
            
            if search_query:
                session = async_get_clientsession(self.hass)
                client = TrBMeteoApiClient(session)
                
                try:
                    locations = await client.search_location(search_query)
                    if locations:
                        self._locations = locations
                        return await self.async_step_select_location()
                    else:
                        errors["base"] = "no_results"
                except TrBMeteoApiError:
                    errors["base"] = "cannot_connect"
            else:
                errors["base"] = "empty_search"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required("location_search"): str,
                }
            ),
            errors=errors,
            description_placeholders={
                "example": "Roma, Milano, Napoli..."
            },
        )

    async def async_step_select_location(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle location selection step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            selected_idx = int(user_input["location"])
            selected = self._locations[selected_idx]
            
            location_id = selected.get("id")
            sector_id = selected.get("id_settore", selected.get("id_macrosettore", 1))
            location_name = selected.get("localita", selected.get("nome", "Unknown"))
            province = selected.get("prov", "")
            
            if province:
                full_name = f"{location_name} ({province})"
            else:
                full_name = location_name

            # Check if already configured
            await self.async_set_unique_id(f"{location_id}_{sector_id}")
            self._abort_if_unique_id_configured()

            # Validate the location
            session = async_get_clientsession(self.hass)
            client = TrBMeteoApiClient(session)

            try:
                is_valid = await client.validate_location(location_id, sector_id)
                if not is_valid:
                    errors["base"] = "invalid_location"
                else:
                    return self.async_create_entry(
                        title=full_name,
                        data={
                            CONF_LOCATION_ID: location_id,
                            CONF_SECTOR_ID: sector_id,
                            CONF_LOCATION_NAME: full_name,
                        },
                    )
            except TrBMeteoApiError:
                errors["base"] = "cannot_connect"

        # Build location options
        location_options = {}
        for idx, loc in enumerate(self._locations):
            name = loc.get("localita", loc.get("nome", "Unknown"))
            province = loc.get("prov", "")
            region = loc.get("regione", "")
            
            if province and region:
                label = f"{name} ({province}) - {region}"
            elif province:
                label = f"{name} ({province})"
            else:
                label = name
            
            location_options[str(idx)] = label

        return self.async_show_form(
            step_id="select_location",
            data_schema=vol.Schema(
                {
                    vol.Required("location"): vol.In(location_options),
                }
            ),
            errors=errors,
        )

    async def async_step_manual(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle manual location ID entry."""
        errors: dict[str, str] = {}

        if user_input is not None:
            location_id = user_input[CONF_LOCATION_ID]
            sector_id = user_input.get(CONF_SECTOR_ID, 1)
            location_name = user_input.get(CONF_LOCATION_NAME, f"Location {location_id}")

            await self.async_set_unique_id(f"{location_id}_{sector_id}")
            self._abort_if_unique_id_configured()

            session = async_get_clientsession(self.hass)
            client = TrBMeteoApiClient(session)

            try:
                is_valid = await client.validate_location(location_id, sector_id)
                if not is_valid:
                    errors["base"] = "invalid_location"
                else:
                    return self.async_create_entry(
                        title=location_name,
                        data={
                            CONF_LOCATION_ID: location_id,
                            CONF_SECTOR_ID: sector_id,
                            CONF_LOCATION_NAME: location_name,
                        },
                    )
            except TrBMeteoApiError:
                errors["base"] = "cannot_connect"

        return self.async_show_form(
            step_id="manual",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_LOCATION_ID): int,
                    vol.Optional(CONF_SECTOR_ID, default=1): int,
                    vol.Optional(CONF_LOCATION_NAME): str,
                }
            ),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Get the options flow for this handler."""
        return TrBMeteoOptionsFlowHandler(config_entry)


class TrBMeteoOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow for 3BMeteo."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({}),
        )
