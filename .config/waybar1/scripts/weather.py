#!/usr/bin/env python3
"""
Waybar weather module - Enhanced Edition
Location: Odendaalsrus, Free State, South Africa
Features: Current + feels like + pressure + wind (km/h + direction) 
 + sunrise/sunset + approximate moon phase + 5-day daily forecast
"""

import json
import requests
import os
import sys
import math
from datetime import datetime, timezone, timedelta

# 🎯 YOUR CONFIGURATION
LAT = -27.7333
LON = 27.0667
API_KEY = "203c09a562baa3933b414cc39687c9b3"  # ← Your spare key
UNITS = "metric"  # Celsius, m/s (we convert to km/h)
LANG = "en"
DISPLAY_NAME = "Odendaalsrus"  # Force display name
CACHE_FILE = os.path.join(os.path.dirname(__file__), "weather-cache.json")
CACHE_DURATION = 600  # 10 minutes cache

# Weather code → Emoji mapping
WEATHER_ICONS = {
    200: "⛈️", 201: "⛈️", 202: "⛈️", 210: "⛈️", 211: "⛈️", 212: "⛈️", 221: "⛈️", 230: "⛈️", 231: "⛈️", 232: "⛈️",
    300: "🌦️", 301: "🌦️", 302: "🌧️", 310: "🌦️", 311: "🌧️", 312: "🌧️", 313: "🌧️", 314: "🌧️", 321: "🌧️",
    500: "🌦️", 501: "🌧️", 502: "🌧️", 503: "🌧️", 504: "🌧️", 511: "🌨️", 520: "🌦️", 521: "🌧️", 522: "🌧️", 531: "🌧️",
    600: "🌨️", 601: "❄️", 602: "❄️", 611: "🌨️", 612: "🌨️", 613: "🌨️", 615: "🌨️", 616: "🌨️", 620: "🌨️", 621: "❄️", 622: "❄️",
    701: "🌫️", 711: "🌫️", 721: "🌫️", 731: "🌫️", 741: "🌫️", 751: "🌫️", 761: "🌫️", 762: "🌋", 771: "🌬️", 781: "🌪️",
    800: "☀️", 801: "🌤️", 802: "⛅", 803: "☁️", 804: "☁️"
}

def get_cached_data():
    """Load cached weather if still valid."""
    try:
        if os.path.exists(CACHE_FILE):
            with open(CACHE_FILE, 'r') as f:
                cache = json.load(f)
            if datetime.now().timestamp() - cache.get('timestamp', 0) < CACHE_DURATION:
                return cache.get('data')
    except:
        pass
    return None

def save_cache(data):
    """Save weather data to cache."""
    try:
        with open(CACHE_FILE, 'w') as f:
            json.dump({'timestamp': datetime.now().timestamp(), 'data': data}, f)
    except:
        pass

def wind_direction(deg):
    """Convert degrees to cardinal direction."""
    dirs = ["N","NNE","NE","ENE","E","ESE","SE","SSE","S","SSW","SW","WSW","W","WNW","NW","NNW"]
    try:
        return dirs[int((float(deg) + 11.25) / 22.5) % 16]
    except:
        return "?"

def moon_phase_name(phase):
    """Convert moon phase (0-1) to name + emoji."""
    phases = [
        (0.00, 0.03, "🌑", "New Moon"),
        (0.03, 0.22, "🌒", "Waxing Crescent"),
        (0.22, 0.28, "🌓", "First Quarter"),
        (0.28, 0.47, "🌔", "Waxing Gibbous"),
        (0.47, 0.53, "🌕", "Full Moon"),
        (0.53, 0.72, "🌖", "Waning Gibbous"),
        (0.72, 0.78, "🌗", "Last Quarter"),
        (0.78, 0.97, "🌘", "Waning Crescent"),
        (0.97, 1.00, "🌑", "New Moon"),
    ]
    for start, end, emoji, name in phases:
        if start <= phase < end:
            return emoji, name
    return "🌙", "Unknown"

def calculate_moon_phase(date=None):
    """Approximate moon phase calculation (synodic month ~29.53 days)."""
    if date is None:
        date = datetime.now()
    # Known new moon: Jan 6, 2000
    known_new_moon = datetime(2000, 1, 6, 18, 14, 0, tzinfo=timezone.utc)
    synodic_month = 29.53058867
    days_since = (date.replace(tzinfo=timezone.utc) - known_new_moon).total_seconds() / 86400
    phase = (days_since % synodic_month) / synodic_month
    return round(phase, 3)

def format_time(timestamp, tz_offset=None):
    """Format Unix timestamp to local time string."""
    try:
        if tz_offset:
            # CORRECT: use timedelta (not timezone.timedelta)
            local = datetime.fromtimestamp(timestamp, tz=timezone.utc) + timedelta(seconds=tz_offset)
        else:
            local = datetime.fromtimestamp(timestamp)
        return local.strftime("%H:%M")
    except:
        return "??:??"

