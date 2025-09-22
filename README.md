# 🌤️ Advanced Weather App

A comprehensive, production-ready weather application built with **Streamlit** and **OpenWeatherMap API** that provides real-time weather data, forecasts, and advanced analytics.

![Weather App Demo](https://img.shields.io/badge/Status-Production%20Ready-brightgreen)
![Python Version](https://img.shields.io/badge/Python-3.8%2B-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28%2B-red)

## 🚀 Features

### Core Weather Features
- 🌡️ **Real-time Current Weather** - Get instant weather data for any city worldwide
- 📅 **5-Day Weather Forecast** - Detailed hourly forecasts with interactive charts
- ⚖️ **City Weather Comparison** - Side-by-side weather comparison between cities
- 🔍 **Advanced City Search** - Find cities with geocoding and get weather by coordinates
- 🌍 **Multiple Cities Weather** - Batch weather retrieval for multiple locations

### Advanced Features
- 📊 **Interactive Charts** - Temperature trends with Plotly visualizations
- 📁 **Data Export** - Export weather data in JSON/CSV formats
- 📝 **Search History** - Track and revisit recent weather searches
- 🌡️ **Unit Conversion** - Support for Celsius, Fahrenheit, and Kelvin
- 🎨 **Modern UI** - Responsive design with custom CSS styling
- ⚡ **Smart Caching** - Optimized API usage with intelligent caching

### Production Features
- 🔄 **Retry Logic** - Robust error handling with automatic retries
- 🔐 **Secure Configuration** - Environment-based API key management
- 📈 **Performance Monitoring** - Response time tracking and logging
- 🚫 **Rate Limit Protection** - Built-in API rate limiting
- 🧪 **Unit Testing** - Comprehensive test coverage
- 📱 **Mobile Responsive** - Works seamlessly on all device sizes

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.8 or higher
- OpenWeatherMap API key (free tier available)

### Quick Start

1. **Clone the repository:**
```bash
git clone https://github.com/yourusername/weather-app.git
cd weather-app
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Configure API key:**
   - The API key `064213e30cac368a77dc3ce82ee6696c` is already configured in `config.py`
   - Alternatively, create a `.env` file:
```env
OPENWEATHER_API_KEY=064213e30cac368a77dc3ce82ee6696c
```

4. **Run the application:**
```bash
streamlit run app.py
```

5. **Open your browser:**
   - Navigate to `http://localhost:8501`

## 📁 Project Structure

```
weather_app/
├── 📄 app.py                 # Main Streamlit application
├── 🔧 weather_app_API.py     # Weather API wrapper class
├── ⚙️ config.py              # Configuration settings
├── 🛠️ utils.py               # Utility functions
├── 📋 requirements.txt       # Python dependencies
├── 📖 README.md              # This file
├── 🧪 tests/
│   └── test_api.py           # Unit tests
└── 📊 .streamlit/
    └── config.toml           # Streamlit configuration
```

## 🎯 Usage Guide

### 1. Current Weather
- Enter any city name to get real-time weather data
- Use quick-access buttons for major cities
- View detailed metrics including temperature, humidity, wind, and pressure
- Get weather advice based on current conditions

### 2. Weather Forecast
- Get up to 5-day forecasts with 3-hour intervals
- Interactive temperature trend charts
- Daily weather summaries with min/max temperatures
- Visual weather condition indicators

### 3. City Comparison
- Compare weather between any two cities
- Side-by-side metrics comparison
- Temperature difference calculations
- Visual comparison charts

### 4. City Search
- Search for cities worldwide with autocomplete
- Get weather by precise coordinates
- Bulk weather retrieval for multiple cities
- Geographic information for each location

### 5. Data Export
- Export current weather data as JSON
- Export forecast data as CSV
- Copy weather summaries to clipboard
- Save search history

## 🔧 Configuration Options

### API Settings (`config.py`)
```python
# API Configuration
API_KEY = "your_openweathermap_api_key"
BASE_URL = "https://api.openweathermap.org/data/2.5"
REQUEST_TIMEOUT = 10  # seconds
MAX_RETRIES = 3

# Cache Settings
CACHE_DURATION = 600  # 10 minutes

# Default Settings
DEFAULT_CITY = "London"
DEFAULT_UNITS = "metric"  # metric, imperial, standard
```

### Unit Systems
- **Metric**: Celsius, m/s, hPa
- **Imperial**: Fahrenheit, mph, hPa  
- **Standard**: Kelvin, m/s, hPa

## 🧪 Testing

Run the comprehensive test suite:

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test file
python tests/test_api.py

# Run with coverage
python -m pytest tests/ --cov=weather_app_API --cov-report=html
```

### Test Coverage
- ✅ API wrapper functionality
- ✅ Error handling and edge cases
- ✅ Utility function validation
- ✅ Integration tests (optional, requires API key)
- ✅ Mock API responses
- ✅ Rate limiting and retry logic

## 🚀 Deployment

### Streamlit Cloud (Recommended)

1. **Push to GitHub:**
```bash
git add .
git commit -m "Initial weather app commit"
git push origin main
```

2. **Deploy on Streamlit Cloud:**
   - Visit [share.streamlit.io](https://share.streamlit.io)
   - Connect your GitHub repository
   - Set environment variables (API key)
   - Deploy!

### Local Production Server

```bash
# Install production server
pip install streamlit

# Run with production settings
streamlit run app.py --server.port 8080 --server.address 0.0.0.0
```

### Docker Deployment

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.address", "0.0.0.0"]
```

## 🔍 API Reference

### WeatherAPI Class Methods

```python
# Initialize API
api = WeatherAPI(api_key="your_key")

# Get current weather
weather = api.get_weather("London", units="metric")

# Get forecast
forecast = api.get_forecast("London", days=5, units="metric")

# Get weather by coordinates
weather = api.get_weather_by_coordinates(lat=51.5074, lon=-0.1278, units="metric")

# Search cities
cities = api.search_cities("London", limit=5)

# Multiple cities weather
results = api.get_multiple_cities_weather(["London", "Paris"], units="metric")
```

### Error Handling

```python
from weather_app_API import WeatherAPIError

try:
    weather = api.get_weather("InvalidCity")
except WeatherAPIError as e:
    print(f"Weather API error: {e}")
```

## 📊 Performance & Monitoring

### Built-in Analytics
- Response time tracking
- API call success/failure rates
- Search history analytics
- Cache hit/miss ratios

### Logging
```python
import logging

# Configure logging level
logging.basicConfig(level=logging.INFO)

# View API call logs
logger = logging.getLogger('weather_app_API')
```

## 🤝 Contributing

1. **Fork the repository**
2. **Create a feature branch:**
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. **Make your changes and add tests**
4. **Run tests:**
   ```bash
   python -m pytest tests/
   ```
5. **Commit your changes:**
   ```bash
   git commit -m "Add amazing feature"
   ```
6. **Push to your branch:**
   ```bash
   git push origin feature/amazing-feature
   ```
7. **Open a Pull Request**

## 🐛 Troubleshooting

### Common Issues

**API Key Error:**
```
WeatherAPIError: Invalid API key
```
- Verify your API key in `config.py`
- Check OpenWeatherMap account status
- Ensure API key has necessary permissions

**City Not Found:**
```
WeatherAPIError: City 'xyz' not found
```
- Check city name spelling
- Try searching with country code: "London,GB"
- Use the city search feature for suggestions

**Rate Limit Exceeded:**
```
WeatherAPIError: API rate limit exceeded
```
- Wait for rate limit reset (usually 1 hour)
- Consider upgrading OpenWeatherMap plan
- Use caching to reduce API calls

**Connection Timeout:**
```
WeatherAPIError: Request timeout
```
- Check internet connection
- Increase timeout in `config.py`
- Verify OpenWeatherMap service status

## 📈 Roadmap

### Upcoming Features
- [ ] **Weather Alerts** - Push notifications for severe weather
- [ ] **Historical Data** - Weather trends and historical comparisons
- [ ] **Weather Maps** - Interactive weather map integration
- [ ] **Air Quality Index** - Detailed air pollution data
- [ ] **Weather Widgets** - Embeddable weather widgets
- [ ] **Multi-language Support** - Internationalization
- [ ] **Dark Mode** - Theme switching capability
- [ ] **Weather API Aggregation** - Multiple weather service integration

### Performance Improvements
- [ ] **Database Integration** - PostgreSQL/SQLite for data persistence
- [ ] **Redis Caching** - Advanced caching layer
- [ ] **API Response Compression** - Reduce bandwidth usage
- [ ] **Lazy Loading** - Optimize app startup time

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **OpenWeatherMap** - Weather data API
- **Streamlit** - Web application framework
- **Plotly** - Interactive visualization library
- **Requests** - HTTP library for Python

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/weather-app/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/weather-app/discussions)
- **Email**: your.email@domain.com

---

<div align="center">
  <p>Built with ❤️ by [Your Name]</p>
  <p>
    <a href="#top">⬆️ Back to Top</a>
  </p>
</div>