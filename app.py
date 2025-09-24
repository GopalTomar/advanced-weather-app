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

# Enhanced CSS with animations and better styling
def load_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global font styling */
    * {
        font-family: 'Inter', sans-serif !important;
        letter-spacing: -0.01em;
    }
    
    /* Main container styling */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }
    
    /* Header styling */
    .main h1 {
        font-size: 3rem !important;
        font-weight: 700 !important;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.5rem !important;
        animation: fadeInDown 1s ease-out;
    }
    
    .main h2 {
        font-size: 2rem !important;
        font-weight: 600 !important;
        color: #2c3e50 !important;
        margin: 1.5rem 0 1rem 0 !important;
        text-align: center;
    }
    
    .main h3 {
        font-size: 1.5rem !important;
        font-weight: 500 !important;
        color: #34495e !important;
        margin: 1rem 0 0.5rem 0 !important;
    }
    
    /* Subtitle styling */
    .subtitle {
        text-align: center;
        font-size: 1.1rem;
        color: #7f8c8d;
        font-weight: 400;
        margin-bottom: 2rem;
        font-style: italic;
        animation: fadeIn 1.5s ease-out;
    }
    
    /* Weather card with enhanced styling */
    .weather-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 20px;
        color: white;
        margin: 2rem 0;
        box-shadow: 0 20px 40px rgba(102, 126, 234, 0.3);
        border: 1px solid rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
        animation: slideInUp 0.8s ease-out;
    }
    
    .weather-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 25px 50px rgba(102, 126, 234, 0.4);
    }
    
    /* Metric cards with hover effects */
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        border-left: 4px solid #667eea;
        margin: 1rem 0;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.08);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(102, 126, 234, 0.1), transparent);
        transition: left 0.5s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.15);
        border-left-color: #764ba2;
    }
    
    .metric-card:hover::before {
        left: 100%;
    }
    
    /* Forecast cards */
    .forecast-card {
        background: linear-gradient(135deg, #a8e6cf 0%, #88d8c0 100%);
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        text-align: center;
        box-shadow: 0 8px 25px rgba(168, 230, 207, 0.3);
        transition: all 0.3s ease;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    .forecast-card:hover {
        transform: translateY(-3px) scale(1.02);
        box-shadow: 0 15px 35px rgba(168, 230, 207, 0.4);
    }
    
    /* Error and success cards */
    .error-card {
        background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        box-shadow: 0 8px 25px rgba(255, 107, 107, 0.3);
        animation: shake 0.5s ease-in-out;
    }
    
    .success-card {
        background: linear-gradient(135deg, #26de81 0%, #20bf6b 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        box-shadow: 0 8px 25px rgba(38, 222, 129, 0.3);
        animation: bounceIn 0.6s ease-out;
    }
    
    /* Button styling */
    .stButton > button {
        width: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.75rem 1.5rem !important;
        font-weight: 500 !important;
        font-size: 1rem !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3) !important;
        text-transform: none !important;
        letter-spacing: 0.01em !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4) !important;
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%) !important;
    }
    
    .stButton > button:active {
        transform: translateY(0) !important;
    }
    
    /* Quick city buttons */
    .quick-city-btn {
        background: rgba(102, 126, 234, 0.1) !important;
        color: #667eea !important;
        border: 2px solid #667eea !important;
        border-radius: 25px !important;
        padding: 0.5rem 1rem !important;
        margin: 0.25rem !important;
        transition: all 0.3s ease !important;
        font-weight: 500 !important;
    }
    
    .quick-city-btn:hover {
        background: #667eea !important;
        color: white !important;
        transform: scale(1.05) !important;
    }
    
    /* Input styling */
    .stTextInput > div > div > input {
        border-radius: 12px !important;
        border: 2px solid #e1e8ed !important;
        padding: 0.75rem !important;
        font-size: 1rem !important;
        transition: all 0.3s ease !important;
        background: rgba(255, 255, 255, 0.9) !important;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1) !important;
        background: white !important;
    }
    
    /* Selectbox styling */
    .stSelectbox > div > div > select {
        border-radius: 12px !important;
        border: 2px solid #e1e8ed !important;
        background: white !important;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #f8f9fa 0%, #e9ecef 100%);
    }
    
    .sidebar .sidebar-content {
        padding: 2rem 1rem;
    }
    
    /* Metric styling */
    [data-testid="metric-container"] {
        background: white;
        padding: 1rem;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
        border: 1px solid rgba(102, 126, 234, 0.1);
        transition: all 0.3s ease;
    }
    
    [data-testid="metric-container"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.12);
        border-color: #667eea;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background: linear-gradient(90deg, #667eea, #764ba2);
        color: white !important;
        border-radius: 12px;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    
    .streamlit-expanderHeader:hover {
        transform: translateX(5px);
    }
    
    /* Loading spinner styling */
    .stSpinner > div {
        border-color: #667eea #f3f3f3 #f3f3f3 #f3f3f3 !important;
    }
    
    /* Footer styling */
    .footer {
        margin-top: 3rem;
        padding: 2rem;
        text-align: center;
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        border-radius: 15px;
        border-top: 3px solid #667eea;
    }
    
    /* Animations */
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    
    @keyframes fadeInDown {
        from { 
            opacity: 0; 
            transform: translateY(-20px); 
        }
        to { 
            opacity: 1; 
            transform: translateY(0); 
        }
    }
    
    @keyframes slideInUp {
        from { 
            opacity: 0; 
            transform: translateY(30px); 
        }
        to { 
            opacity: 1; 
            transform: translateY(0); 
        }
    }
    
    @keyframes bounceIn {
        0% { transform: scale(0.3); opacity: 0; }
        50% { transform: scale(1.05); }
        70% { transform: scale(0.9); }
        100% { transform: scale(1); opacity: 1; }
    }
    
    @keyframes shake {
        0%, 100% { transform: translateX(0); }
        10%, 30%, 50%, 70%, 90% { transform: translateX(-5px); }
        20%, 40%, 60%, 80% { transform: translateX(5px); }
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .main h1 {
            font-size: 2rem !important;
        }
        
        .weather-card {
            padding: 1.5rem;
        }
        
        .metric-card {
            padding: 1rem;
        }
    }
    
    /* Hover effects for text elements */
    .hover-text {
        transition: all 0.3s ease;
        cursor: default;
    }
    
    .hover-text:hover {
        color: #667eea;
        transform: translateX(3px);
    }
    
    /* Glassmorphism effect */
    .glass-card {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 20px;
        padding: 2rem;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    }
    
    /* Progress bar styling */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #667eea, #764ba2);
        border-radius: 10px;
    }
    
    /* Alert styling */
    .stAlert {
        border-radius: 12px;
        border: none;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
    }
    </style>
    """, unsafe_allow_html=True)

def display_current_weather(weather_data, units):
    """Display current weather information with enhanced styling"""
    try:
        # Main weather info
        main = weather_data['main']
        weather = weather_data['weather'][0]
        wind = weather_data.get('wind', {})
        
        city_name = weather_data['name']
        country = weather_data['sys']['country']
        
        # Weather card with enhanced styling
        icon = get_weather_icon(weather['icon'])
        
        st.markdown(f"""
        <div class="weather-card">
            <h2 style="margin-bottom: 1.5rem; text-align: center; font-size: 2.2rem;">
                <span style="font-size: 3rem; margin-right: 1rem;">{icon}</span>
                {city_name}, {country}
            </h2>
            <div style="display: flex; align-items: center; justify-content: center; gap: 3rem; flex-wrap: wrap;">
                <div style="text-align: center;">
                    <div style="font-size: 4rem; font-weight: 700; margin-bottom: 0.5rem;">
                        {format_temperature(main['temp'], units)}
                    </div>
                    <div style="font-size: 1.3rem; opacity: 0.9;">
                        {capitalize_words(weather['description'])}
                    </div>
                </div>
                <div style="text-align: center; opacity: 0.9;">
                    <div style="font-size: 1.1rem; margin-bottom: 0.5rem;">Feels like</div>
                    <div style="font-size: 1.8rem; font-weight: 600;">
                        {format_temperature(main['feels_like'], units)}
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Weather advice with better styling
        advice = get_weather_advice(weather_data)
        st.info(f"💡 **Weather Tip**: {advice}")
        
        # Metrics in columns with enhanced spacing
        st.markdown("<div style='margin: 2rem 0;'>", unsafe_allow_html=True)
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
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Additional details with enhanced styling
        with st.expander("📋 Detailed Weather Information", expanded=False):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("""
                <div class="glass-card" style="margin: 1rem 0;">
                    <h4 style="color: #667eea; margin-bottom: 1rem;">🌡️ Temperature Details</h4>
                </div>
                """, unsafe_allow_html=True)
                
                st.write(f"**Current:** {format_temperature(main['temp'], units)}")
                st.write(f"**Feels like:** {format_temperature(main['feels_like'], units)}")
                st.write(f"**Min today:** {format_temperature(main['temp_min'], units)}")
                st.write(f"**Max today:** {format_temperature(main['temp_max'], units)}")
            
            with col2:
                st.markdown("""
                <div class="glass-card" style="margin: 1rem 0;">
                    <h4 style="color: #667eea; margin-bottom: 1rem;">🌤️ Weather Conditions</h4>
                </div>
                """, unsafe_allow_html=True)
                
                st.write(f"**Condition:** {capitalize_words(weather['description'])}")
                st.write(f"**Humidity:** {format_humidity(main['humidity'])}")
                st.write(f"**Pressure:** {format_pressure(main['pressure'])}")
                
                if 'visibility' in weather_data:
                    visibility_km = weather_data['visibility'] / 1000
                    st.write(f"**Visibility:** {visibility_km:.1f} km")
                
                if wind:
                    st.write(f"**Wind speed:** {format_wind_speed(wind.get('speed', 0), units)}")
                    if 'deg' in wind:
                        st.write(f"**Wind direction:** {wind['deg']}°")
        
        # Sun times with enhanced styling
        if 'sys' in weather_data:
            sys_data = weather_data['sys']
            timezone_offset = weather_data.get('timezone', 0)
            
            if 'sunrise' in sys_data and 'sunset' in sys_data:
                sunrise = format_time(sys_data['sunrise'], timezone_offset)
                sunset = format_time(sys_data['sunset'], timezone_offset)
                
                st.markdown("<div style='margin: 2rem 0;'>", unsafe_allow_html=True)
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("🌅 Sunrise", sunrise)
                with col2:
                    st.metric("🌇 Sunset", sunset)
                st.markdown("</div>", unsafe_allow_html=True)
        
        return True
        
    except KeyError as e:
        st.error(f"❌ Error displaying weather data: Missing field {e}")
        return False
    except Exception as e:
        st.error(f"❌ Error displaying weather data: {str(e)}")
        return False