def get_daily_foresum(forecast_list):
    """Condense 3-hour forecast into daily summaries (one per day)."""
    daily = {}
    for item in forecast_list:
        dt = datetime.fromtimestamp(item['dt'])
        day_key = dt.strftime("%Y-%m-%d")
        if day_key not in daily:
            daily[day_key] = {
                'date': dt.strftime("%a %d"),
                'temp_min': item['main']['temp_min'],
                'temp_max': item['main']['temp_max'],
                'icon': WEATHER_ICONS.get(item['weather'][0]['id'], "🌡️"),
                'desc': item['weather'][0]['description'].title()
            }
        else:
            daily[day_key]['temp_min'] = min(daily[day_key]['temp_min'], item['main']['temp_min'])
            daily[day_key]['temp_max'] = max(daily[day_key]['temp_max'], item['main']['temp_max'])
    return list(daily.values())[:5]  # Return next 5 days

def fetch_weather():
    """Fetch current weather + forecast from OpenWeatherMap."""
    try:
        # Current weather (includes sunrise/sunset)
        current_url = f"https://api.openweathermap.org/data/2.5/weather?lat={LAT}&lon={LON}&appid={API_KEY}&units={UNITS}&lang={LANG}"
        current = requests.get(current_url, timeout=10).json()
        
        # 5-day forecast (3-hour steps)
        forecast_url = f"https://api.openweathermap.org/data/2.5/forecast?lat={LAT}&lon={LON}&appid={API_KEY}&units={UNITS}&lang={LANG}"
        forecast = requests.get(forecast_url, timeout=10).json()
        
        return current, forecast
    except Exception as e:
        return None, str(e)

def main():
    # Try cache first
    cached = get_cached_data()
    if cached:
        print(json.dumps(cached))
        return
    
    # Fetch fresh data
    current, forecast = fetch_weather()
    
    # Error handling
    if current is None or current.get("cod") != 200:
        error = {"text": "🔗 °", "tooltip": f"Weather error: {forecast if isinstance(forecast, str) else 'API error'}"}
        print(json.dumps(error))
        return
    
    try:
        # ===== CURRENT CONDITIONS =====
        main = current["main"]
        wind = current["wind"]
        weather = current["weather"][0]
        sys_data = current["sys"]
        
        temp = main["temp"]
        feels = main["feels_like"]
        pressure = main["pressure"]  # hPa
        humidity = main["humidity"]
        
        wind_ms = wind["speed"]
        wind_kmh = round(wind_ms * 3.6, 1)  # Convert m/s → km/h
        wind_deg = wind.get("deg", 0)
        wind_dir = wind_direction(wind_deg)
        
        desc = weather["description"].title()
        code = weather["id"]
        icon = WEATHER_ICONS.get(code, "🌡️")
        
        # Sunrise/Sunset
        sunrise = format_time(sys_data["sunrise"])
        sunset = format_time(sys_data["sunset"])
        
        # Moon phase (approximate)
        moon_phase_val = calculate_moon_phase()
        moon_emoji, moon_name = moon_phase_name(moon_phase_val)
        
        # ===== FORECAST (5 days) =====
        daily_forecast = get_daily_foresum(forecast["list"]) if "list" in forecast else []
        
        # ===== BUILD WAYBAR OUTPUT =====
        output = {}
        output["text"] = f"{icon} {temp:.0f}°"
        
        # Build rich tooltip
        city = DISPLAY_NAME if DISPLAY_NAME else current.get("name", "Unknown")
        tooltip = f"<b>📍 {city}</b>\n"
        tooltip += f"<b>{icon} {desc}</b> • {temp:.0f}°C\n"
        tooltip += f"Feels: {feels:.0f}°C • 💧 {humidity}%\n"
        tooltip += f"🌬️ {wind_dir} {wind_kmh} km/h • 🌡️ {pressure} hPa\n"
        tooltip += f"🌅 {sunrise} • 🌇 {sunset} • {moon_emoji} {moon_name}\n"
        
        # Add 5-day forecast
        if daily_forecast:
            tooltip += f"\n<b>📅 5-Day Forecast:</b>\n"
            for day in daily_forecast:
                tooltip += f"{day['date']} {day['icon']} {day['temp_min']:.0f}°/{day['temp_max']:.0f}° {day['desc'][:15]}\n"
        
        # Footer note about moon phase
        tooltip += f"\n<i>Moon phase is approximate. For exact data, upgrade to OneCall API.</i>"
        
        output["tooltip"] = tooltip
        
        # Cache and output
        save_cache(output)
        print(json.dumps(output))
        
    except Exception as e:
        error = {"text": "❌", "tooltip": f"Parse error: {str(e)[:100]}"}
        print(json.dumps(error))

if __name__ == "__main__":
    main()
