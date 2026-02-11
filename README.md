# 3BMeteo Home Assistant Integration

A custom Home Assistant integration for 3BMeteo weather service (Italy).

## Features

- **Weather Entity**: Current conditions, temperature, humidity, pressure, wind
- **Daily Forecast**: Up to 15 days forecast
- **Hourly Forecast**: Hourly breakdown for current day
- **Location Search**: Search and select your Italian location
- **Automatic Updates**: Weather data updated every 30 minutes

## Installation

### Manual Installation

1. Copy the `custom_components/3bmeteo` folder to your Home Assistant `config/custom_components/` directory.

2. Restart Home Assistant.

3. Go to **Settings** → **Devices & Services** → **Add Integration** → Search for "3BMeteo".

4. Enter your location name (e.g., "Roma", "Milano", "Napoli") and select from the search results.

### HACS Installation

1. Add this repository as a custom repository in HACS.
2. Install the "3BMeteo" integration.
3. Restart Home Assistant.
4. Configure via UI.

## Configuration

The integration is configured via the UI:

1. Search for your location by name
2. Select your location from the search results
3. The weather entity will be created automatically

## Exposed Data

### Current Conditions
- Temperature
- Apparent Temperature (feels like)
- Humidity
- Pressure
- Wind Speed
- Wind Bearing
- Wind Gust Speed
- Weather Condition

### Weather Conditions Mapped
The integration maps 3BMeteo weather symbols to Home Assistant conditions:
- `sunny` - Clear sky
- `partlycloudy` - Partly cloudy
- `cloudy` - Cloudy
- `rainy` - Rain
- `pouring` - Heavy rain
- `lightning-rainy` - Thunderstorms
- `snowy` - Snow
- `snowy-rainy` - Mixed precipitation
- `hail` - Hail
- `fog` - Fog

## Services

The weather entity supports the standard Home Assistant weather services:
- `weather.get_forecasts` - Get daily or hourly forecasts

## Troubleshooting

### "Failed to connect to 3BMeteo API"
- Check your internet connection
- The 3BMeteo API may be temporarily unavailable

### "No locations found"
- Try a different search term
- Use the Italian name of the location
- Try using the manual entry with the location ID

## Credits

Data provided by [3BMeteo](https://www.3bmeteo.com)

## License

This integration is provided as-is for personal use.
