# app.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import json
import time
from weather_app_API import WeatherAPI, WeatherAPIError
from utils import (
    format_temperature, format_pressure, format_humidity, 
    format_wind_speed, get_weather_icon, format_time,
    capitalize_words, validate_city_name, create_weather_summary,
    get_weather_advice, color_temp_by_range, get_search_history
)
from config import Config

# Page configuration
st.set_page_config(
    page_title="🌤️ Advanced Weather App",
    page_icon="🌤️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize API
@st.cache_resource
def init_weather_api():
    return WeatherAPI()

# Custom CSS
def load_css():
    st.markdown("""
    <style>
    .weather-card {
        background: linear-gradient(135deg, #74b9ff 0%, #0984e3 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #74b9ff;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    .forecast-card {
        background: linear-gradient(135deg, #a8e6cf 0%, #7fcdcd 100%);
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        text-align: center;
    }
    
    .error-card {
        background: linear-gradient(135deg, #ff7675 0%, #d63031 100%);
        color: white;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    .success-card {
        background: linear-gradient(135deg, #00b894 0%, #00a085 100%);
        color: white;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    </style>
    """, unsafe_allow_html=True)

def display_current_weather(weather_data, units):
    """Display current weather information"""
    try:
        # Main weather info
        main = weather_data['main']
        weather = weather_data['weather'][0]
        wind = weather_data.get('wind', {})
        
        city_name = weather_data['name']
        country = weather_data['sys']['country']
        
        # Weather card
        icon = get_weather_icon(weather['icon'])
        
        st.markdown(f"""
        <div class="weather-card">
            <h2 style="margin-bottom: 1rem;">{icon} {city_name}, {country}</h2>
            <div style="display: flex; align-items: center; gap: 2rem;">
                <div style="font-size: 3rem; font-weight: bold;">
                    {format_temperature(main['temp'], units)}
                </div>
                <div>
                    <p style="font-size: 1.2rem; margin: 0;">{capitalize_words(weather['description'])}</p>
                    <p style="margin: 0; opacity: 0.8;">Feels like {format_temperature(main['feels_like'], units)}</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Weather advice
        advice = get_weather_advice(weather_data)
        st.info(advice)
        
        # Metrics in columns
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="🌡️ Temperature",
                value=format_temperature(main['temp'], units),
                delta=f"{main['temp'] - main['feels_like']:.1f}° from feels like"
            )
        
        with col2:
            st.metric(
                label="💧 Humidity", 
                value=format_humidity(main['humidity'])
            )
        
        with col3:
            st.metric(
                label="🌪️ Wind Speed",
                value=format_wind_speed(wind.get('speed', 0), units)
            )
        
        with col4:
            st.metric(
                label="📊 Pressure",
                value=format_pressure(main['pressure'])
            )
        
        # Additional details
        with st.expander("📋 Detailed Information"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Temperature Details:**")
                st.write(f"• Current: {format_temperature(main['temp'], units)}")
                st.write(f"• Feels like: {format_temperature(main['feels_like'], units)}")
                st.write(f"• Min today: {format_temperature(main['temp_min'], units)}")
                st.write(f"• Max today: {format_temperature(main['temp_max'], units)}")
            
            with col2:
                st.write("**Weather Conditions:**")
                st.write(f"• Condition: {capitalize_words(weather['description'])}")
                st.write(f"• Humidity: {format_humidity(main['humidity'])}")
                st.write(f"• Pressure: {format_pressure(main['pressure'])}")
                if 'visibility' in weather_data:
                    visibility_km = weather_data['visibility'] / 1000
                    st.write(f"• Visibility: {visibility_km:.1f} km")
                
                if wind:
                    st.write(f"• Wind speed: {format_wind_speed(wind.get('speed', 0), units)}")
                    if 'deg' in wind:
                        st.write(f"• Wind direction: {wind['deg']}°")
        
        # Sun times
        if 'sys' in weather_data:
            sys_data = weather_data['sys']
            timezone_offset = weather_data.get('timezone', 0)
            
            if 'sunrise' in sys_data and 'sunset' in sys_data:
                sunrise = format_time(sys_data['sunrise'], timezone_offset)
                sunset = format_time(sys_data['sunset'], timezone_offset)
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("🌅 Sunrise", sunrise)
                with col2:
                    st.metric("🌇 Sunset", sunset)
        
        return True
        
    except KeyError as e:
        st.error(f"Error displaying weather data: Missing field {e}")
        return False
    except Exception as e:
        st.error(f"Error displaying weather data: {str(e)}")
        return False

def display_forecast(forecast_data, units):
    """Display weather forecast"""
    try:
        forecast_list = forecast_data['list']
        city_name = forecast_data['city']['name']
        
        st.subheader(f"📅 5-Day Forecast for {city_name}")
        
        # Process forecast data
        daily_data = {}
        hourly_temps = []
        hourly_times = []
        
        for item in forecast_list:
            dt = datetime.fromtimestamp(item['dt'])
            date_str = dt.strftime('%Y-%m-%d')
            time_str = dt.strftime('%H:%M')
            
            # Collect hourly data for chart
            hourly_temps.append(item['main']['temp'])
            hourly_times.append(dt)
            
            # Group by date for daily summary
            if date_str not in daily_data:
                daily_data[date_str] = {
                    'temps': [],
                    'conditions': [],
                    'icons': [],
                    'humidity': [],
                    'wind_speed': []
                }
            
            daily_data[date_str]['temps'].append(item['main']['temp'])
            daily_data[date_str]['conditions'].append(item['weather'][0]['description'])
            daily_data[date_str]['icons'].append(item['weather'][0]['icon'])
            daily_data[date_str]['humidity'].append(item['main']['humidity'])
            daily_data[date_str]['wind_speed'].append(item['wind']['speed'])
        
        # Temperature trend chart
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=hourly_times,
            y=hourly_temps,
            mode='lines+markers',
            name='Temperature',
            line=dict(color='#74b9ff', width=3),
            marker=dict(size=6)
        ))
        
        fig.update_layout(
            title=f"Temperature Trend - {city_name}",
            xaxis_title="Time",
            yaxis_title=f"Temperature ({Config.UNITS_DISPLAY[units]['temp']})",
            hovermode='x unified',
            template='plotly_white'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Daily forecast cards
        st.subheader("📊 Daily Summary")
        
        for date_str, data in list(daily_data.items())[:5]:  # Show 5 days
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            day_name = date_obj.strftime('%A, %B %d')
            
            col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 1])
            
            with col1:
                # Most common weather condition and icon
                most_common_icon = max(set(data['icons']), key=data['icons'].count)
                icon = get_weather_icon(most_common_icon)
                most_common_condition = max(set(data['conditions']), key=data['conditions'].count)
                
                st.write(f"**{day_name}**")
                st.write(f"{icon} {capitalize_words(most_common_condition)}")
            
            with col2:
                min_temp = min(data['temps'])
                max_temp = max(data['temps'])
                st.metric(
                    "🌡️ Temp Range",
                    f"{max_temp:.0f}°/{min_temp:.0f}°"
                )
            
            with col3:
                avg_humidity = sum(data['humidity']) / len(data['humidity'])
                st.metric("💧 Humidity", f"{avg_humidity:.0f}%")
            
            with col4:
                avg_wind = sum(data['wind_speed']) / len(data['wind_speed'])
                st.metric("🌪️ Wind", f"{avg_wind:.1f} {Config.UNITS_DISPLAY[units]['speed']}")
            
            with col5:
                temp_color = color_temp_by_range(max_temp)
                st.markdown(f'<div style="background-color: {temp_color}; padding: 10px; border-radius: 5px; text-align: center; color: white; font-weight: bold;">{max_temp:.0f}°</div>', 
                           unsafe_allow_html=True)
            
            st.divider()
        
        return True
        
    except KeyError as e:
        st.error(f"Error displaying forecast data: Missing field {e}")
        return False
    except Exception as e:
        st.error(f"Error displaying forecast data: {str(e)}")
        return False

def display_comparison(weather_data1, weather_data2, units):
    """Display weather comparison between two cities"""
    try:
        city1 = weather_data1['name']
        city2 = weather_data2['name']
        
        st.subheader(f"⚖️ Weather Comparison: {city1} vs {city2}")
        
        col1, col2 = st.columns(2)
        
        # City 1
        with col1:
            st.markdown(f"### {city1}, {weather_data1['sys']['country']}")
            
            main1 = weather_data1['main']
            weather1 = weather_data1['weather'][0]
            icon1 = get_weather_icon(weather1['icon'])
            
            st.markdown(f"""
            <div class="weather-card" style="margin-bottom: 1rem;">
                <div style="text-align: center;">
                    <div style="font-size: 2rem;">{icon1}</div>
                    <div style="font-size: 2rem; font-weight: bold;">{format_temperature(main1['temp'], units)}</div>
                    <p>{capitalize_words(weather1['description'])}</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.metric("Feels Like", format_temperature(main1['feels_like'], units))
            st.metric("Humidity", format_humidity(main1['humidity']))
            st.metric("Pressure", format_pressure(main1['pressure']))
        
        # City 2
        with col2:
            st.markdown(f"### {city2}, {weather_data2['sys']['country']}")
            
            main2 = weather_data2['main']
            weather2 = weather_data2['weather'][0]
            icon2 = get_weather_icon(weather2['icon'])
            
            st.markdown(f"""
            <div class="weather-card" style="margin-bottom: 1rem;">
                <div style="text-align: center;">
                    <div style="font-size: 2rem;">{icon2}</div>
                    <div style="font-size: 2rem; font-weight: bold;">{format_temperature(main2['temp'], units)}</div>
                    <p>{capitalize_words(weather2['description'])}</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            temp_diff = main2['temp'] - main1['temp']
            st.metric(
                "Feels Like", 
                format_temperature(main2['feels_like'], units),
                delta=f"{temp_diff:+.1f}° vs {city1}"
            )
            
            humidity_diff = main2['humidity'] - main1['humidity']
            st.metric(
                "Humidity", 
                format_humidity(main2['humidity']),
                delta=f"{humidity_diff:+d}% vs {city1}"
            )
            
            pressure_diff = main2['pressure'] - main1['pressure']
            st.metric(
                "Pressure", 
                format_pressure(main2['pressure']),
                delta=f"{pressure_diff:+.1f} vs {city1}"
            )
        
        # Comparison chart
        comparison_data = {
            'City': [city1, city2],
            'Temperature': [main1['temp'], main2['temp']],
            'Feels Like': [main1['feels_like'], main2['feels_like']],
            'Humidity': [main1['humidity'], main2['humidity']],
            'Pressure': [main1['pressure'], main2['pressure']]
        }
        
        df = pd.DataFrame(comparison_data)
        
        # Temperature comparison chart
        fig = px.bar(
            df, 
            x='City', 
            y='Temperature',
            title=f'Temperature Comparison ({Config.UNITS_DISPLAY[units]["temp"]})',
            color='Temperature',
            color_continuous_scale='RdYlBu_r'
        )
        st.plotly_chart(fig, use_container_width=True)
        
        return True
        
    except Exception as e:
        st.error(f"Error displaying comparison: {str(e)}")
        return False

def search_history_sidebar():
    """Display search history in sidebar"""
    st.sidebar.subheader("📝 Recent Searches")
    
    history = get_search_history()
    
    if history:
        for i, entry in enumerate(history[:5]):  # Show last 5 searches
            status_icon = "✅" if entry['success'] else "❌"
            st.sidebar.write(f"{status_icon} {entry['city']}")
            st.sidebar.caption(f"🕒 {entry['timestamp']}")
    else:
        st.sidebar.write("No recent searches")

def export_data_section(weather_data, forecast_data=None):
    """Provide data export functionality"""
    st.subheader("📁 Export Data")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 Export Current Weather (JSON)"):
            weather_json = json.dumps(weather_data, indent=2, default=str)
            st.download_button(
                label="Download JSON",
                data=weather_json,
                file_name=f"weather_{weather_data['name']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
    
    with col2:
        if forecast_data and st.button("📈 Export Forecast (CSV)"):
            # Convert forecast to DataFrame
            forecast_rows = []
            for item in forecast_data['list']:
                row = {
                    'datetime': datetime.fromtimestamp(item['dt']).strftime('%Y-%m-%d %H:%M:%S'),
                    'temperature': item['main']['temp'],
                    'feels_like': item['main']['feels_like'],
                    'humidity': item['main']['humidity'],
                    'pressure': item['main']['pressure'],
                    'weather': item['weather'][0]['main'],
                    'description': item['weather'][0]['description'],
                    'wind_speed': item['wind']['speed']
                }
                forecast_rows.append(row)
            
            df = pd.DataFrame(forecast_rows)
            csv = df.to_csv(index=False)
            
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"forecast_{forecast_data['city']['name']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
    
    with col3:
        if st.button("📋 Copy Weather Summary"):
            if weather_data:
                summary = create_weather_summary(weather_data)
                st.code(summary, language=None)
                st.success("Summary ready to copy!")

def main():
    """Main application function"""
    load_css()
    
    # Initialize session state
    if 'weather_api' not in st.session_state:
        st.session_state.weather_api = init_weather_api()
    
    if 'current_weather' not in st.session_state:
        st.session_state.current_weather = None
    
    if 'forecast_data' not in st.session_state:
        st.session_state.forecast_data = None
    
    # App header
    st.title("🌤️ Advanced Weather App")
    st.markdown("*Get real-time weather data, forecasts, and comparisons for cities worldwide*")
    
    # Sidebar configuration
    st.sidebar.title("⚙️ Settings")
    
    # Units selection
    units = st.sidebar.selectbox(
        "🌡️ Temperature Units",
        options=["metric", "imperial"],
        format_func=lambda x: "Celsius (°C)" if x == "metric" else "Fahrenheit (°F)",
        key="units"
    )
    
    # App mode selection
    app_mode = st.sidebar.selectbox(
        "📱 App Mode",
        ["🏠 Current Weather", "📅 Weather Forecast", "⚖️ City Comparison", "🔍 City Search", "ℹ️ About"]
    )
    
    search_history_sidebar()
    
    # Main content based on selected mode
    if app_mode == "🏠 Current Weather":
        st.header("🌡️ Current Weather")
        
        # City input
        col1, col2 = st.columns([3, 1])
        
        with col1:
            city = st.text_input(
                "Enter city name:",
                placeholder="e.g., London, New York, Tokyo",
                help="Enter the name of any city worldwide"
            )
        
        with col2:
            search_button = st.button("🔍 Get Weather", type="primary")
        
        # Quick city buttons
        st.markdown("**Quick Access:**")
        quick_cities = ["London", "New York", "Tokyo", "Paris", "Sydney", "Mumbai", "Dubai"]
        cols = st.columns(len(quick_cities))
        
        for i, quick_city in enumerate(quick_cities):
            with cols[i]:
                if st.button(quick_city, key=f"quick_{quick_city}"):
                    city = quick_city
                    search_button = True
        
        # Weather display
        if search_button and city:
            if not validate_city_name(city):
                st.error("❌ Please enter a valid city name (letters, spaces, and hyphens only)")
            else:
                try:
                    with st.spinner(f"🔍 Getting weather data for {city}..."):
                        weather_data = st.session_state.weather_api.get_weather(city, units)
                        st.session_state.current_weather = weather_data
                    
                    if display_current_weather(weather_data, units):
                        st.success(f"✅ Weather data updated for {city}")
                        
                        # Export section
                        export_data_section(weather_data)
                        
                except WeatherAPIError as e:
                    st.error(f"❌ {str(e)}")
                except Exception as e:
                    st.error(f"❌ An unexpected error occurred: {str(e)}")
        
        elif st.session_state.current_weather:
            st.info("📊 Showing cached weather data. Enter a city name to get fresh data.")
            display_current_weather(st.session_state.current_weather, units)
    
    elif app_mode == "📅 Weather Forecast":
        st.header("📈 Weather Forecast")
        
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            city = st.text_input(
                "Enter city name for forecast:",
                placeholder="e.g., London, Paris, Tokyo"
            )
        
        with col2:
            days = st.selectbox("Forecast days:", [1, 2, 3, 4, 5], index=2)
        
        with col3:
            get_forecast_btn = st.button("📅 Get Forecast", type="primary")
        
        if get_forecast_btn and city:
            if not validate_city_name(city):
                st.error("❌ Please enter a valid city name")
            else:
                try:
                    with st.spinner(f"📅 Getting {days}-day forecast for {city}..."):
                        forecast_data = st.session_state.weather_api.get_forecast(city, days, units)
                        st.session_state.forecast_data = forecast_data
                    
                    if display_forecast(forecast_data, units):
                        st.success(f"✅ Forecast data loaded for {city}")
                        
                        # Export section
                        export_data_section(None, forecast_data)
                        
                except WeatherAPIError as e:
                    st.error(f"❌ {str(e)}")
                except Exception as e:
                    st.error(f"❌ An unexpected error occurred: {str(e)}")
    
    elif app_mode == "⚖️ City Comparison":
        st.header("🆚 City Weather Comparison")
        
        col1, col2, col3 = st.columns([2, 2, 1])
        
        with col1:
            city1 = st.text_input("First city:", placeholder="e.g., London")
        
        with col2:
            city2 = st.text_input("Second city:", placeholder="e.g., Paris")
        
        with col3:
            compare_btn = st.button("⚖️ Compare", type="primary")
        
        if compare_btn and city1 and city2:
            if not (validate_city_name(city1) and validate_city_name(city2)):
                st.error("❌ Please enter valid city names")
            else:
                try:
                    with st.spinner(f"🔍 Comparing weather between {city1} and {city2}..."):
                        weather1 = st.session_state.weather_api.get_weather(city1, units)
                        weather2 = st.session_state.weather_api.get_weather(city2, units)
                    
                    display_comparison(weather1, weather2, units)
                    st.success(f"✅ Comparison completed between {city1} and {city2}")
                    
                except WeatherAPIError as e:
                    st.error(f"❌ {str(e)}")
                except Exception as e:
                    st.error(f"❌ An unexpected error occurred: {str(e)}")
    
    elif app_mode == "🔍 City Search":
        st.header("🔍 City Search & Multiple Weather")
        
        # City search
        st.subheader("🏙️ Search Cities")
        search_query = st.text_input("Search for cities:", placeholder="e.g., London")
        
        if search_query:
            try:
                cities = st.session_state.weather_api.search_cities(search_query, 10)
                
                if cities:
                    st.write(f"Found {len(cities)} cities matching '{search_query}':")
                    
                    for city in cities:
                        col1, col2, col3 = st.columns([2, 1, 1])
                        with col1:
                            country = city.get('country', 'Unknown')
                            state = city.get('state', '')
                            display_name = f"{city['name']}, {state + ', ' if state else ''}{country}"
                            st.write(f"📍 {display_name}")
                        
                        with col2:
                            st.write(f"📐 {city['lat']:.2f}, {city['lon']:.2f}")
                        
                        with col3:
                            if st.button(f"Get Weather", key=f"weather_{city['name']}_{city['lat']}"):
                                try:
                                    weather_data = st.session_state.weather_api.get_weather_by_coordinates(
                                        city['lat'], city['lon'], units
                                    )
                                    display_current_weather(weather_data, units)
                                except Exception as e:
                                    st.error(f"Error: {str(e)}")
                else:
                    st.info("No cities found matching your search.")
            except Exception as e:
                st.error(f"Search error: {str(e)}")
        
        st.divider()
        
        # Multiple cities weather
        st.subheader("🌍 Multiple Cities Weather")
        
        cities_input = st.text_area(
            "Enter multiple cities (one per line):",
            placeholder="London\nParis\nTokyo\nNew York",
            height=100
        )
        
        if st.button("🌐 Get All Weather Data") and cities_input:
            cities_list = [city.strip() for city in cities_input.split('\n') if city.strip()]
            
            if len(cities_list) > 10:
                st.warning("⚠️ Limited to 10 cities to avoid rate limits")
                cities_list = cities_list[:10]
            
            try:
                with st.spinner(f"🔍 Getting weather data for {len(cities_list)} cities..."):
                    results = st.session_state.weather_api.get_multiple_cities_weather(cities_list, units)
                
                st.success(f"✅ Successfully retrieved data for {results['successful_count']}/{results['total_requested']} cities")
                
                # Display successful results
                if results['successful']:
                    for city, weather_data in results['successful'].items():
                        with st.expander(f"🌤️ {city}"):
                            display_current_weather(weather_data, units)
                
                # Display errors
                if results['errors']:
                    st.subheader("❌ Failed Cities")
                    for city, error in results['errors'].items():
                        st.error(f"{city}: {error}")
            
            except Exception as e:
                st.error(f"❌ Error getting multiple cities data: {str(e)}")
    
    elif app_mode == "ℹ️ About":
        st.header("ℹ️ About This App")
        
        st.markdown("""
        ### 🌤️ Advanced Weather App
        
        This is a comprehensive weather application built with **Streamlit** and **OpenWeatherMap API** that provides:
        
        **Features:**
        - 🌡️ Real-time current weather data
        - 📅 5-day weather forecasts with hourly details
        - ⚖️ Side-by-side city weather comparisons
        - 🔍 City search and multiple city weather
        - 📊 Interactive charts and visualizations
        - 📁 Data export (JSON/CSV)
        - 📝 Search history tracking
        - 🌡️ Multiple unit systems (Celsius/Fahrenheit)
        
        **Technical Stack:**
        - **Frontend**: Streamlit
        - **API**: OpenWeatherMap
        - **Charts**: Plotly
        - **Data**: Pandas
        - **HTTP**: Requests with retry logic
        
        **Data Sources:**
        - Current weather data
        - 5-day/3-hour forecasts
        - Geocoding for city search
        - Air quality data (where available)
        
        **Production Features:**
        - ✅ Error handling and retry logic
        - ✅ Response caching
        - ✅ Input validation
        - ✅ Logging and monitoring
        - ✅ Rate limiting protection
        - ✅ Mobile-responsive design
        """)
        
        st.divider()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **🔧 Configuration:**
            - API Provider: OpenWeatherMap
            - Update Frequency: Real-time
            - Cache Duration: 10 minutes
            - Max Retries: 3 attempts
            """)
        
        with col2:
            st.markdown("""
            **📊 Metrics Included:**
            - Temperature (current, min, max, feels like)
            - Humidity and pressure
            - Wind speed and direction
            - Weather conditions and visibility
            - Sunrise and sunset times
            """)
        
        st.info("💡 **Tip**: Use the sidebar to switch between different modes and adjust settings!")
        
        # API status check
        if st.button("🔍 Test API Connection"):
            try:
                with st.spinner("Testing API connection..."):
                    test_weather = st.session_state.weather_api.get_weather("London", "metric")
                st.success("✅ API connection successful!")
                st.json({"status": "connected", "test_city": "London", "timestamp": datetime.now().isoformat()})
            except Exception as e:
                st.error(f"❌ API connection failed: {str(e)}")
    
    # Footer
    st.divider()
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(
            "<div style='text-align: center; color: gray;'>"
            "🌤️ Advanced Weather App | Built with Streamlit & OpenWeatherMap API"
            "</div>", 
            unsafe_allow_html=True
        )

if __name__ == "__main__":
    main()