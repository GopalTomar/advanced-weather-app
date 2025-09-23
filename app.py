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

# Enhanced Custom CSS with Dark Theme, Animations, and Glassmorphism
def load_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global Styles */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        min-height: 100vh;
        font-family: 'Inter', sans-serif;
        position: relative;
        overflow-x: hidden;
    }
    
    /* Animated Background Particles */
    .stApp::before {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: 
            radial-gradient(circle at 20% 20%, rgba(255, 255, 255, 0.1) 1px, transparent 1px),
            radial-gradient(circle at 80% 80%, rgba(255, 255, 255, 0.1) 1px, transparent 1px),
            radial-gradient(circle at 40% 60%, rgba(255, 255, 255, 0.05) 2px, transparent 2px);
        background-size: 100px 100px, 150px 150px, 80px 80px;
        animation: float 20s ease-in-out infinite;
        z-index: -1;
        pointer-events: none;
    }
    
    @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
    }
    
    /* Sidebar Styling */
    .css-1d391kg {
        background: rgba(17, 25, 40, 0.8) !important;
        backdrop-filter: blur(20px);
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    /* Main Content Area */
    .main .block-container {
        padding-top: 2rem;
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(20px);
        border-radius: 20px;
        margin: 1rem;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    }
    
    /* Animated Title */
    .main-title {
        background: linear-gradient(45deg, #667eea, #764ba2, #f093fb);
        background-size: 300% 300%;
        background-clip: text;
        -webkit-background-clip: text;
        color: transparent;
        animation: gradientShift 3s ease infinite;
        text-align: center;
        font-size: 3.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        text-shadow: 0 0 30px rgba(255, 255, 255, 0.3);
    }
    
    @keyframes gradientShift {
        0%, 100% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
    }
    
    /* Subtitle with typing animation */
    .subtitle {
        color: rgba(255, 255, 255, 0.8);
        text-align: center;
        font-size: 1.2rem;
        margin-bottom: 2rem;
        animation: fadeInUp 1s ease-out 0.5s both;
    }
    
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    /* Glassmorphism Weather Cards */
    .weather-card {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.15), rgba(255, 255, 255, 0.05));
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        padding: 2rem;
        border-radius: 20px;
        color: white;
        margin: 1.5rem 0;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
        animation: slideInUp 0.6s ease-out;
    }
    
    .weather-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
        transition: left 0.5s;
    }
    
    .weather-card:hover {
        transform: translateY(-5px) scale(1.02);
        box-shadow: 0 12px 48px rgba(0, 0, 0, 0.2);
        border: 1px solid rgba(255, 255, 255, 0.3);
    }
    
    .weather-card:hover::before {
        left: 100%;
    }
    
    @keyframes slideInUp {
        from {
            opacity: 0;
            transform: translateY(50px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    /* Enhanced Metric Cards */
    .metric-card {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        padding: 1.5rem;
        border-radius: 15px;
        border: 1px solid rgba(255, 255, 255, 0.2);
        margin: 0.5rem 0;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    
    .metric-card:hover {
        transform: translateY(-3px);
        background: rgba(255, 255, 255, 0.15);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
    }
    
    /* Animated Buttons */
    .stButton > button {
        background: linear-gradient(45deg, #667eea, #764ba2);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        position: relative;
        overflow: hidden;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.6);
        background: linear-gradient(45deg, #764ba2, #667eea);
    }
    
    .stButton > button:active {
        transform: translateY(0);
    }
    
    /* Quick Access Buttons */
    .quick-city-btn {
        background: rgba(255, 255, 255, 0.1) !important;
        color: white !important;
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
        border-radius: 20px !important;
        padding: 0.5rem 1.5rem !important;
        margin: 0.25rem !important;
        transition: all 0.3s ease !important;
        backdrop-filter: blur(10px) !important;
    }
    
    .quick-city-btn:hover {
        background: rgba(255, 255, 255, 0.2) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2) !important;
    }
    
    /* Input Fields */
    .stTextInput > div > div > input {
        background: rgba(255, 255, 255, 0.1);
        color: white;
        border: 1px solid rgba(255, 255, 255, 0.3);
        border-radius: 15px;
        padding: 0.75rem 1rem;
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus {
        border: 2px solid #667eea;
        background: rgba(255, 255, 255, 0.15);
        box-shadow: 0 0 20px rgba(102, 126, 234, 0.3);
    }
    
    /* Forecast Cards */
    .forecast-card {
        background: linear-gradient(135deg, rgba(168, 230, 207, 0.2), rgba(127, 205, 205, 0.2));
        backdrop-filter: blur(15px);
        padding: 1.5rem;
        border-radius: 15px;
        margin: 0.5rem 0;
        text-align: center;
        border: 1px solid rgba(255, 255, 255, 0.2);
        transition: all 0.3s ease;
        animation: fadeInScale 0.5s ease-out;
    }
    
    .forecast-card:hover {
        transform: scale(1.05);
        background: linear-gradient(135deg, rgba(168, 230, 207, 0.3), rgba(127, 205, 205, 0.3));
    }
    
    @keyframes fadeInScale {
        from {
            opacity: 0;
            transform: scale(0.8);
        }
        to {
            opacity: 1;
            transform: scale(1);
        }
    }
    
    /* Success and Error Cards */
    .success-card {
        background: linear-gradient(135deg, rgba(0, 184, 148, 0.2), rgba(0, 160, 133, 0.2));
        color: #00b894;
        padding: 1rem;
        border-radius: 15px;
        margin: 1rem 0;
        border: 1px solid rgba(0, 184, 148, 0.3);
        backdrop-filter: blur(10px);
        animation: slideInRight 0.5s ease-out;
    }
    
    .error-card {
        background: linear-gradient(135deg, rgba(255, 118, 117, 0.2), rgba(214, 48, 49, 0.2));
        color: #ff7675;
        padding: 1rem;
        border-radius: 15px;
        margin: 1rem 0;
        border: 1px solid rgba(255, 118, 117, 0.3);
        backdrop-filter: blur(10px);
        animation: slideInRight 0.5s ease-out;
    }
    
    @keyframes slideInRight {
        from {
            opacity: 0;
            transform: translateX(30px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    /* Selectbox Styling */
    .stSelectbox > div > div {
        background: rgba(255, 255, 255, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.3);
        border-radius: 15px;
        backdrop-filter: blur(10px);
    }
    
    /* Sidebar Elements */
    .css-1d391kg .stSelectbox > div > div,
    .css-1d391kg .stTextInput > div > div > input {
        background: rgba(255, 255, 255, 0.1);
        color: white;
        border: 1px solid rgba(255, 255, 255, 0.3);
    }
    
    /* Hover Text Effects */
    .hover-glow {
        transition: all 0.3s ease;
        cursor: pointer;
    }
    
    .hover-glow:hover {
        color: #667eea;
        text-shadow: 0 0 10px rgba(102, 126, 234, 0.5);
        transform: scale(1.05);
    }
    
    /* Loading Animation */
    .loading-weather {
        display: flex;
        justify-content: center;
        align-items: center;
        padding: 2rem;
    }
    
    .weather-spinner {
        width: 60px;
        height: 60px;
        border: 3px solid rgba(255, 255, 255, 0.3);
        border-top: 3px solid #667eea;
        border-radius: 50%;
        animation: spin 1s linear infinite;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    /* Metric Value Styling */
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        background: linear-gradient(45deg, #667eea, #f093fb);
        background-clip: text;
        -webkit-background-clip: text;
        color: transparent;
        text-shadow: 0 0 10px rgba(255, 255, 255, 0.3);
    }
    
    /* Weather Icons Animation */
    .weather-icon {
        font-size: 4rem;
        animation: bounce 2s ease-in-out infinite;
        filter: drop-shadow(0 0 10px rgba(255, 255, 255, 0.3));
    }
    
    @keyframes bounce {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-10px); }
    }
    
    /* Chart Containers */
    .chart-container {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(15px);
        border-radius: 20px;
        padding: 1rem;
        margin: 1rem 0;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    /* Responsive Design */
    @media (max-width: 768px) {
        .main-title {
            font-size: 2.5rem;
        }
        
        .weather-card {
            padding: 1rem;
            margin: 1rem 0;
        }
        
        .metric-card {
            padding: 1rem;
        }
    }
    
    /* Tab Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: rgba(255, 255, 255, 0.1);
        border-radius: 15px;
        color: white;
        font-weight: 600;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        transition: all 0.3s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background-color: rgba(255, 255, 255, 0.2);
        transform: translateY(-2px);
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(45deg, #667eea, #764ba2);
        color: white;
    }
    
    /* Expander Styling */
    .streamlit-expanderHeader {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 15px;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        color: white;
        font-weight: 600;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        color: rgba(255, 255, 255, 0.6);
        padding: 2rem;
        margin-top: 3rem;
        border-top: 1px solid rgba(255, 255, 255, 0.1);
        background: rgba(0, 0, 0, 0.1);
        backdrop-filter: blur(10px);
    }
    </style>
    """, unsafe_allow_html=True)

def display_current_weather(weather_data, units):
    """Display current weather information with enhanced animations"""
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
            <h2 style="margin-bottom: 1rem; text-align: center;">
                <span class="weather-icon">{icon}</span>
                <span class="hover-glow">{city_name}, {country}</span>
            </h2>
            <div style="display: flex; align-items: center; justify-content: center; gap: 3rem; flex-wrap: wrap;">
                <div class="metric-value" style="text-align: center;">
                    {format_temperature(main['temp'], units)}
                </div>
                <div style="text-align: center;">
                    <p style="font-size: 1.4rem; margin: 0; color: rgba(255,255,255,0.9);">{capitalize_words(weather['description'])}</p>
                    <p style="margin: 0.5rem 0 0 0; opacity: 0.8;">Feels like {format_temperature(main['feels_like'], units)}</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Weather advice with enhanced styling
        advice = get_weather_advice(weather_data)
        st.markdown(f"""
        <div class="success-card">
            <strong>💡 Weather Advice:</strong> {advice}
        </div>
        """, unsafe_allow_html=True)
        
        # Metrics in columns with animations
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div style="text-align: center;">
                    <div style="font-size: 2rem; margin-bottom: 0.5rem;">🌡️</div>
                    <div style="font-size: 1.5rem; font-weight: 600; color: #667eea;">
                        {format_temperature(main['temp'], units)}
                    </div>
                    <div style="font-size: 0.9rem; opacity: 0.8;">Temperature</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <div style="text-align: center;">
                    <div style="font-size: 2rem; margin-bottom: 0.5rem;">💧</div>
                    <div style="font-size: 1.5rem; font-weight: 600; color: #00b894;">
                        {format_humidity(main['humidity'])}
                    </div>
                    <div style="font-size: 0.9rem; opacity: 0.8;">Humidity</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <div style="text-align: center;">
                    <div style="font-size: 2rem; margin-bottom: 0.5rem;">🌪️</div>
                    <div style="font-size: 1.5rem; font-weight: 600; color: #fd79a8;">
                        {format_wind_speed(wind.get('speed', 0), units)}
                    </div>
                    <div style="font-size: 0.9rem; opacity: 0.8;">Wind Speed</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="metric-card">
                <div style="text-align: center;">
                    <div style="font-size: 2rem; margin-bottom: 0.5rem;">📊</div>
                    <div style="font-size: 1.5rem; font-weight: 600; color: #fdcb6e;">
                        {format_pressure(main['pressure'])}
                    </div>
                    <div style="font-size: 0.9rem; opacity: 0.8;">Pressure</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Additional details in expandable section
        with st.expander("📋 Detailed Weather Information", expanded=False):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("""
                <div style="color: rgba(255,255,255,0.9);">
                <h4 style="color: #667eea;">🌡️ Temperature Details</h4>
                """, unsafe_allow_html=True)
                st.write(f"• **Current**: {format_temperature(main['temp'], units)}")
                st.write(f"• **Feels like**: {format_temperature(main['feels_like'], units)}")
                st.write(f"• **Min today**: {format_temperature(main['temp_min'], units)}")
                st.write(f"• **Max today**: {format_temperature(main['temp_max'], units)}")
                st.markdown("</div>", unsafe_allow_html=True)
            
            with col2:
                st.markdown("""
                <div style="color: rgba(255,255,255,0.9);">
                <h4 style="color: #00b894;">🌤️ Weather Conditions</h4>
                """, unsafe_allow_html=True)
                st.write(f"• **Condition**: {capitalize_words(weather['description'])}")
                st.write(f"• **Humidity**: {format_humidity(main['humidity'])}")
                st.write(f"• **Pressure**: {format_pressure(main['pressure'])}")
                if 'visibility' in weather_data:
                    visibility_km = weather_data['visibility'] / 1000
                    st.write(f"• **Visibility**: {visibility_km:.1f} km")
                
                if wind:
                    st.write(f"• **Wind speed**: {format_wind_speed(wind.get('speed', 0), units)}")
                    if 'deg' in wind:
                        st.write(f"• **Wind direction**: {wind['deg']}°")
                st.markdown("</div>", unsafe_allow_html=True)
        
        # Sun times with enhanced styling
        if 'sys' in weather_data:
            sys_data = weather_data['sys']
            timezone_offset = weather_data.get('timezone', 0)
            
            if 'sunrise' in sys_data and 'sunset' in sys_data:
                sunrise = format_time(sys_data['sunrise'], timezone_offset)
                sunset = format_time(sys_data['sunset'], timezone_offset)
                
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div style="text-align: center;">
                            <div style="font-size: 2rem; margin-bottom: 0.5rem;">🌅</div>
                            <div style="font-size: 1.2rem; font-weight: 600; color: #fdcb6e;">
                                {sunrise}
                            </div>
                            <div style="font-size: 0.9rem; opacity: 0.8;">Sunrise</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div style="text-align: center;">
                            <div style="font-size: 2rem; margin-bottom: 0.5rem;">🌇</div>
                            <div style="font-size: 1.2rem; font-weight: 600; color: #e17055;">
                                {sunset}
                            </div>
                            <div style="font-size: 0.9rem; opacity: 0.8;">Sunset</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        
        return True
        
    except KeyError as e:
        st.markdown(f"""
        <div class="error-card">
            <strong>❌ Error:</strong> Missing weather data field: {e}
        </div>
        """, unsafe_allow_html=True)
        return False
    except Exception as e:
        st.markdown(f"""
        <div class="error-card">
            <strong>❌ Error:</strong> {str(e)}
        </div>
        """, unsafe_allow_html=True)
        return False

def display_forecast(forecast_data, units):
    """Display weather forecast with enhanced visuals"""
    try:
        forecast_list = forecast_data['list']
        city_name = forecast_data['city']['name']
        
        st.markdown(f"""
        <h2 style="color: white; text-align: center; margin: 2rem 0;">
            📅 5-Day Forecast for <span class="hover-glow">{city_name}</span>
        </h2>
        """, unsafe_allow_html=True)
        
        # Process forecast data
        daily_data = {}
        hourly_temps = []
        hourly_times = []
        
        for item in forecast_list:
            dt = datetime.fromtimestamp(item['dt'])
            date_str = dt.strftime('%Y-%m-%d')
            
            hourly_temps.append(item['main']['temp'])
            hourly_times.append(dt)
            
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
            line=dict(color='#667eea', width=4, shape='spline'),
            marker=dict(size=8, color='#764ba2', line=dict(width=2, color='white')),
            fill='tonexty',
            fillcolor='rgba(102, 126, 234, 0.1)'
        ))
        
        fig.update_layout(
            title={
                'text': f"🌡️ Temperature Trend - {city_name}",
                'font': {'size': 20, 'color': 'white'},
                'x': 0.5
            },
            xaxis_title="Time",
            yaxis_title=f"Temperature ({Config.UNITS_DISPLAY[units]['temp']})",
            hovermode='x unified',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            xaxis=dict(gridcolor='rgba(255,255,255,0.1)'),
            yaxis=dict(gridcolor='rgba(255,255,255,0.1)')
        )
        
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Daily forecast cards with enhanced animations
        st.markdown("""
        <h3 style="color: white; text-align: center; margin: 2rem 0;">
            📊 Daily Weather Summary
        </h3>
        """, unsafe_allow_html=True)
        
        for i, (date_str, data) in enumerate(list(daily_data.items())[:5]):
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            day_name = date_obj.strftime('%A, %B %d')
            
            # Most common weather condition and icon
            most_common_icon = max(set(data['icons']), key=data['icons'].count)
            icon = get_weather_icon(most_common_icon)
            most_common_condition = max(set(data['conditions']), key=data['conditions'].count)
            
            min_temp = min(data['temps'])
            max_temp = max(data['temps'])
            avg_humidity = sum(data['humidity']) / len(data['humidity'])
            avg_wind = sum(data['wind_speed']) / len(data['wind_speed'])
            
            # Enhanced forecast card with animation delay
            st.markdown(f"""
            <div class="forecast-card" style="animation-delay: {i * 0.1}s;">
                <div style="display: grid; grid-template-columns: 2fr 1fr 1fr 1fr 1fr; gap: 1rem; align-items: center;">
                    <div style="text-align: left;">
                        <div style="font-size: 1.8rem; margin-bottom: 0.5rem;">{icon}</div>
                        <div style="font-weight: 600; font-size: 1.1rem; color: white;">{day_name}</div>
                        <div style="opacity: 0.8; font-size: 0.9rem;">{capitalize_words(most_common_condition)}</div>
                    </div>
                    <div style="text-align: center;">
                        <div style="font-size: 1.4rem; font-weight: 600; color: #667eea;">{max_temp:.0f}°</div>
                        <div style="font-size: 1rem; opacity: 0.7;">{min_temp:.0f}°</div>
                        <div style="font-size: 0.8rem; opacity: 0.6;">High/Low</div>
                    </div>
                    <div style="text-align: center;">
                        <div style="font-size: 1.2rem; color: #00b894;">💧</div>
                        <div style="font-size: 1rem; font-weight: 500;">{avg_humidity:.0f}%</div>
                        <div style="font-size: 0.8rem; opacity: 0.6;">Humidity</div>
                    </div>
                    <div style="text-align: center;">
                        <div style="font-size: 1.2rem; color: #fd79a8;">🌪️</div>
                        <div style="font-size: 1rem; font-weight: 500;">{avg_wind:.1f}</div>
                        <div style="font-size: 0.8rem; opacity: 0.6;">{Config.UNITS_DISPLAY[units]['speed']}</div>
                    </div>
                    <div style="text-align: center;">
                        <div style="background: linear-gradient(45deg, {color_temp_by_range(max_temp)}, rgba(255,255,255,0.1)); 
                                    padding: 10px; border-radius: 50%; width: 50px; height: 50px; margin: 0 auto;
                                    display: flex; align-items: center; justify-content: center; 
                                    font-weight: bold; color: white; font-size: 1.1rem;
                                    box-shadow: 0 4px 15px rgba(0,0,0,0.2);">
                            {max_temp:.0f}°
                        </div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            if i < 4:  # Don't add divider after last item
                st.markdown('<div style="height: 0.5rem;"></div>', unsafe_allow_html=True)
        
        return True
        
    except KeyError as e:
        st.markdown(f"""
        <div class="error-card">
            <strong>❌ Error:</strong> Missing forecast data field: {e}
        </div>
        """, unsafe_allow_html=True)
        return False
    except Exception as e:
        st.markdown(f"""
        <div class="error-card">
            <strong>❌ Error:</strong> {str(e)}
        </div>
        """, unsafe_allow_html=True)
        return False

def display_comparison(weather_data1, weather_data2, units):
    """Display enhanced weather comparison between two cities"""
    try:
        city1 = weather_data1['name']
        city2 = weather_data2['name']
        
        st.markdown(f"""
        <h2 style="color: white; text-align: center; margin: 2rem 0;">
            ⚖️ Weather Battle: <span class="hover-glow">{city1}</span> vs <span class="hover-glow">{city2}</span>
        </h2>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        # City 1
        with col1:
            main1 = weather_data1['main']
            weather1 = weather_data1['weather'][0]
            icon1 = get_weather_icon(weather1['icon'])
            
            st.markdown(f"""
            <div class="weather-card" style="margin-right: 0.5rem;">
                <h3 style="text-align: center; margin-bottom: 1.5rem; color: #667eea;">
                    {city1}, {weather_data1['sys']['country']}
                </h3>
                <div style="text-align: center; margin-bottom: 1.5rem;">
                    <div class="weather-icon" style="font-size: 3rem; margin-bottom: 1rem;">{icon1}</div>
                    <div class="metric-value" style="font-size: 2.5rem; margin-bottom: 0.5rem;">
                        {format_temperature(main1['temp'], units)}
                    </div>
                    <p style="font-size: 1.1rem; margin: 0; color: rgba(255,255,255,0.9);">
                        {capitalize_words(weather1['description'])}
                    </p>
                </div>
                
                <div style="display: grid; gap: 1rem;">
                    <div class="metric-card">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <span>🌡️ Feels Like</span>
                            <span style="font-weight: 600; color: #667eea;">
                                {format_temperature(main1['feels_like'], units)}
                            </span>
                        </div>
                    </div>
                    <div class="metric-card">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <span>💧 Humidity</span>
                            <span style="font-weight: 600; color: #00b894;">
                                {format_humidity(main1['humidity'])}
                            </span>
                        </div>
                    </div>
                    <div class="metric-card">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <span>📊 Pressure</span>
                            <span style="font-weight: 600; color: #fdcb6e;">
                                {format_pressure(main1['pressure'])}
                            </span>
                        </div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # City 2 with comparison deltas
        with col2:
            main2 = weather_data2['main']
            weather2 = weather_data2['weather'][0]
            icon2 = get_weather_icon(weather2['icon'])
            
            # Calculate differences
            temp_diff = main2['temp'] - main1['temp']
            feels_like_diff = main2['feels_like'] - main1['feels_like']
            humidity_diff = main2['humidity'] - main1['humidity']
            pressure_diff = main2['pressure'] - main1['pressure']
            
            # Determine colors based on differences
            temp_color = "#e74c3c" if temp_diff > 0 else "#3498db" if temp_diff < 0 else "#95a5a6"
            feels_color = "#e74c3c" if feels_like_diff > 0 else "#3498db" if feels_like_diff < 0 else "#95a5a6"
            humidity_color = "#e74c3c" if humidity_diff > 0 else "#3498db" if humidity_diff < 0 else "#95a5a6"
            pressure_color = "#e74c3c" if pressure_diff > 0 else "#3498db" if pressure_diff < 0 else "#95a5a6"
            
            st.markdown(f"""
            <div class="weather-card" style="margin-left: 0.5rem;">
                <h3 style="text-align: center; margin-bottom: 1.5rem; color: #764ba2;">
                    {city2}, {weather_data2['sys']['country']}
                </h3>
                <div style="text-align: center; margin-bottom: 1.5rem;">
                    <div class="weather-icon" style="font-size: 3rem; margin-bottom: 1rem;">{icon2}</div>
                    <div class="metric-value" style="font-size: 2.5rem; margin-bottom: 0.5rem;">
                        {format_temperature(main2['temp'], units)}
                    </div>
                    <p style="font-size: 1.1rem; margin: 0; color: rgba(255,255,255,0.9);">
                        {capitalize_words(weather2['description'])}
                    </p>
                    <div style="font-size: 0.9rem; color: {temp_color}; font-weight: 600; margin-top: 0.5rem;">
                        {temp_diff:+.1f}° vs {city1}
                    </div>
                </div>
                
                <div style="display: grid; gap: 1rem;">
                    <div class="metric-card">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <span>🌡️ Feels Like</span>
                            <div style="text-align: right;">
                                <div style="font-weight: 600; color: #764ba2;">
                                    {format_temperature(main2['feels_like'], units)}
                                </div>
                                <div style="font-size: 0.8rem; color: {feels_color};">
                                    {feels_like_diff:+.1f}°
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="metric-card">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <span>💧 Humidity</span>
                            <div style="text-align: right;">
                                <div style="font-weight: 600; color: #00b894;">
                                    {format_humidity(main2['humidity'])}
                                </div>
                                <div style="font-size: 0.8rem; color: {humidity_color};">
                                    {humidity_diff:+d}%
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="metric-card">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <span>📊 Pressure</span>
                            <div style="text-align: right;">
                                <div style="font-weight: 600; color: #fdcb6e;">
                                    {format_pressure(main2['pressure'])}
                                </div>
                                <div style="font-size: 0.8rem; color: {pressure_color};">
                                    {pressure_diff:+.1f}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Enhanced comparison chart
        comparison_data = {
            'City': [city1, city2],
            'Temperature': [main1['temp'], main2['temp']],
            'Feels Like': [main1['feels_like'], main2['feels_like']],
            'Humidity': [main1['humidity'], main2['humidity']],
            'Pressure': [main1['pressure'], main2['pressure']]
        }
        
        df = pd.DataFrame(comparison_data)
        
        # Multi-metric comparison chart
        fig = go.Figure()
        
        # Temperature bars
        fig.add_trace(go.Bar(
            name='Temperature',
            x=df['City'],
            y=df['Temperature'],
            marker_color=['#667eea', '#764ba2'],
            text=df['Temperature'].round(1),
            textposition='auto',
        ))
        
        fig.update_layout(
            title={
                'text': f'🌡️ Temperature Comparison ({Config.UNITS_DISPLAY[units]["temp"]})',
                'font': {'size': 20, 'color': 'white'},
                'x': 0.5
            },
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            xaxis=dict(gridcolor='rgba(255,255,255,0.1)'),
            yaxis=dict(gridcolor='rgba(255,255,255,0.1)'),
            showlegend=False
        )
        
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Winner announcement
        if temp_diff > 2:
            winner_msg = f"🔥 {city2} is significantly warmer than {city1}!"
        elif temp_diff < -2:
            winner_msg = f"❄️ {city1} is significantly cooler than {city2}!"
        else:
            winner_msg = f"🤝 {city1} and {city2} have similar temperatures!"
        
        st.markdown(f"""
        <div class="success-card" style="text-align: center; font-size: 1.2rem;">
            <strong>{winner_msg}</strong>
        </div>
        """, unsafe_allow_html=True)
        
        return True
        
    except Exception as e:
        st.markdown(f"""
        <div class="error-card">
            <strong>❌ Error:</strong> {str(e)}
        </div>
        """, unsafe_allow_html=True)
        return False

def search_history_sidebar():
    """Display search history in enhanced sidebar"""
    st.sidebar.markdown("""
    <h3 style="color: white; margin-bottom: 1rem;">📝 Recent Searches</h3>
    """, unsafe_allow_html=True)
    
    history = get_search_history()
    
    if history:
        for i, entry in enumerate(history[:5]):
            status_icon = "✅" if entry['success'] else "❌"
            st.sidebar.markdown(f"""
            <div style="background: rgba(255, 255, 255, 0.1); 
                        padding: 0.5rem; margin: 0.5rem 0; border-radius: 10px;
                        border-left: 3px solid {'#00b894' if entry['success'] else '#e74c3c'};">
                <div style="font-weight: 600;">{status_icon} {entry['city']}</div>
                <div style="font-size: 0.8rem; opacity: 0.7;">🕒 {entry['timestamp']}</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.sidebar.markdown("""
        <div style="text-align: center; color: rgba(255, 255, 255, 0.6); padding: 1rem;">
            No recent searches
        </div>
        """, unsafe_allow_html=True)

def export_data_section(weather_data, forecast_data=None):
    """Enhanced data export functionality"""
    st.markdown("""
    <h3 style="color: white; text-align: center; margin: 2rem 0;">
        📁 Export Weather Data
    </h3>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 Export Current Weather (JSON)", key="export_json"):
            weather_json = json.dumps(weather_data, indent=2, default=str)
            st.download_button(
                label="⬇️ Download JSON",
                data=weather_json,
                file_name=f"weather_{weather_data['name']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
    
    with col2:
        if forecast_data and st.button("📈 Export Forecast (CSV)", key="export_csv"):
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
                label="⬇️ Download CSV",
                data=csv,
                file_name=f"forecast_{forecast_data['city']['name']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
    
    with col3:
        if st.button("📋 Copy Weather Summary", key="export_summary"):
            if weather_data:
                summary = create_weather_summary(weather_data)
                st.code(summary, language=None)
                st.markdown("""
                <div class="success-card">
                    <strong>✅ Summary ready to copy!</strong>
                </div>
                """, unsafe_allow_html=True)

def main():
    """Enhanced main application function"""
    load_css()
    
    # Initialize session state
    if 'weather_api' not in st.session_state:
        st.session_state.weather_api = init_weather_api()
    
    if 'current_weather' not in st.session_state:
        st.session_state.current_weather = None
    
    if 'forecast_data' not in st.session_state:
        st.session_state.forecast_data = None
    
    # Enhanced app header with animations
    st.markdown("""
    <div class="main-title">
        🌤️ Advanced Weather App
    </div>
    <div class="subtitle">
        Get real-time weather data, forecasts, and comparisons for cities worldwide
    </div>
    """, unsafe_allow_html=True)
    
    # Enhanced sidebar configuration
    st.sidebar.markdown("""
    <h2 style="color: white; text-align: center; margin-bottom: 1.5rem;">
        ⚙️ Settings
    </h2>
    """, unsafe_allow_html=True)
    
    # Units selection with enhanced styling
    units = st.sidebar.selectbox(
        "🌡️ Temperature Units",
        options=["metric", "imperial"],
        format_func=lambda x: "Celsius (°C)" if x == "metric" else "Fahrenheit (°F)",
        key="units"
    )
    
    # App mode selection with enhanced styling
    app_mode = st.sidebar.selectbox(
        "📱 App Mode",
        ["🏠 Current Weather", "📅 Weather Forecast", "⚖️ City Comparison", "🔍 City Search", "ℹ️ About"]
    )
    
    search_history_sidebar()
    
    # Main content with enhanced modes
    if app_mode == "🏠 Current Weather":
        st.markdown("""
        <h2 style="color: white; text-align: center; margin: 2rem 0;">
            🌡️ Current Weather
        </h2>
        """, unsafe_allow_html=True)
        
        # Enhanced city input
        col1, col2 = st.columns([3, 1])
        
        with col1:
            city = st.text_input(
                "",
                placeholder="🏙️ Enter city name (e.g., London, New York, Tokyo)",
                help="Enter the name of any city worldwide",
                label_visibility="collapsed"
            )
        
        with col2:
            search_button = st.button("🔍 Get Weather", type="primary", use_container_width=True)
        
        # Enhanced quick city buttons
        st.markdown("""
        <h4 style="color: white; text-align: center; margin: 1.5rem 0 1rem 0;">
            ⚡ Quick Access Cities
        </h4>
        """, unsafe_allow_html=True)
        
        quick_cities = ["London", "New York", "Tokyo", "Paris", "Sydney", "Mumbai", "Dubai"]
        cols = st.columns(len(quick_cities))
        
        for i, quick_city in enumerate(quick_cities):
            with cols[i]:
                if st.button(quick_city, key=f"quick_{quick_city}", 
                           help=f"Get weather for {quick_city}"):
                    city = quick_city
                    search_button = True
        
        # Weather display with loading animation
        if search_button and city:
            if not validate_city_name(city):
                st.markdown("""
                <div class="error-card">
                    <strong>❌ Invalid Input:</strong> Please enter a valid city name (letters, spaces, and hyphens only)
                </div>
                """, unsafe_allow_html=True)
            else:
                try:
                    # Enhanced loading spinner
                    with st.spinner(""):
                        st.markdown(f"""
                        <div class="loading-weather">
                            <div class="weather-spinner"></div>
                            <p style="color: white; margin-left: 1rem;">
                                🔍 Getting weather data for <strong>{city}</strong>...
                            </p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        weather_data = st.session_state.weather_api.get_weather(city, units)
                        st.session_state.current_weather = weather_data
                    
                    if display_current_weather(weather_data, units):
                        st.markdown(f"""
                        <div class="success-card">
                            <strong>✅ Success:</strong> Weather data updated for {city}
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Enhanced export section
                        export_data_section(weather_data)
                        
                except WeatherAPIError as e:
                    st.markdown(f"""
                    <div class="error-card">
                        <strong>❌ Weather API Error:</strong> {str(e)}
                    </div>
                    """, unsafe_allow_html=True)
                except Exception as e:
                    st.markdown(f"""
                    <div class="error-card">
                        <strong>❌ Unexpected Error:</strong> {str(e)}
                    </div>
                    """, unsafe_allow_html=True)
        
        elif st.session_state.current_weather:
            st.markdown("""
            <div style="background: rgba(52, 152, 219, 0.2); color: white; padding: 1rem; 
                        border-radius: 15px; margin: 1rem 0; border: 1px solid rgba(52, 152, 219, 0.3);
                        backdrop-filter: blur(10px); text-align: center;">
                <strong>📊 Info:</strong> Showing cached weather data. Enter a city name to get fresh data.
            </div>
            """, unsafe_allow_html=True)
            display_current_weather(st.session_state.current_weather, units)
    
    elif app_mode == "📅 Weather Forecast":
        st.markdown("""
        <h2 style="color: white; text-align: center; margin: 2rem 0;">
            📈 Weather Forecast
        </h2>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            city = st.text_input(
                "",
                placeholder="🏙️ Enter city name for forecast",
                label_visibility="collapsed"
            )
        
        with col2:
            days = st.selectbox("📅 Forecast days:", [1, 2, 3, 4, 5], index=2)
        
        with col3:
            get_forecast_btn = st.button("📅 Get Forecast", type="primary", use_container_width=True)
        
        if get_forecast_btn and city:
            if not validate_city_name(city):
                st.markdown("""
                <div class="error-card">
                    <strong>❌ Invalid Input:</strong> Please enter a valid city name
                </div>
                """, unsafe_allow_html=True)
            else:
                try:
                    with st.spinner(""):
                        st.markdown(f"""
                        <div class="loading-weather">
                            <div class="weather-spinner"></div>
                            <p style="color: white; margin-left: 1rem;">
                                📅 Getting {days}-day forecast for <strong>{city}</strong>...
                            </p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        forecast_data = st.session_state.weather_api.get_forecast(city, days, units)
                        st.session_state.forecast_data = forecast_data
                    
                    if display_forecast(forecast_data, units):
                        st.markdown(f"""
                        <div class="success-card">
                            <strong>✅ Success:</strong> Forecast data loaded for {city}
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Enhanced export section
                        export_data_section(None, forecast_data)
                        
                except WeatherAPIError as e:
                    st.markdown(f"""
                    <div class="error-card">
                        <strong>❌ Weather API Error:</strong> {str(e)}
                    </div>
                    """, unsafe_allow_html=True)
                except Exception as e:
                    st.markdown(f"""
                    <div class="error-card">
                        <strong>❌ Unexpected Error:</strong> {str(e)}
                    </div>
                    """, unsafe_allow_html=True)
    
    elif app_mode == "⚖️ City Comparison":
        st.markdown("""
        <h2 style="color: white; text-align: center; margin: 2rem 0;">
            🆚 City Weather Comparison
        </h2>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([2, 2, 1])
        
        with col1:
            city1 = st.text_input("", placeholder="🏙️ First city (e.g., London)", 
                                 label_visibility="collapsed")
        
        with col2:
            city2 = st.text_input("", placeholder="🏙️ Second city (e.g., Paris)", 
                                 label_visibility="collapsed")
        
        with col3:
            compare_btn = st.button("⚖️ Compare", type="primary", use_container_width=True)
        
        if compare_btn and city1 and city2:
            if not (validate_city_name(city1) and validate_city_name(city2)):
                st.markdown("""
                <div class="error-card">
                    <strong>❌ Invalid Input:</strong> Please enter valid city names
                </div>
                """, unsafe_allow_html=True)
            else:
                try:
                    with st.spinner(""):
                        st.markdown(f"""
                        <div class="loading-weather">
                            <div class="weather-spinner"></div>
                            <p style="color: white; margin-left: 1rem;">
                                🔍 Comparing weather between <strong>{city1}</strong> and <strong>{city2}</strong>...
                            </p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        weather1 = st.session_state.weather_api.get_weather(city1, units)
                        weather2 = st.session_state.weather_api.get_weather(city2, units)
                    
                    if display_comparison(weather1, weather2, units):
                        pass  # Success message is shown in display_comparison
                        
                except WeatherAPIError as e:
                    st.markdown(f"""
                    <div class="error-card">
                        <strong>❌ Weather API Error:</strong> {str(e)}
                    </div>
                    """, unsafe_allow_html=True)
                except Exception as e:
                    st.markdown(f"""
                    <div class="error-card">
                        <strong>❌ Unexpected Error:</strong> {str(e)}
                    </div>
                    """, unsafe_allow_html=True)
    
    elif app_mode == "🔍 City Search":
        st.markdown("""
        <h2 style="color: white; text-align: center; margin: 2rem 0;">
            🔍 City Search & Multiple Weather
        </h2>
        """, unsafe_allow_html=True)
        
        # Enhanced city search
        st.markdown("""
        <h3 style="color: white; margin: 2rem 0 1rem 0;">
            🏙️ Search Cities
        </h3>
        """, unsafe_allow_html=True)
        
        search_query = st.text_input("", placeholder="🔍 Search for cities (e.g., London)", 
                                   label_visibility="collapsed")
        
        if search_query:
            try:
                cities = st.session_state.weather_api.search_cities(search_query, 10)
                
                if cities:
                    st.markdown(f"""
                    <div class="success-card">
                        <strong>🎯 Found {len(cities)} cities matching '{search_query}'</strong>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    for i, city in enumerate(cities):
                        country = city.get('country', 'Unknown')
                        state = city.get('state', '')
                        display_name = f"{city['name']}, {state + ', ' if state else ''}{country}"
                        
                        st.markdown(f"""
                        <div class="metric-card" style="animation-delay: {i * 0.1}s;">
                            <div style="display: grid; grid-template-columns: 2fr 1fr 1fr; gap: 1rem; align-items: center;">
                                <div>
                                    <div style="font-weight: 600; color: white; font-size: 1.1rem;">
                                        📍 {display_name}
                                    </div>
                                </div>
                                <div style="text-align: center; color: rgba(255,255,255,0.8);">
                                    📐 {city['lat']:.2f}, {city['lon']:.2f}
                                </div>
                                <div style="text-align: center;">
                                    <button onclick="location.reload()" style="
                                        background: linear-gradient(45deg, #667eea, #764ba2);
                                        color: white; border: none; border-radius: 20px;
                                        padding: 0.5rem 1rem; font-weight: 600;
                                        cursor: pointer; transition: all 0.3s ease;
                                        box-shadow: 0 2px 10px rgba(0,0,0,0.2);">
                                        🌤️ Get Weather
                                    </button>
                                </div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Add actual functionality for weather button
                        col1, col2, col3 = st.columns([2, 1, 1])
                        with col3:
                            if st.button(f"Get Weather", key=f"weather_{city['name']}_{city['lat']}", 
                                       help=f"Get current weather for {display_name}"):
                                try:
                                    with st.spinner(""):
                                        weather_data = st.session_state.weather_api.get_weather_by_coordinates(
                                            city['lat'], city['lon'], units
                                        )
                                    display_current_weather(weather_data, units)
                                except Exception as e:
                                    st.markdown(f"""
                                    <div class="error-card">
                                        <strong>❌ Error:</strong> {str(e)}
                                    </div>
                                    """, unsafe_allow_html=True)
                else:
                    st.markdown("""
                    <div style="background: rgba(52, 152, 219, 0.2); color: white; padding: 1rem; 
                                border-radius: 15px; margin: 1rem 0; border: 1px solid rgba(52, 152, 219, 0.3);
                                backdrop-filter: blur(10px); text-align: center;">
                        <strong>🔍 No Results:</strong> No cities found matching your search.
                    </div>
                    """, unsafe_allow_html=True)
            except Exception as e:
                st.markdown(f"""
                <div class="error-card">
                    <strong>❌ Search Error:</strong> {str(e)}
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown('<div style="height: 2rem;"></div>', unsafe_allow_html=True)
        
        # Enhanced multiple cities weather
        st.markdown("""
        <h3 style="color: white; margin: 2rem 0 1rem 0;">
            🌍 Multiple Cities Weather
        </h3>
        """, unsafe_allow_html=True)
        
        cities_input = st.text_area(
            "",
            placeholder="🏙️ Enter multiple cities (one per line):\n\nLondon\nParis\nTokyo\nNew York",
            height=120,
            label_visibility="collapsed"
        )
        
        if st.button("🌐 Get All Weather Data", type="primary") and cities_input:
            cities_list = [city.strip() for city in cities_input.split('\n') if city.strip()]
            
            if len(cities_list) > 10:
                st.markdown("""
                <div style="background: rgba(243, 156, 18, 0.2); color: #f39c12; padding: 1rem; 
                            border-radius: 15px; margin: 1rem 0; border: 1px solid rgba(243, 156, 18, 0.3);
                            backdrop-filter: blur(10px); text-align: center;">
                    <strong>⚠️ Limit Reached:</strong> Limited to 10 cities to avoid rate limits
                </div>
                """, unsafe_allow_html=True)
                cities_list = cities_list[:10]
            
            try:
                with st.spinner(""):
                    st.markdown(f"""
                    <div class="loading-weather">
                        <div class="weather-spinner"></div>
                        <p style="color: white; margin-left: 1rem;">
                            🔍 Getting weather data for <strong>{len(cities_list)} cities</strong>...
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    results = st.session_state.weather_api.get_multiple_cities_weather(cities_list, units)
                
                st.markdown(f"""
                <div class="success-card">
                    <strong>✅ Results:</strong> Successfully retrieved data for {results['successful_count']}/{results['total_requested']} cities
                </div>
                """, unsafe_allow_html=True)
                
                # Display successful results with enhanced cards
                if results['successful']:
                    st.markdown("""
                    <h4 style="color: white; margin: 2rem 0 1rem 0;">
                        🌤️ Weather Data Retrieved
                    </h4>
                    """, unsafe_allow_html=True)
                    
                    for i, (city, weather_data) in enumerate(results['successful'].items()):
                        with st.expander(f"🌤️ {city} Weather", expanded=False):
                            display_current_weather(weather_data, units)
                
                # Display errors with enhanced styling
                if results['errors']:
                    st.markdown("""
                    <h4 style="color: #e74c3c; margin: 2rem 0 1rem 0;">
                        ❌ Failed Cities
                    </h4>
                    """, unsafe_allow_html=True)
                    
                    for city, error in results['errors'].items():
                        st.markdown(f"""
                        <div class="error-card">
                            <strong>{city}:</strong> {error}
                        </div>
                        """, unsafe_allow_html=True)
            
            except Exception as e:
                st.markdown(f"""
                <div class="error-card">
                    <strong>❌ Multiple Cities Error:</strong> {str(e)}
                </div>
                """, unsafe_allow_html=True)
    
    elif app_mode == "ℹ️ About":
        st.markdown("""
        <h2 style="color: white; text-align: center; margin: 2rem 0;">
            ℹ️ About This App
        </h2>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="weather-card">
            <h3 style="color: #667eea; margin-bottom: 1.5rem;">🌤️ Advanced Weather App</h3>
            
            <p style="font-size: 1.1rem; line-height: 1.6; margin-bottom: 1.5rem; color: rgba(255,255,255,0.9);">
                This is a comprehensive weather application built with <strong>Streamlit</strong> and <strong>OpenWeatherMap API</strong> 
                that provides real-time weather insights with a stunning, interactive interface.
            </p>
            
            <h4 style="color: #00b894; margin: 1.5rem 0 1rem 0;">✨ Key Features</h4>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1rem; margin-bottom: 1.5rem;">
                <div class="metric-card">
                    <strong>🌡️ Real-time Weather</strong><br>
                    Current conditions with detailed metrics
                </div>
                <div class="metric-card">
                    <strong>📅 5-Day Forecasts</strong><br>
                    Hourly details with interactive charts
                </div>
                <div class="metric-card">
                    <strong>⚖️ City Comparisons</strong><br>
                    Side-by-side weather analysis
                </div>
                <div class="metric-card">
                    <strong>🔍 Smart Search</strong><br>
                    Global city search and bulk queries
                </div>
                <div class="metric-card">
                    <strong>📊 Data Visualization</strong><br>
                    Interactive charts and graphs
                </div>
                <div class="metric-card">
                    <strong>📁 Export Options</strong><br>
                    JSON, CSV, and summary formats
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <div class="forecast-card">
                <h4 style="color: #667eea; margin-bottom: 1rem;">🛠️ Technical Stack</h4>
                <ul style="text-align: left; color: rgba(255,255,255,0.9);">
                    <li><strong>Frontend:</strong> Streamlit with custom CSS</li>
                    <li><strong>API:</strong> OpenWeatherMap</li>
                    <li><strong>Charts:</strong> Plotly for interactive visualizations</li>
                    <li><strong>Data Processing:</strong> Pandas</li>
                    <li><strong>HTTP Client:</strong> Requests with retry logic</li>
                    <li><strong>Styling:</strong> Custom CSS with animations</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="forecast-card">
                <h4 style="color: #00b894; margin-bottom: 1rem;">📊 Data Metrics</h4>
                <ul style="text-align: left; color: rgba(255,255,255,0.9);">
                    <li>Temperature (current, min, max, feels like)</li>
                    <li>Humidity and atmospheric pressure</li>
                    <li>Wind speed and direction</li>
                    <li>Weather conditions and visibility</li>
                    <li>Sunrise and sunset times</li>
                    <li>Air quality data (where available)</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="weather-card">
            <h4 style="color: #fd79a8; margin-bottom: 1rem;">🎨 Enhanced UI Features</h4>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem;">
                <div style="text-align: center;">
                    <div style="font-size: 2rem; margin-bottom: 0.5rem;">🌌</div>
                    <strong>Dark Theme</strong><br>
                    <span style="opacity: 0.8;">Gradient backgrounds with glassmorphism</span>
                </div>
                <div style="text-align: center;">
                    <div style="font-size: 2rem; margin-bottom: 0.5rem;">✨</div>
                    <strong>Animations</strong><br>
                    <span style="opacity: 0.8;">Smooth transitions and hover effects</span>
                </div>
                <div style="text-align: center;">
                    <div style="font-size: 2rem; margin-bottom: 0.5rem;">🎯</div>
                    <strong>Interactive</strong><br>
                    <span style="opacity: 0.8;">Responsive cards and buttons</span>
                </div>
                <div style="text-align: center;">
                    <div style="font-size: 2rem; margin-bottom: 0.5rem;">📱</div>
                    <strong>Mobile Ready</strong><br>
                    <span style="opacity: 0.8;">Responsive design for all devices</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="success-card" style="text-align: center; margin: 2rem 0;">
            <strong>💡 Pro Tip:</strong> Use the sidebar to switch between different modes and adjust settings for the best experience!
        </div>
        """, unsafe_allow_html=True)
        
        # Enhanced API status check
        if st.button("🔍 Test API Connection", type="primary", use_container_width=True):
            try:
                with st.spinner(""):
                    st.markdown("""
                    <div class="loading-weather">
                        <div class="weather-spinner"></div>
                        <p style="color: white; margin-left: 1rem;">
                            Testing API connection...
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    test_weather = st.session_state.weather_api.get_weather("London", "metric")
                
                st.markdown("""
                <div class="success-card">
                    <strong>✅ API Connection Successful!</strong>
                </div>
                """, unsafe_allow_html=True)
                
                st.json({
                    "status": "connected", 
                    "test_city": "London", 
                    "timestamp": datetime.now().isoformat()
                })
            except Exception as e:
                st.markdown(f"""
                <div class="error-card">
                    <strong>❌ API Connection Failed:</strong> {str(e)}
                </div>
                """, unsafe_allow_html=True)
    
    # Enhanced footer
    st.markdown('<div style="height: 3rem;"></div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="footer">
        <div style="display: flex; justify-content: center; align-items: center; gap: 2rem; flex-wrap: wrap;">
            <div style="text-align: center;">
                <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">🌤️</div>
                <div style="font-weight: 600;">Advanced Weather App</div>
                <div style="font-size: 0.9rem; opacity: 0.7;">Built with Streamlit & OpenWeatherMap API</div>
            </div>
        </div>
        
        <div style="margin-top: 1rem; padding-top: 1rem; border-top: 1px solid rgba(255,255,255,0.1);">
            <div style="text-align: center; font-size: 0.9rem; opacity: 0.6;">
                🚀 Enhanced with animations, glassmorphism UI, and interactive elements
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