def display_forecast(forecast_data, units):
    """Display weather forecast with enhanced styling"""
    try:
        forecast_list = forecast_data['list']
        city_name = forecast_data['city']['name']
        
        st.markdown(f"""
        <h2 style="text-align: center; color: #2c3e50; margin: 2rem 0;">
            📅 5-Day Forecast for <span style="color: #667eea;">{city_name}</span>
        </h2>
        """, unsafe_allow_html=True)
        
        # Process forecast data
        daily_data = {}
        hourly_temps = []
        hourly_times = []
        
        for item in forecast_list:
            dt = datetime.fromtimestamp(item['dt'])
            date_str = dt.strftime('%Y-%m-%d')
            
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
        
        # Enhanced temperature trend chart
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=hourly_times,
            y=hourly_temps,
            mode='lines+markers',
            name='Temperature',
            line=dict(color='#667eea', width=4),
            marker=dict(size=8, color='#764ba2'),
            fill='tonexty',
            fillcolor='rgba(102, 126, 234, 0.1)'
        ))
        
        fig.update_layout(
            title=f"🌡️ Temperature Trend - {city_name}",
            title_font=dict(size=20, color='#2c3e50'),
            xaxis_title="Time",
            yaxis_title=f"Temperature ({Config.UNITS_DISPLAY[units]['temp']})",
            hovermode='x unified',
            template='plotly_white',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(family='Inter, sans-serif'),
            margin=dict(t=60, b=40, l=40, r=40)
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Daily forecast cards with enhanced styling
        st.markdown("""
        <h3 style="text-align: center; color: #2c3e50; margin: 3rem 0 2rem 0;">
            📊 Daily Weather Summary
        </h3>
        """, unsafe_allow_html=True)
        
        for i, (date_str, data) in enumerate(list(daily_data.items())[:5]):
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            day_name = date_obj.strftime('%A, %B %d')
            
            # Enhanced forecast card
            col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 1])
            
            with col1:
                most_common_icon = max(set(data['icons']), key=data['icons'].count)
                icon = get_weather_icon(most_common_icon)
                most_common_condition = max(set(data['conditions']), key=data['conditions'].count)
                
                st.markdown(f"""
                <div class="forecast-card" style="text-align: left;">
                    <div style="font-weight: 600; font-size: 1.1rem; color: #2c3e50; margin-bottom: 0.5rem;">
                        {day_name}
                    </div>
                    <div style="font-size: 1.5rem; margin-bottom: 0.25rem;">{icon}</div>
                    <div style="color: #34495e; font-weight: 500;">
                        {capitalize_words(most_common_condition)}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                min_temp = min(data['temps'])
                max_temp = max(data['temps'])
                st.metric(
                    "🌡️ Range",
                    f"{max_temp:.0f}°/{min_temp:.0f}°",
                    help="High/Low temperature"
                )
            
            with col3:
                avg_humidity = sum(data['humidity']) / len(data['humidity'])
                st.metric("💧 Humidity", f"{avg_humidity:.0f}%")
            
            with col4:
                avg_wind = sum(data['wind_speed']) / len(data['wind_speed'])
                st.metric("🌪️ Wind", f"{avg_wind:.1f} {Config.UNITS_DISPLAY[units]['speed']}")
            
            with col5:
                temp_color = color_temp_by_range(max_temp)
                st.markdown(f"""
                <div style="
                    background: linear-gradient(135deg, {temp_color}, {temp_color}dd);
                    padding: 15px;
                    border-radius: 12px;
                    text-align: center;
                    color: white;
                    font-weight: 700;
                    font-size: 1.2rem;
                    box-shadow: 0 4px 15px rgba(0,0,0,0.2);
                    transition: transform 0.3s ease;
                " onmouseover="this.style.transform='scale(1.05)'" onmouseout="this.style.transform='scale(1)'">
                    {max_temp:.0f}°
                </div>
                """, unsafe_allow_html=True)
            
            if i < 4:  # Don't add divider after last item
                st.markdown("<hr style='margin: 2rem 0; border: none; height: 1px; background: linear-gradient(90deg, transparent, #e1e8ed, transparent);'>", unsafe_allow_html=True)
        
        return True
        
    except KeyError as e:
        st.error(f"❌ Error displaying forecast data: Missing field {e}")
        return False
    except Exception as e:
        st.error(f"❌ Error displaying forecast data: {str(e)}")
        return False

def display_comparison(weather_data1, weather_data2, units):
    """Display weather comparison with enhanced styling"""
    try:
        city1 = weather_data1['name']
        city2 = weather_data2['name']
        
        st.markdown(f"""
        <h2 style="text-align: center; color: #2c3e50; margin: 2rem 0;">
            ⚖️ Weather Comparison: <span style="color: #667eea;">{city1}</span> vs <span style="color: #764ba2;">{city2}</span>
        </h2>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2, gap="large")
        
        # City 1 with enhanced styling
        with col1:
            main1 = weather_data1['main']
            weather1 = weather_data1['weather'][0]
            icon1 = get_weather_icon(weather1['icon'])
            
            st.markdown(f"""
            <div class="weather-card" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
                <h3 style="text-align: center; margin-bottom: 1.5rem; color: white;">
                    {city1}, {weather_data1['sys']['country']}
                </h3>
                <div style="text-align: center;">
                    <div style="font-size: 4rem; margin-bottom: 1rem;">{icon1}</div>
                    <div style="font-size: 3rem; font-weight: 700; margin-bottom: 0.5rem;">
                        {format_temperature(main1['temp'], units)}
                    </div>
                    <div style="font-size: 1.2rem; opacity: 0.9;">
                        {capitalize_words(weather1['description'])}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Metrics for city 1
            st.metric("🌡️ Feels Like", format_temperature(main1['feels_like'], units))
            st.metric("💧 Humidity", format_humidity(main1['humidity']))
            st.metric("📊 Pressure", format_pressure(main1['pressure']))
        
        # City 2 with enhanced styling
        with col2:
            main2 = weather_data2['main']
            weather2 = weather_data2['weather'][0]
            icon2 = get_weather_icon(weather2['icon'])
            
            st.markdown(f"""
            <div class="weather-card" style="background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);">
                <h3 style="text-align: center; margin-bottom: 1.5rem; color: white;">
                    {city2}, {weather_data2['sys']['country']}
                </h3>
                <div style="text-align: center;">
                    <div style="font-size: 4rem; margin-bottom: 1rem;">{icon2}</div>
                    <div style="font-size: 3rem; font-weight: 700; margin-bottom: 0.5rem;">
                        {format_temperature(main2['temp'], units)}
                    </div>
                    <div style="font-size: 1.2rem; opacity: 0.9;">
                        {capitalize_words(weather2['description'])}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Metrics for city 2 with comparison deltas
            temp_diff = main2['temp'] - main1['temp']
            st.metric(
                "🌡️ Feels Like", 
                format_temperature(main2['feels_like'], units),
                delta=f"{temp_diff:+.1f}° vs {city1}"
            )
            
            humidity_diff = main2['humidity'] - main1['humidity']
            st.metric(
                "💧 Humidity", 
                format_humidity(main2['humidity']),
                delta=f"{humidity_diff:+d}% vs {city1}"
            )
            
            pressure_diff = main2['pressure'] - main1['pressure']
            st.metric(
                "📊 Pressure", 
                format_pressure(main2['pressure']),
                delta=f"{pressure_diff:+.1f} vs {city1}"
            )
        
        # Enhanced comparison chart
        comparison_data = {
            'City': [city1, city2],
            'Temperature': [main1['temp'], main2['temp']],
            'Feels Like': [main1['feels_like'], main2['feels_like']],
            'Humidity': [main1['humidity'], main2['humidity']],
            'Pressure': [main1['pressure'], main2['pressure']]
        }
        
        df = pd.DataFrame(comparison_data)
        
        # Temperature comparison chart with enhanced styling
        fig = px.bar(
            df, 
            x='City', 
            y='Temperature',
            title=f'🌡️ Temperature Comparison ({Config.UNITS_DISPLAY[units]["temp"]})',
            color='Temperature',
            color_continuous_scale='RdYlBu_r',
            text='Temperature'
        )
        
        fig.update_traces(
            texttemplate='%{text:.1f}°',
            textposition='outside',
            marker_line_color='rgba(102, 126, 234, 0.3)',
            marker_line_width=2
        )
        
        fig.update_layout(
            template='plotly_white',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(family='Inter, sans-serif'),
            title_font=dict(size=20, color='#2c3e50'),
            showlegend=False,
            margin=dict(t=60, b=40, l=40, r=40)
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        return True
        
    except Exception as e:
        st.error(f"❌ Error displaying comparison: {str(e)}")
        return False

def search_history_sidebar():
    """Display search history in sidebar with enhanced styling"""
    st.sidebar.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                color: white; padding: 1rem; border-radius: 10px; margin-bottom: 1rem;">
        <h3 style="margin: 0; text-align: center;">📝 Recent Searches</h3>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
    
    history = get_search_history()
    
    if history:
        for i, entry in enumerate(history[:5]):
            status_icon = "✅" if entry['success'] else "❌"
            st.sidebar.markdown(f"""
            <div style="background: white; padding: 0.75rem; border-radius: 8px; 
                        margin: 0.5rem 0; box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                        transition: transform 0.2s ease;"
                 onmouseover="this.style.transform='translateX(3px)'"
                 onmouseout="this.style.transform='translateX(0)'">
                <div style="font-weight: 500; color: #2c3e50;">
                    {status_icon} {entry['city']}
                </div>
                <div style="font-size: 0.8rem; color: #7f8c8d; margin-top: 0.25rem;">
                    🕒 {entry['timestamp']}
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.sidebar.markdown("""
        <div style="background: rgba(108, 117, 125, 0.1); padding: 1rem; 
                    border-radius: 8px; text-align: center; color: #6c757d;">
            No recent searches
        </div>
        """, unsafe_allow_html=True)

def export_data_section(weather_data, forecast_data=None):
    """Provide data export functionality with enhanced styling"""
    st.markdown("""
    <div style="background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); 
                padding: 2rem; border-radius: 15px; margin: 2rem 0; border: 1px solid #dee2e6;">
        <h3 style="text-align: center; color: #2c3e50; margin-bottom: 1.5rem;">
            📁 Export Weather Data
        </h3>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 Export Current Weather (JSON)", help="Download current weather data as JSON file"):
            weather_json = json.dumps(weather_data, indent=2, default=str)
            st.download_button(
                label="💾 Download JSON",
                data=weather_json,
                file_name=f"weather_{weather_data['name']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
    
    with col2:
        if forecast_data and st.button("📈 Export Forecast (CSV)", help="Download forecast data as CSV file"):
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
                label="💾 Download CSV",
                data=csv,
                file_name=f"forecast_{forecast_data['city']['name']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
    
    with col3:
        if st.button("📋 Copy Weather Summary", help="Generate a text summary of current weather"):
            if weather_data:
                summary = create_weather_summary(weather_data)
                st.code(summary, language=None)
                st.success("✅ Summary ready to copy!")

def create_quick_city_buttons():
    """Create enhanced quick access city buttons"""
    st.markdown("""
    <div style="margin: 1.5rem 0;">
        <h4 style="text-align: center; color: #2c3e50; margin-bottom: 1rem;">
            🚀 Quick Access Cities
        </h4>
    </div>
    """, unsafe_allow_html=True)
    
    quick_cities = ["London", "New York", "Tokyo", "Paris", "Sydney", "Mumbai", "Dubai"]
    cols = st.columns(len(quick_cities))
    
    selected_city = None
    for i, quick_city in enumerate(quick_cities):
        with cols[i]:
            if st.button(
                quick_city, 
                key=f"quick_{quick_city}",
                help=f"Get weather for {quick_city}"
            ):
                selected_city = quick_city
    
    return selected_city

def main():
    """Main application function with enhanced UI"""
    load_css()
    
    # Initialize session state
    if 'weather_api' not in st.session_state:
        st.session_state.weather_api = init_weather_api()
    
    if 'current_weather' not in st.session_state:
        st.session_state.current_weather = None
    
    if 'forecast_data' not in st.session_state:
        st.session_state.forecast_data = None
    
    # Enhanced app header
    st.markdown("""
    <div style="text-align: center; margin-bottom: 3rem;">
        <h1 style="margin-bottom: 0.5rem;">🌤️ Advanced Weather App</h1>
        <div class="subtitle">
            Get real-time weather data, forecasts, and comparisons for cities worldwide
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Enhanced sidebar configuration
    st.sidebar.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                color: white; padding: 1.5rem; border-radius: 15px; margin-bottom: 2rem;
                text-align: center;">
        <h2 style="margin: 0;">⚙️ Settings</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # Units selection with enhanced styling
    units = st.sidebar.selectbox(
        "🌡️ Temperature Units",
        options=["metric", "imperial"],
        format_func=lambda x: "🌡️ Celsius (°C)" if x == "metric" else "🌡️ Fahrenheit (°F)",
        key="units",
        help="Choose your preferred temperature unit"
    )
    
    # App mode selection with enhanced styling
    app_mode = st.sidebar.selectbox(
        "📱 App Mode",
        ["🏠 Current Weather", "📅 Weather Forecast", "⚖️ City Comparison", "🔍 City Search", "ℹ️ About"],
        help="Select the mode you want to use"
    )
    
    search_history_sidebar()
    
    # Main content based on selected mode
    if app_mode == "🏠 Current Weather":
        st.markdown("""
        <h2 style="text-align: center; color: #2c3e50; margin: 2rem 0;">
            🌡️ Current Weather Conditions
        </h2>
        """, unsafe_allow_html=True)
        
        # Enhanced city input section
        col1, col2 = st.columns([4, 1])
        
        with col1:
            city = st.text_input(
                "Enter city name:",
                placeholder="🏙️ e.g., London, New York, Tokyo",
                help="Enter the name of any city worldwide to get current weather"
            )
        
        with col2:
            search_button = st.button("🔍 Get Weather", type="primary", help="Search for weather data")
        
        # Quick city buttons
        selected_quick_city = create_quick_city_buttons()
        if selected_quick_city:
            city = selected_quick_city
            search_button = True
        
        # Weather display with enhanced error handling
        if search_button and city:
            if not validate_city_name(city):
                st.markdown("""
                <div class="error-card">
                    ❌ Please enter a valid city name (letters, spaces, and hyphens only)
                </div>
                """, unsafe_allow_html=True)
            else:
                try:
                    with st.spinner(f"🔍 Getting weather data for {city}..."):
                        progress_bar = st.progress(0)
                        for i in range(100):
                            time.sleep(0.01)
                            progress_bar.progress(i + 1)
                        
                        weather_data = st.session_state.weather_api.get_weather(city, units)
                        st.session_state.current_weather = weather_data
                        progress_bar.empty()
                    
                    if display_current_weather(weather_data, units):
                        st.markdown("""
                        <div class="success-card">
                            ✅ Weather data successfully updated for {city}!
                        </div>
                        """.format(city=city), unsafe_allow_html=True)
                        
                        export_data_section(weather_data)
                        
                except WeatherAPIError as e:
                    st.markdown(f"""
                    <div class="error-card">
                        ❌ {str(e)}
                    </div>
                    """, unsafe_allow_html=True)
                except Exception as e:
                    st.markdown(f"""
                    <div class="error-card">
                        ❌ An unexpected error occurred: {str(e)}
                    </div>
                    """, unsafe_allow_html=True)
        
        elif st.session_state.current_weather:
            st.info("📊 Showing cached weather data. Enter a city name to get fresh data.")
            display_current_weather(st.session_state.current_weather, units)
    
    elif app_mode == "📅 Weather Forecast":
        st.markdown("""
        <h2 style="text-align: center; color: #2c3e50; margin: 2rem 0;">
            📈 Weather Forecast
        </h2>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([3, 1, 1])
        
        with col1:
            city = st.text_input(
                "Enter city name for forecast:",
                placeholder="🏙️ e.g., London, Paris, Tokyo",
                help="Get detailed weather forecast for any city"
            )
        
        with col2:
            days = st.selectbox(
                "📅 Forecast days:", 
                [1, 2, 3, 4, 5], 
                index=2,
                help="Select number of days for forecast"
            )
        
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
                        export_data_section(None, forecast_data)
                        
                except WeatherAPIError as e:
                    st.error(f"❌ {str(e)}")
                except Exception as e:
                    st.error(f"❌ An unexpected error occurred: {str(e)}")
    
    elif app_mode == "⚖️ City Comparison":
        st.markdown("""
        <h2 style="text-align: center; color: #2c3e50; margin: 2rem 0;">
            🆚 City Weather Comparison
        </h2>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([3, 3, 1])
        
        with col1:
            city1 = st.text_input(
                "First city:", 
                placeholder="🏙️ e.g., London",
                help="Enter the first city for comparison"
            )
        
        with col2:
            city2 = st.text_input(
                "Second city:", 
                placeholder="🏙️ e.g., Paris",
                help="Enter the second city for comparison"
            )
        
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
        st.markdown("""
        <h2 style="text-align: center; color: #2c3e50; margin: 2rem 0;">
            🔍 City Search & Multiple Weather
        </h2>
        """, unsafe_allow_html=True)
        
        # City search section
        st.markdown("""
        <h3 style="color: #34495e; margin: 2rem 0 1rem 0;">
            🏙️ Search Cities
        </h3>
        """, unsafe_allow_html=True)
        
        search_query = st.text_input(
            "Search for cities:", 
            placeholder="🔍 e.g., London",
            help="Search for cities worldwide"
        )
        
        if search_query:
            try:
                cities = st.session_state.weather_api.search_cities(search_query, 10)
                
                if cities:
                    st.success(f"🎯 Found {len(cities)} cities matching '{search_query}'")
                    
                    for city in cities:
                        col1, col2, col3 = st.columns([3, 2, 1])
                        with col1:
                            country = city.get('country', 'Unknown')
                            state = city.get('state', '')
                            display_name = f"{city['name']}, {state + ', ' if state else ''}{country}"
                            
                            st.markdown(f"""
                            <div style="background: white; padding: 1rem; border-radius: 10px; 
                                        margin: 0.5rem 0; box-shadow: 0 4px 15px rgba(0,0,0,0.08);
                                        border-left: 4px solid #667eea;">
                                <div style="font-weight: 600; color: #2c3e50;">
                                    📍 {display_name}
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        with col2:
                            st.markdown(f"""
                            <div style="background: rgba(102, 126, 234, 0.1); padding: 0.75rem; 
                                        border-radius: 8px; text-align: center; margin: 0.5rem 0;">
                                <span style="color: #667eea; font-weight: 500;">
                                    📐 {city['lat']:.2f}, {city['lon']:.2f}
                                </span>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        with col3:
                            if st.button(f"🌤️ Weather", key=f"weather_{city['name']}_{city['lat']}"):
                                try:
                                    with st.spinner(f"Getting weather for {city['name']}..."):
                                        weather_data = st.session_state.weather_api.get_weather_by_coordinates(
                                            city['lat'], city['lon'], units
                                        )
                                        display_current_weather(weather_data, units)
                                except Exception as e:
                                    st.error(f"❌ Error: {str(e)}")
                else:
                    st.info("🔍 No cities found matching your search.")
            except Exception as e:
                st.error(f"❌ Search error: {str(e)}")
        
        st.markdown("<hr style='margin: 3rem 0; border: none; height: 2px; background: linear-gradient(90deg, transparent, #667eea, transparent);'>", unsafe_allow_html=True)
        
        # Multiple cities weather section
        st.markdown("""
        <h3 style="color: #34495e; margin: 2rem 0 1rem 0;">
            🌍 Multiple Cities Weather
        </h3>
        """, unsafe_allow_html=True)
        
        cities_input = st.text_area(
            "Enter multiple cities (one per line):",
            placeholder="🌍 London\n🗽 New York\n🗼 Tokyo\n🎭 Paris",
            height=120,
            help="Enter city names, one per line (max 10 cities)"
        )
        
        if st.button("🌐 Get All Weather Data", type="primary") and cities_input:
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
                        with st.expander(f"🌤️ Weather for {city}", expanded=False):
                            display_current_weather(weather_data, units)
                
                # Display errors
                if results['errors']:
                    st.markdown("""
                    <h4 style="color: #e74c3c; margin: 2rem 0 1rem 0;">
                        ❌ Failed Cities
                    </h4>
                    """, unsafe_allow_html=True)
                    for city, error in results['errors'].items():
                        st.error(f"🏙️ {city}: {error}")
            
            except Exception as e:
                st.error(f"❌ Error getting multiple cities data: {str(e)}")
    
    elif app_mode == "ℹ️ About":
        st.markdown("""
        <h2 style="text-align: center; color: #2c3e50; margin: 2rem 0;">
            ℹ️ About This Application
        </h2>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="glass-card" style="margin: 2rem 0;">
            <div style="text-align: center; margin-bottom: 2rem;">
                <h3 style="color: #667eea; margin-bottom: 1rem;">🌤️ Advanced Weather App</h3>
                <p style="font-size: 1.1rem; color: #6c757d; line-height: 1.6;">
                    A comprehensive weather application built with modern web technologies, 
                    providing real-time weather data and forecasts for cities worldwide.
                </p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Features section with enhanced styling
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <div style="background: white; padding: 2rem; border-radius: 15px; 
                        box-shadow: 0 8px 25px rgba(0,0,0,0.1); margin: 1rem 0;">
                <h4 style="color: #667eea; margin-bottom: 1rem;">✨ Features</h4>
                <ul style="line-height: 2; color: #495057;">
                    <li>🌡️ Real-time current weather data</li>
                    <li>📅 5-day weather forecasts with hourly details</li>
                    <li>⚖️ Side-by-side city weather comparisons</li>
                    <li>🔍 City search and multiple city weather</li>
                    <li>📊 Interactive charts and visualizations</li>
                    <li>📁 Data export (JSON/CSV)</li>
                    <li>📝 Search history tracking</li>
                    <li>🌡️ Multiple unit systems</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div style="background: white; padding: 2rem; border-radius: 15px; 
                        box-shadow: 0 8px 25px rgba(0,0,0,0.1); margin: 1rem 0;">
                <h4 style="color: #764ba2; margin-bottom: 1rem;">🛠️ Technical Stack</h4>
                <ul style="line-height: 2; color: #495057;">
                    <li><strong>Frontend:</strong> Streamlit</li>
                    <li><strong>API:</strong> OpenWeatherMap</li>
                    <li><strong>Charts:</strong> Plotly</li>
                    <li><strong>Data:</strong> Pandas</li>
                    <li><strong>HTTP:</strong> Requests</li>
                    <li><strong>Styling:</strong> Custom CSS</li>
                    <li><strong>Animations:</strong> CSS3</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        
        # Additional information
        st.markdown("""
        <div style="background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); 
                    padding: 2rem; border-radius: 15px; margin: 2rem 0; text-align: center;">
            <h4 style="color: #2c3e50; margin-bottom: 1rem;">💡 Pro Tips</h4>
            <p style="color: #6c757d; line-height: 1.6;">
                • Use the sidebar to switch between different modes and adjust settings<br>
                • Click on the quick access city buttons for instant weather data<br>
                • Export your weather data for offline analysis<br>
                • Compare weather between multiple cities for travel planning
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # API status check with enhanced styling
        if st.button("🔍 Test API Connection", help="Test the connection to weather API"):
            try:
                with st.spinner("Testing API connection..."):
                    test_weather = st.session_state.weather_api.get_weather("London", "metric")
                
                st.markdown("""
                <div class="success-card">
                    ✅ API connection successful!
                </div>
                """, unsafe_allow_html=True)
                
                st.json({
                    "status": "connected", 
                    "test_city": "London", 
                    "timestamp": datetime.now().isoformat(),
                    "response_time": "< 1s"
                })
            except Exception as e:
                st.markdown(f"""
                <div class="error-card">
                    ❌ API connection failed: {str(e)}
                </div>
                """, unsafe_allow_html=True)
    
    # Enhanced footer
    st.markdown("<div style='margin-top: 4rem;'>", unsafe_allow_html=True)
    st.markdown("""
    <div class="footer">
        <div style="display: flex; justify-content: center; align-items: center; gap: 2rem; flex-wrap: wrap;">
            <div style="text-align: center;">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">🌤️</div>
                <div style="font-weight: 600; color: #2c3e50;">Advanced Weather App</div>
                <div style="color: #6c757d; font-size: 0.9rem;">Built with ❤️ using Streamlit</div>
            </div>
            <div style="text-align: center; color: #6c757d;">
                <div>📡 Powered by OpenWeatherMap API</div>
                <div>🚀 Real-time weather data worldwide</div>
            </div>
        </div>
        <div style="margin-top: 1.5rem; padding-top: 1.5rem; border-top: 1px solid #dee2e6; 
                    text-align: center; color: #6c757d; font-size: 0.9rem;">
            © 2024 Advanced Weather App | Made for weather enthusiasts
        </div>
    </div>
