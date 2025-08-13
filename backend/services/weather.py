import os
from typing import Optional, Dict, Any
import requests
from ..config import AppConfig


def fetch_weather_snapshot(lat: float, lon: float) -> Optional[Dict[str, Any]]:
    key = AppConfig().WEATHER_API_KEY
    if not key:
        return None
    try:
        # Current Weather API v2.5 (as per provided docs)
        params = {
            'lat': lat,
            'lon': lon,
            'appid': key,
            'units': 'metric',
        }
        # Optional language via env
        lang = os.environ.get('WEATHER_LANG')
        if lang:
            params['lang'] = lang

        resp = requests.get('https://api.openweathermap.org/data/2.5/weather', params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        main = data.get('main', {})
        wind = data.get('wind', {})
        wlist = data.get('weather') or [{}]
        rain = (data.get('rain') or {}).get('1h')

        return {
            'tempC': main.get('temp'),
            'humidity': main.get('humidity'),
            'pressure': main.get('pressure'),
            'windSpeed': wind.get('speed'),
            'weather': wlist[0].get('description'),
            'rain1h': rain,
        }
    except Exception:
        return None


