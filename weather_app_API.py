# weather_app_API.py
import requests
import logging
import time
from typing import Dict, List, Optional, Tuple, Any
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from config import Config
from utils import log_search_history

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WeatherAPIError(Exception):
    """Custom exception for Weather API errors"""
    pass

class WeatherAPI:
    def __init__(self, api_key: str = None):
        """Initialize WeatherAPI with configuration"""
        self.api_key = api_key or Config.API_KEY
        self.base_url = Config.BASE_URL
        self.geocoding_url = Config.GEOCODING_URL
        self.session = self._create_session()
        
    def _create_session(self) -> requests.Session:
        """Create requests session with retry strategy"""
        session = requests.Session()
        
        retry_strategy = Retry(
            total=Config.MAX_RETRIES,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"],
            backoff_factor=1
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        return session
    
    def _make_request(self, url: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Make HTTP request with error handling"""
        try:
            params['appid'] = self.api_key
            
            logger.info(f"Making API request to: {url}")
            response = self.session.get(
                url, 
                params=params, 
                timeout=Config.REQUEST_TIMEOUT
            )
            
            response.raise_for_status()
            data = response.json()
            
            # Check for API-specific errors
            if 'cod' in data and str(data['cod']) != '200':
                error_msg = data.get('message', 'Unknown API error')
                raise WeatherAPIError(f"API Error {data['cod']}: {error_msg}")
            
            return data
            
        except requests.exceptions.Timeout:
            logger.error("Request timeout occurred")
            raise WeatherAPIError("Request timeout. Please try again.")
            
        except requests.exceptions.ConnectionError:
            logger.error("Connection error occurred")
            raise WeatherAPIError("Connection error. Please check your internet connection.")
            
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error occurred: {e}")
            if response.status_code == 401:
                raise WeatherAPIError("Invalid API key. Please check your configuration.")
            elif response.status_code == 404:
                raise WeatherAPIError("City not found. Please check the spelling.")
            elif response.status_code == 429:
                raise WeatherAPIError("API rate limit exceeded. Please try again later.")
            else:
                raise WeatherAPIError(f"HTTP Error {response.status_code}")
                
        except ValueError as e:
            logger.error(f"JSON decode error: {e}")
            raise WeatherAPIError("Invalid response from weather service.")
            
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise WeatherAPIError(f"Unexpected error: {str(e)}")
    
    def get_coordinates(self, city: str) -> Tuple[float, float]:
        """Get latitude and longitude for a city using geocoding API"""
        try:
            url = f"{self.geocoding_url}/direct"
            params = {
                'q': city,
                'limit': 1
            }
            
            data = self._make_request(url, params)
            
            if not data:
                raise WeatherAPIError(f"City '{city}' not found")
            
            location = data[0]
            lat = location['lat']
            lon = location['lon']
            
            logger.info(f"Coordinates for {city}: ({lat}, {lon})")
            return lat, lon
            
        except Exception as e:
            logger.error(f"Error getting coordinates for {city}: {e}")
            raise WeatherAPIError(f"Could not find coordinates for {city}")
    
    def get_weather(self, city: str, units: str = "metric") -> Dict[str, Any]:
        """
        Get current weather data for a city
        
        Args:
            city (str): City name
            units (str): Temperature units (metric, imperial, standard)
            
        Returns:
            Dict containing weather data
        """
        try:
            start_time = time.time()
            
            url = f"{self.base_url}/weather"
            params = {
                'q': city,
                'units': units
            }
            
            data = self._make_request(url, params)
            
            # Log successful search
            log_search_history(city, success=True)
            
            # Add metadata
            data['_metadata'] = {
                'city_searched': city,
                'units': units,
                'fetch_time': time.time(),
                'response_time': time.time() - start_time
            }
            
            logger.info(f"Successfully fetched weather for {city}")
            return data
            
        except WeatherAPIError as e:
            log_search_history(city, success=False)
            logger.error(f"Weather API error for {city}: {e}")
            raise
            
        except Exception as e:
            log_search_history(city, success=False)
            logger.error(f"Unexpected error getting weather for {city}: {e}")
            raise WeatherAPIError(f"Error fetching weather data: {str(e)}")
    
    def get_forecast(self, city: str, days: int = 5, units: str = "metric") -> Dict[str, Any]:
        """
        Get weather forecast for a city
        
        Args:
            city (str): City name
            days (int): Number of days (1-5)
            units (str): Temperature units
            
        Returns:
            Dict containing forecast data
        """
        try:
            start_time = time.time()
            
            # Validate days parameter
            if not 1 <= days <= 5:
                raise ValueError("Days must be between 1 and 5")
            
            url = f"{self.base_url}/forecast"
            params = {
                'q': city,
                'units': units,
                'cnt': days * 8  # 8 forecasts per day (every 3 hours)
            }
            
            data = self._make_request(url, params)
            
            # Add metadata
            data['_metadata'] = {
                'city_searched': city,
                'units': units,
                'days_requested': days,
                'fetch_time': time.time(),
                'response_time': time.time() - start_time
            }
            
            logger.info(f"Successfully fetched {days}-day forecast for {city}")
            return data
            
        except WeatherAPIError as e:
            logger.error(f"Forecast API error for {city}: {e}")
            raise
            
        except Exception as e:
            logger.error(f"Unexpected error getting forecast for {city}: {e}")
            raise WeatherAPIError(f"Error fetching forecast data: {str(e)}")
    
    def get_weather_by_coordinates(self, lat: float, lon: float, units: str = "metric") -> Dict[str, Any]:
        """Get weather data by latitude and longitude"""
        try:
            url = f"{self.base_url}/weather"
            params = {
                'lat': lat,
                'lon': lon,
                'units': units
            }
            
            data = self._make_request(url, params)
            
            # Add metadata
            data['_metadata'] = {
                'coordinates': (lat, lon),
                'units': units,
                'fetch_time': time.time()
            }
            
            logger.info(f"Successfully fetched weather for coordinates ({lat}, {lon})")
            return data
            
        except Exception as e:
            logger.error(f"Error getting weather by coordinates: {e}")
            raise WeatherAPIError(f"Error fetching weather data: {str(e)}")
    
    def get_air_quality(self, lat: float, lon: float) -> Dict[str, Any]:
        """Get air quality data for coordinates"""
        try:
            url = "http://api.openweathermap.org/data/2.5/air_pollution"
            params = {
                'lat': lat,
                'lon': lon
            }
            
            data = self._make_request(url, params)
            
            logger.info(f"Successfully fetched air quality for ({lat}, {lon})")
            return data
            
        except Exception as e:
            logger.error(f"Error getting air quality: {e}")
            raise WeatherAPIError(f"Error fetching air quality data: {str(e)}")
    
    def search_cities(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search for cities matching query"""
        try:
            url = f"{self.geocoding_url}/direct"
            params = {
                'q': query,
                'limit': limit
            }
            
            data = self._make_request(url, params)
            
            logger.info(f"Found {len(data)} cities matching '{query}'")
            return data
            
        except Exception as e:
            logger.error(f"Error searching cities: {e}")
            raise WeatherAPIError(f"Error searching cities: {str(e)}")
    
    def get_multiple_cities_weather(self, cities: List[str], units: str = "metric") -> Dict[str, Any]:
        """Get weather data for multiple cities"""
        results = {}
        errors = {}
        
        for city in cities:
            try:
                weather_data = self.get_weather(city, units)
                results[city] = weather_data
                time.sleep(0.1)  # Small delay to avoid rate limiting
                
            except Exception as e:
                errors[city] = str(e)
                logger.error(f"Failed to get weather for {city}: {e}")
        
        return {
            'successful': results,
            'errors': errors,
            'total_requested': len(cities),
            'successful_count': len(results),
            'error_count': len(errors)
        }

# Convenience functions for backward compatibility
def get_weather(city: str, units: str = "metric") -> Dict[str, Any]:
    """Convenience function to get current weather"""
    api = WeatherAPI()
    return api.get_weather(city, units)

def get_forecast(city: str, days: int = 3, units: str = "metric") -> Dict[str, Any]:
    """Convenience function to get weather forecast"""
    api = WeatherAPI()
    return api.get_forecast(city, days, units)