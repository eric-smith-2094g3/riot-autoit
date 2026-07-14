import time
import requests

# WMO code to friendly phrase
WMO_DESCRIPTIONS = {
    0: "Clear",
    1: "Mostly Clear",
    2: "Partly Cloudy",
    3: "Overcast",
    45: "Foggy",
    48: "Rime Fog",
    51: "Light Drizzle",
    53: "Drizzle",
    55: "Dense Drizzle",
    61: "Light Rain",
    63: "Rain",
    65: "Heavy Rain",
    71: "Light Snow",
    73: "Snow",
    75: "Heavy Snow",
    80: "Showers",
    81: "Heavy Showers",
    82: "Violent Showers",
    95: "Stormy",
    96: "Hail Storm",
}

_cached_result = None
_last_fetch = 0.0
CACHE_TTL = 600.0  # 10 minutes


def fetch_weather(lat, lon, city_label=""):
    global _cached_result, _last_fetch
    now = time.time()
    if _cached_result and (now - _last_fetch) < CACHE_TTL:
        return _cached_result

    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current_weather": "true",
        "timezone": "auto",
    }
    try:
        resp = requests.get(url, params=params, timeout=5)
        if resp.status_code != 200:
            return _cached_result or "Weather unavailable"
        data = resp.json().get("current_weather", {})
    except requests.RequestException:
        # fall back to previous reading if offline briefly
        return _cached_result or "Weather unavailable"

    temp = round(data.get("temperature", 0))
    code = data.get("weathercode", 0)
    desc = WMO_DESCRIPTIONS.get(code, "Fair")
    wind = round(data.get("windspeed", 0))

    prefix = f"{city_label}: " if city_label else ""
    result = f"{prefix}{temp}C {desc} (wind {wind} km/h)"
    _cached_result = result
    _last_fetch = now
    return result
