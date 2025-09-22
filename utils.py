# utils.py
import streamlit as st
from datetime import datetime, timezone
from typing import Dict, Any
import logging
from config import Config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def format_temperature(temp: float, units: str = "metric") -> str:
    """Format temperature with appropriate unit symbol"""
    unit_symbol = Config.UNITS_DISPLAY[units]["temp"]
    return f"{temp:.1f}{unit_symbol}"

def format_pressure(pressure: float) -> str:
    """Format pressure in hPa"""
    return f"{pressure} hPa"

def format_humidity(humidity: int) -> str:
    """Format humidity as percentage"""
    return f"{humidity}%"

def format_wind_speed(speed: float, units: str = "metric") -> str:
    """Format wind speed with appropriate unit"""
    unit_symbol = Config.UNITS_DISPLAY[units]["speed"]
    return f"{speed:.1f} {unit_symbol}"

def format_visibility(visibility: float) -> str:
    """Format visibility in km"""
    visibility_km = visibility / 1000
    return f"{visibility_km:.1f} km"

def get_weather_icon(icon_code: str) -> str:
    """Get emoji icon for weather condition"""
    return Config.WEATHER_ICONS.get(icon_code, "🌤️")

def format_datetime(timestamp: int, timezone_offset: int = 0) -> str:
    """Format Unix timestamp to readable datetime"""
    dt = datetime.fromtimestamp(timestamp + timezone_offset, tz=timezone.utc)
    return dt.strftime("%Y-%m-%d %H:%M:%S UTC")

def format_time(timestamp: int, timezone_offset: int = 0) -> str:
    """Format Unix timestamp to readable time only"""
    dt = datetime.fromtimestamp(timestamp + timezone_offset, tz=timezone.utc)
    return dt.strftime("%H:%M")

def capitalize_words(text: str) -> str:
    """Capitalize each word in a string"""
    return ' '.join(word.capitalize() for word in text.split())

def validate_city_name(city: str) -> bool:
    """Validate city name input"""
    if not city or len(city.strip()) < 2:
        return False
    if not city.replace(' ', '').replace('-', '').isalpha():
        return False
    return True

def create_weather_summary(weather_data: Dict[str, Any]) -> str:
    """Create a human-readable weather summary"""
    try:
        main = weather_data['weather'][0]['main']
        description = weather_data['weather'][0]['description']
        temp = weather_data['main']['temp']
        feels_like = weather_data['main']['feels_like']
        
        summary = f"Currently {description} with temperature {temp:.1f}°C "
        summary += f"(feels like {feels_like:.1f}°C)"
        
        return summary
    except KeyError as e:
        logger.error(f"Error creating weather summary: {e}")
        return "Weather summary unavailable"

def get_weather_advice(weather_data: Dict[str, Any]) -> str:
    """Get weather-based advice"""
    try:
        main_weather = weather_data['weather'][0]['main'].lower()
        temp = weather_data['main']['temp']
        
        if main_weather in ['rain', 'drizzle']:
            return "☔ Don't forget your umbrella!"
        elif main_weather == 'snow':
            return "❄️ Bundle up and watch for slippery conditions!"
        elif main_weather == 'thunderstorm':
            return "⛈️ Stay indoors if possible!"
        elif temp > 30:
            return "🌡️ Stay hydrated and seek shade!"
        elif temp < 0:
            return "🧥 Dress warmly!"
        elif main_weather == 'clear':
            return "☀️ Perfect weather to go outside!"
        else:
            return "🌤️ Have a great day!"
    except KeyError:
        return "Have a wonderful day!"

def color_temp_by_range(temp: float) -> str:
    """Return color based on temperature range"""
    if temp <= 0:
        return "#0066CC"  # Cold blue
    elif temp <= 10:
        return "#00AACC"  # Cool blue
    elif temp <= 20:
        return "#00CC66"  # Mild green
    elif temp <= 30:
        return "#FFAA00"  # Warm orange
    else:
        return "#FF4444"  # Hot red

@st.cache_data(ttl=Config.CACHE_DURATION)
def cache_weather_data(city: str, units: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """Cache weather data to avoid repeated API calls"""
    return data

def log_search_history(city: str, success: bool = True):
    """Log search history for analytics"""
    if 'search_history' not in st.session_state:
        st.session_state.search_history = []
    
    search_entry = {
        'city': city,
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'success': success
    }
    
    # Keep only last 10 searches
    st.session_state.search_history.insert(0, search_entry)
    if len(st.session_state.search_history) > 10:
        st.session_state.search_history.pop()

def get_search_history() -> list:
    """Get search history"""
    return st.session_state.get('search_history', [])