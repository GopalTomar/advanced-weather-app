# config.py
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    # API Configuration
    API_KEY = "064213e30cac368a77dc3ce82ee6696c"
    BASE_URL = "https://api.openweathermap.org/data/2.5"
    GEOCODING_URL = "https://api.openweathermap.org/geo/1.0"
    
    # Default Settings
    DEFAULT_CITY = "London"
    DEFAULT_UNITS = "metric"  # metric, imperial, standard
    CACHE_DURATION = 600  # 10 minutes in seconds
    
    # Request Settings
    REQUEST_TIMEOUT = 10  # seconds
    MAX_RETRIES = 3
    
    # UI Settings
    WEATHER_ICONS = {
        "01d": "☀️", "01n": "🌙",  # clear sky
        "02d": "⛅", "02n": "☁️",  # few clouds
        "03d": "☁️", "03n": "☁️",  # scattered clouds
        "04d": "☁️", "04n": "☁️",  # broken clouds
        "09d": "🌧️", "09n": "🌧️", # shower rain
        "10d": "🌦️", "10n": "🌧️", # rain
        "11d": "⛈️", "11n": "⛈️",  # thunderstorm
        "13d": "🌨️", "13n": "🌨️", # snow
        "50d": "🌫️", "50n": "🌫️"  # mist
    }
    
    # Units mapping
    UNITS_DISPLAY = {
        "metric": {"temp": "°C", "speed": "m/s", "pressure": "hPa"},
        "imperial": {"temp": "°F", "speed": "mph", "pressure": "hPa"},
        "standard": {"temp": "K", "speed": "m/s", "pressure": "hPa"}
    }