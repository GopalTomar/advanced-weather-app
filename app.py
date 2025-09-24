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

# Enhanced Custom CSS
def load_css():
    st.markdown("""
    <style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Roboto:wght@300;400;500;700&display=swap');
    
    /* Global Styles */
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
        font-size: 14px;
        line-height: 1.6;
        color: #2c3e50;
    }
    
    /* Streamlit specific overrides */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }
    
    /* Header Styles */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Inter', sans-serif !important;
        font-weight: 600 !important;
        line-height: 1.3 !important;
        color: #2c3e50 !important;
        margin-bottom: 1rem !important;
        letter-spacing: -0.02em;
    }
    
    h1 {
        font-size: 2.5rem !important;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-align: center;
        margin-bottom: 0.5rem !important;
    }
    
    h2 {
        font-size: 1.8rem !important;
        color: #34495e !important;
    }
    
    h3 {
        font-size: 1.4rem !important;
        color: #34495e !important;
    }
    
    /* Subtitle text */
    .subtitle {
        text-align: center;
        color: #7f8c8d;
        font-style: italic;
        margin-bottom: 2rem;
        font-size: 1.1rem;
        font-weight: 400;
    }
    
    /* Weather Cards */
    .weather-card {
        background: linear-gradient(135deg, #74b9ff 0%, #0984e3 100%);
        padding: 2rem;
        border-radius: 20px;
        color: white;
        margin: 1.5rem 0;
        box-shadow: 0 10px 30px rgba(116, 185, 255, 0.3);
        border: none;
        position: relative;
        overflow: hidden;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .weather-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(135deg, rgba(255,255,255,0.1) 0%, transparent 100%);
        opacity: 0;
        transition: opacity 0.3s ease;
    }
    
    .weather-card:hover {
        transform: translateY(-5px) scale(1.02);
        box-shadow: 0 20px 40px rgba(116, 185, 255, 0.4);
    }
    
    .weather-card:hover::before {
        opacity: 1;
    }
    
    .weather-card h2 {
        color: white !important;
        font-weight: 500 !important;
        margin-bottom: 1rem !important;
        text-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    /* Metric Cards */
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 16px;
        border: 1px solid #e8ecef;
        margin: 0.5rem 0;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
        position: relative;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        border-left: 4px solid transparent;
        background-clip: padding-box;
    }
    
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 4px;
        height: 100%;
        background: linear-gradient(135deg, #74b9ff 0%, #0984e3 100%);
        border-radius: 4px 0 0 4px;
        transition: width 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
        border-color: #74b9ff;
    }
    
    .metric-card:hover::before {
        width: 8px;
    }
    
    /* Forecast Cards */
    .forecast-card {
        background: linear-gradient(135deg, #a8e6cf 0%, #7fcdcd 100%);
        padding: 1.5rem;
        border-radius: 16px;
        margin: 0.75rem 0;
        text-align: center;
        box-shadow: 0 6px 20px rgba(168, 230, 207, 0.3);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        border: none;
        position: relative;
        overflow: hidden;
    }
    
    .forecast-card::after {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
        transition: left 0.5s ease;
    }
    
    .forecast-card:hover {
        transform: translateY(-3px) scale(1.02);
        box-shadow: 0 12px 30px rgba(168, 230, 207, 0.4);
    }
    
    .forecast-card:hover::after {
        left: 100%;
    }
    
    /* Error and Success Cards */
    .error-card {
        background: linear-gradient(135deg, #ff7675 0%, #d63031 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        box-shadow: 0 6px 20px rgba(255, 118, 117, 0.3);
        border: none;
        animation: shake 0.5s ease-in-out;
    }
    
    .success-card {
        background: linear-gradient(135deg, #00b894 0%, #00a085 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        box-shadow: 0 6px 20px rgba(0, 184, 148, 0.3);
        border: none;
        animation: slideInUp 0.5s ease-out;
    }
    
    /* Button Styles */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.75rem 1.5rem;
        font-weight: 500;
        font-family: 'Inter', sans-serif;
        font-size: 0.9rem;
        cursor: pointer;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
        position: relative;
        overflow: hidden;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
    }
    
    .stButton > button:active {
        transform: translateY(0);
    }
    
    /* Primary Button */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #ff7675 0%, #d63031 100%);
        box-shadow: 0 4px 15px rgba(255, 118, 117, 0.3);
    }
    
    .stButton > button[kind="primary"]:hover {
        box-shadow: 0 8px 25px rgba(255, 118, 117, 0.4);
    }
    
    /* Quick Access Buttons */
    .quick-city-btn {
        background: linear-gradient(135deg, #a8e6cf 0%, #7fcdcd 100%);
        border: none;
        border-radius: 25px;
        padding: 0.5rem 1rem;
        font-weight: 500;
        color: #2c3e50;
        cursor: pointer;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        font-family: 'Inter', sans-serif;
        margin: 0.25rem;
        box-shadow: 0 3px 10px rgba(168, 230, 207, 0.3);
    }
    
    .quick-city-btn:hover {
        transform: translateY(-2px) scale(1.05);
        box-shadow: 0 6px 20px rgba(168, 230, 207, 0.4);
    }
    
    /* Input Styles */
    .stTextInput > div > div > input {
        border-radius: 12px;
        border: 2px solid #e8ecef;
        padding: 0.75rem 1rem;
        font-family: 'Inter', sans-serif;
        font-size: 0.95rem;
        transition: all 0.3s ease;
        background: white;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #74b9ff;
        box-shadow: 0 0 0 3px rgba(116, 185, 255, 0.1);
        outline: none;
    }
    
    /* Selectbox Styles */
    .stSelectbox > div > div {
        border-radius: 12px;
        border: 2px solid #e8ecef;
        background: white;
        transition: all 0.3s ease;
    }
    
    .stSelectbox > div > div:hover {
        border-color: #74b9ff;
    }
    
    /* Sidebar Styles */
    .css-1d391kg {
        background: linear-gradient(180deg, #f8f9fa 0%, #ffffff 100%);
    }
    
    .sidebar-title {
        font-size: 1.2rem;
        font-weight: 600;
        color: #2c3e50;
        margin-bottom: 1rem;
        text-align: center;
        padding: 1rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    /* Metrics */
    .metric-container {
        background: white;
        padding: 1.5rem;
        border-radius: 16px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
        margin: 0.5rem 0;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        border: 2px solid transparent;
    }
    
    .metric-container:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
        border-color: #74b9ff;
    }
    
    /* Expander Styles */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
        border-radius: 12px;
        border: 2px solid #e8ecef;
        font-weight: 500;
        color: #2c3e50;
        transition: all 0.3s ease;
    }
    
    .streamlit-expanderHeader:hover {
        border-color: #74b9ff;
        background: linear-gradient(135deg, #74b9ff 0%, #0984e3 100%);
        color: white;
    }
    
    /* Info/Warning/Error Boxes */
    .stInfo, .stSuccess, .stWarning, .stError {
        border-radius: 12px;
        border: none;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        font-family: 'Inter', sans-serif;
    }
    
    /* Divider */
    hr {
        border: none;
        height: 2px;
        background: linear-gradient(135deg, #74b9ff 0%, #0984e3 100%);
        border-radius: 2px;
        margin: 2rem 0;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        color: #7f8c8d;
        font-size: 0.9rem;
        padding: 2rem 0;
        border-top: 2px solid #ecf0f1;
        margin-top: 3rem;
    }
    
    /* Animations */
    @keyframes shake {
        0%, 100% { transform: translateX(0); }
        25% { transform: translateX(-5px); }
        75% { transform: translateX(5px); }
    }
    
    @keyframes slideInUp {
        from {
            transform: translateY(20px);
            opacity: 0;
        }
        to {
            transform: translateY(0);
            opacity: 1;
        }
    }
    
    @keyframes fadeInScale {
        from {
            transform: scale(0.9);
            opacity: 0;
        }
        to {
            transform: scale(1);
            opacity: 1;
        }
    }
    
    /* Loading Animation */
    .loading-pulse {
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.5; }
        100% { opacity: 1; }
    }
    
    /* Responsive Design */
    @media (max-width: 768px) {
        .main .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
        }
        
        h1 {
            font-size: 2rem !important;
        }
        
        .weather-card {
            padding: 1.5rem;
            margin: 1rem 0;
        }
    }
    
    /* Chart Container */
    .plot-container {
        background: white;
        border-radius: 16px;
        padding: 1rem;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
        margin: 1rem 0;
        transition: all 0.3s ease;
    }
    
    .plot-container:hover {
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
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
            <div style="display: flex; align-items: center; gap: 2rem; flex-wrap: wrap;">
                <div style="font-size: 3rem; font-weight: bold;">
                    {format_temperature(main['temp'], units)}
                </div>
                <div>
                    <p style="font-size: 1.2rem; margin: 0; font-weight: 500;">{capitalize_words(weather['description'])}</p>
                    <p style="margin: 0; opacity: 0.8;">Feels like {format_temperature(main['feels_like'], units)}</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Weather advice
        advice = get_weather_advice(weather_data)
        st.info(advice)
        
        # Metrics in columns with enhanced styling
        col1, col2, col3, col4 = st.columns(4)
        
        metrics_data = [
            ("🌡️ Temperature", format_temperature(main['temp'], units), f"{main['temp'] - main['feels_like']:.1f}° from feels like"),
            ("💧 Humidity", format_humidity(main['humidity']), None),
            ("🌪️ Wind Speed", format_wind_speed(wind.get('speed', 0), units), None),
            ("📊 Pressure", format_pressure(main['pressure']), None)
        ]
        
        cols = [col1, col2, col3, col4]
        for i, (label, value, delta) in enumerate(metrics_data):
            with cols[i]:
                st.markdown(f"""
                <div class="metric-container">
                    <div style="font-size: 0.85rem; color: #7f8c8d; font-weight: 500; margin-bottom: 0.5rem;">{label}</div>
                    <div style="font-size: 1.5rem; font-weight: 600; color: #2c3e50;">{value}</div>
                    {f'<div style="font-size: 0.8rem; color: #74b9ff; margin-top: 0.3rem;">{delta}</div>' if delta else ''}
                </div>
                """, unsafe_allow_html=True)
        
        # Additional details with improved styling
        with st.expander("📋 Detailed Information"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("""
                <div style="background: #f8f9fa; padding: 1rem; border-radius: 12px; margin-bottom: 1rem;">
                    <h4 style="color: #2c3e50; margin-bottom: 0.5rem;">🌡️ Temperature Details</h4>
                </div>
                """, unsafe_allow_html=True)
                st.write(f"• **Current**: {format_temperature(main['temp'], units)}")
                st.write(f"• **Feels like**: {format_temperature(main['feels_like'], units)}")
                st.write(f"• **Min today**: {format_temperature(main['temp_min'], units)}")
                st.write(f"• **Max today**: {format_temperature(main['temp_max'], units)}")
            
            with col2:
                st.markdown("""
                <div style="background: #f8f9fa; padding: 1rem; border-radius: 12px; margin-bottom: 1rem;">
                    <h4 style="color: #2c3e50; margin-bottom: 0.5rem;">🌤️ Weather Conditions</h4>
                </div>
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
                    <div class="metric-container" style="text-align: center;">
                        <div style="font-size: 2rem; margin-bottom: 0.5rem;">🌅</div>
                        <div style="font-size: 0.9rem; color: #7f8c8d; margin-bottom: 0.3rem;">Sunrise</div>
                        <div style="font-size: 1.3rem; font-weight: 600; color: #2c3e50;">{sunrise}</div>
                    </div>
                    """, unsafe_allow_html=True)
                with col2:
                    st.markdown(f"""
                    <div class="metric-container" style="text-align: center;">
                        <div style="font-size: 2rem; margin-bottom: 0.5rem;">🌇</div>
                        <div style="font-size: 0.9rem; color: #7f8c8d; margin-bottom: 0.3rem;">Sunset</div>
                        <div style="font-size: 1.3rem; font-weight: 600; color: #2c3e50;">{sunset}</div>
                    </div>
                    """, unsafe_allow_html=True)
        
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
        
        st.markdown(f"""
        <div style="text-align: center; margin-bottom: 2rem;">
            <h2 style="color: #2c3e50; font-weight: 600;">📅 5-Day Forecast for {city_name}</h2>
        </div>
        """, unsafe_allow_html=True)
        
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
        
        # Temperature trend chart with enhanced styling
        st.markdown('<div class="plot-container">', unsafe_allow_html=True)
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=hourly_times,
            y=hourly_temps,
            mode='lines+markers',
            name='Temperature',
            line=dict(color='#74b9ff', width=3),
            marker=dict(size=8, color='#0984e3'),
            fill='tonexty',
            fillcolor='rgba(116, 185, 255, 0.1)'
        ))
        
        fig.update_layout(
            title=dict(
                text=f"🌡️ Temperature Trend - {city_name}",
                x=0.5,
                font=dict(size=18, color='#2c3e50', family='Inter')
            ),
            xaxis_title="Time",
            yaxis_title=f"Temperature ({Config.UNITS_DISPLAY[units]['temp']})",
            hovermode='x unified',
            template='plotly_white',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(family='Inter', size=12),
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Daily forecast cards with enhanced styling
        st.markdown("""
        <div style="text-align: center; margin: 2rem 0;">
            <h3 style="color: #2c3e50; font-weight: 600;">📊 Daily Summary</h3>
        </div>
        """, unsafe_allow_html=True)
        
        for date_str, data in list(daily_data.items())[:5]:  # Show 5 days
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
            temp_color = color_temp_by_range(max_temp)
            
            st.markdown(f"""
            <div class="forecast-card" style="margin: 1rem 0;">
                <div style="display: grid; grid-template-columns: 2fr 1fr 1fr 1fr 1fr; gap: 1rem; align-items: center; text-align: center;">
                    <div style="text-align: left;">
                        <div style="font-size: 1.1rem; font-weight: 600; color: #2c3e50; margin-bottom: 0.3rem;">{day_name}</div>
                        <div style="display: flex; align-items: center; gap: 0.5rem;">
                            <span style="font-size: 1.5rem;">{icon}</span>
                            <span style="color: #34495e; font-weight: 500;">{capitalize_words(most_common_condition)}</span>
                        </div>
                    </div>
                    <div>
                        <div style="font-size: 0.8rem; color: #7f8c8d; margin-bottom: 0.2rem;">🌡️ Temp Range</div>
                        <div style="font-weight: 600; color: #2c3e50;">{max_temp:.0f}°/{min_temp:.0f}°</div>
                    </div>
                    <div>
                        <div style="font-size: 0.8rem; color: #7f8c8d; margin-bottom: 0.2rem;">💧 Humidity</div>
                        <div style="font-weight: 600; color: #2c3e50;">{avg_humidity:.0f}%</div>
                    </div>
                    <div>
                        <div style="font-size: 0.8rem; color: #7f8c8d; margin-bottom: 0.2rem;">🌪️ Wind</div>
                        <div style="font-weight: 600; color: #2c3e50;">{avg_wind:.1f} {Config.UNITS_DISPLAY[units]['speed']}</div>
                    </div>
                    <div>
                        <div style="background: {temp_color}; padding: 0.5rem 1rem; border-radius: 25px; color: white; font-weight: bold; box-shadow: 0 2px 8px rgba(0,0,0,0.2);">{max_temp:.0f}°</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
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
        
        st.markdown(f"""
        <div style="text-align: center; margin-bottom: 2rem;">
            <h2 style="color: #2c3e50; font-weight: 600;">⚖️ Weather Comparison: {city1} vs {city2}</h2>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        # City 1
        with col1:
            main1 = weather_data1['main']
            weather1 = weather_data1['weather'][0]
            icon1 = get_weather_icon(weather1['icon'])
            
            st.markdown(f"""
            <div class="weather-card" style="margin-bottom: 1.5rem;">
                <h3 style="color: white !important; text-align: center; margin-bottom: 1rem;">{city1}, {weather_data1['sys']['country']}</h3>
                <div style="text-align: center;">
                    <div style="font-size: 3rem; margin-bottom: 0.5rem;">{icon1}</div>
                    <div style="font-size: 2.5rem; font-weight: bold; margin-bottom: 0.5rem;">{format_temperature(main1['temp'], units)}</div>
                    <p style="font-size: 1.1rem; margin: 0; opacity: 0.9; font-weight: 500;">{capitalize_words(weather1['description'])}</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Metrics for city 1
            metrics1 = [
                ("Feels Like", format_temperature(main1['feels_like'], units)),
                ("Humidity", format_humidity(main1['humidity'])),
                ("Pressure", format_pressure(main1['pressure']))
            ]
            
            for label, value in metrics1:
                st.markdown(f"""
                <div class="metric-container" style="text-align: center; margin: 0.5rem 0;">
                    <div style="font-size: 0.85rem; color: #7f8c8d; margin-bottom: 0.3rem;">{label}</div>
                    <div style="font-size: 1.3rem; font-weight: 600; color: #2c3e50;">{value}</div>
                </div>
                """, unsafe_allow_html=True)
        
        # City 2
        with col2:
            main2 = weather_data2['main']
            weather2 = weather_data2['weather'][0]
            icon2 = get_weather_icon(weather2['icon'])
            
            st.markdown(f"""
            <div class="weather-card" style="margin-bottom: 1.5rem;">
                <h3 style="color: white !important; text-align: center; margin-bottom: 1rem;">{city2}, {weather_data2['sys']['country']}</h3>
                <div style="text-align: center;">
                    <div style="font-size: 3rem; margin-bottom: 0.5rem;">{icon2}</div>
                    <div style="font-size: 2.5rem; font-weight: bold; margin-bottom: 0.5rem;">{format_temperature(main2['temp'], units)}</div>
                    <p style="font-size: 1.1rem; margin: 0; opacity: 0.9; font-weight: 500;">{capitalize_words(weather2['description'])}</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Metrics for city 2 with comparisons
            temp_diff = main2['temp'] - main1['temp']
            humidity_diff = main2['humidity'] - main1['humidity']
            pressure_diff = main2['pressure'] - main1['pressure']
            
            metrics2 = [
                ("Feels Like", format_temperature(main2['feels_like'], units), f"{temp_diff:+.1f}° vs {city1}"),
                ("Humidity", format_humidity(main2['humidity']), f"{humidity_diff:+d}% vs {city1}"),
                ("Pressure", format_pressure(main2['pressure']), f"{pressure_diff:+.1f} vs {city1}")
            ]
            
            for label, value, delta in metrics2:
                delta_color = "#27ae60" if "+" in delta else "#e74c3c" if "-" in delta else "#7f8c8d"
                st.markdown(f"""
                <div class="metric-container" style="text-align: center; margin: 0.5rem 0;">
                    <div style="font-size: 0.85rem; color: #7f8c8d; margin-bottom: 0.3rem;">{label}</div>
                    <div style="font-size: 1.3rem; font-weight: 600; color: #2c3e50; margin-bottom: 0.2rem;">{value}</div>
                    <div style="font-size: 0.8rem; color: {delta_color}; font-weight: 500;">{delta}</div>
                </div>
                """, unsafe_allow_html=True)
        
        # Comparison chart with enhanced styling
        comparison_data = {
            'City': [city1, city2],
            'Temperature': [main1['temp'], main2['temp']],
            'Feels Like': [main1['feels_like'], main2['feels_like']],
            'Humidity': [main1['humidity'], main2['humidity']],
            'Pressure': [main1['pressure'], main2['pressure']]
        }
        
        df = pd.DataFrame(comparison_data)
        
        # Temperature comparison chart
        st.markdown('<div class="plot-container">', unsafe_allow_html=True)
        fig = px.bar(
            df, 
            x='City', 
            y='Temperature',
            title=f'🌡️ Temperature Comparison ({Config.UNITS_DISPLAY[units]["temp"]})',
            color='Temperature',
            color_continuous_scale='RdYlBu_r'
        )
        
        fig.update_layout(
            title=dict(
                x=0.5,
                font=dict(size=18, color='#2c3e50', family='Inter')
            ),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(family='Inter', size=12),
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        return True
        
    except Exception as e:
        st.error(f"Error displaying comparison: {str(e)}")
        return False

def search_history_sidebar():
    """Display search history in sidebar"""
    st.sidebar.markdown('<div class="sidebar-title">📝 Recent Searches</div>', unsafe_allow_html=True)
    
    history = get_search_history()
    
    if history:
        for i, entry in enumerate(history[:5]):  # Show last 5 searches
            status_icon = "✅" if entry['success'] else "❌"
            st.sidebar.markdown(f"""
            <div style="background: white; padding: 0.75rem; border-radius: 8px; margin: 0.5rem 0; 
                        box-shadow: 0 2px 8px rgba(0,0,0,0.1); transition: all 0.3s ease;">
                <div style="font-weight: 500; color: #2c3e50;">{status_icon} {entry['city']}</div>
                <div style="font-size: 0.8rem; color: #7f8c8d; margin-top: 0.2rem;">🕒 {entry['timestamp']}</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.sidebar.markdown("""
        <div style="text-align: center; color: #7f8c8d; font-style: italic; padding: 1rem;">
            No recent searches
        </div>
        """, unsafe_allow_html=True)

def export_data_section(weather_data, forecast_data=None):
    """Provide data export functionality"""
    st.markdown("""
    <div style="margin: 2rem 0;">
        <h3 style="color: #2c3e50; text-align: center; margin-bottom: 1rem;">📁 Export Data</h3>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 Export Current Weather (JSON)", key="export_json"):
            weather_json = json.dumps(weather_data, indent=2, default=str)
            st.download_button(
                label="Download JSON",
                data=weather_json,
                file_name=f"weather_{weather_data['name']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
    
    with col2:
        if forecast_data and st.button("📈 Export Forecast (CSV)", key="export_csv"):
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
        if st.button("📋 Copy Weather Summary", key="export_summary"):
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
    
    # App header with enhanced styling
    st.markdown("""
    <div style="text-align: center; margin-bottom: 3rem;">
        <h1>🌤️ Advanced Weather App</h1>
        <div class="subtitle">Get real-time weather data, forecasts, and comparisons for cities worldwide</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar configuration with enhanced styling
    st.sidebar.markdown('<div class="sidebar-title">⚙️ Settings</div>', unsafe_allow_html=True)
    
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
        st.markdown('<div style="text-align: center; margin-bottom: 2rem;"><h2>🌡️ Current Weather</h2></div>', unsafe_allow_html=True)
        
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
        
        # Quick city buttons with enhanced styling
        st.markdown("""
        <div style="text-align: center; margin: 2rem 0;">
            <h4 style="color: #2c3e50; margin-bottom: 1rem;">⚡ Quick Access</h4>
        </div>
        """, unsafe_allow_html=True)
        
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
                st.markdown("""
                <div class="error-card">
                    <div style="display: flex; align-items: center; gap: 0.5rem;">
                        <span style="font-size: 1.2rem;">❌</span>
                        <span>Please enter a valid city name (letters, spaces, and hyphens only)</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                try:
                    with st.spinner(f"🔍 Getting weather data for {city}..."):
                        weather_data = st.session_state.weather_api.get_weather(city, units)
                        st.session_state.current_weather = weather_data
                    
                    if display_current_weather(weather_data, units):
                        st.markdown(f"""
                        <div class="success-card">
                            <div style="display: flex; align-items: center; gap: 0.5rem;">
                                <span style="font-size: 1.2rem;">✅</span>
                                <span>Weather data updated for {city}</span>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Export section
                        export_data_section(weather_data)
                        
                except WeatherAPIError as e:
                    st.markdown(f"""
                    <div class="error-card">
                        <div style="display: flex; align-items: center; gap: 0.5rem;">
                            <span style="font-size: 1.2rem;">❌</span>
                            <span>{str(e)}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                except Exception as e:
                    st.markdown(f"""
                    <div class="error-card">
                        <div style="display: flex; align-items: center; gap: 0.5rem;">
                            <span style="font-size: 1.2rem;">❌</span>
                            <span>An unexpected error occurred: {str(e)}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        
        elif st.session_state.current_weather:
            st.info("📊 Showing cached weather data. Enter a city name to get fresh data.")
            display_current_weather(st.session_state.current_weather, units)
    
    elif app_mode == "📅 Weather Forecast":
        st.markdown('<div style="text-align: center; margin-bottom: 2rem;"><h2>📈 Weather Forecast</h2></div>', unsafe_allow_html=True)
        
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
                st.markdown("""
                <div class="error-card">
                    <div style="display: flex; align-items: center; gap: 0.5rem;">
                        <span style="font-size: 1.2rem;">❌</span>
                        <span>Please enter a valid city name</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                try:
                    with st.spinner(f"📅 Getting {days}-day forecast for {city}..."):
                        forecast_data = st.session_state.weather_api.get_forecast(city, days, units)
                        st.session_state.forecast_data = forecast_data
                    
                    if display_forecast(forecast_data, units):
                        st.markdown(f"""
                        <div class="success-card">
                            <div style="display: flex; align-items: center; gap: 0.5rem;">
                                <span style="font-size: 1.2rem;">✅</span>
                                <span>Forecast data loaded for {city}</span>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Export section
                        export_data_section(None, forecast_data)
                        
                except WeatherAPIError as e:
                    st.markdown(f"""
                    <div class="error-card">
                        <div style="display: flex; align-items: center; gap: 0.5rem;">
                            <span style="font-size: 1.2rem;">❌</span>
                            <span>{str(e)}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                except Exception as e:
                    st.markdown(f"""
                    <div class="error-card">
                        <div style="display: flex; align-items: center; gap: 0.5rem;">
                            <span style="font-size: 1.2rem;">❌</span>
                            <span>An unexpected error occurred: {str(e)}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
    
    elif app_mode == "⚖️ City Comparison":
        st.markdown('<div style="text-align: center; margin-bottom: 2rem;"><h2>🆚 City Weather Comparison</h2></div>', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([2, 2, 1])
        
        with col1:
            city1 = st.text_input("First city:", placeholder="e.g., London")
        
        with col2:
            city2 = st.text_input("Second city:", placeholder="e.g., Paris")
        
        with col3:
            compare_btn = st.button("⚖️ Compare", type="primary")
        
        if compare_btn and city1 and city2:
            if not (validate_city_name(city1) and validate_city_name(city2)):
                st.markdown("""
                <div class="error-card">
                    <div style="display: flex; align-items: center; gap: 0.5rem;">
                        <span style="font-size: 1.2rem;">❌</span>
                        <span>Please enter valid city names</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                try:
                    with st.spinner(f"🔍 Comparing weather between {city1} and {city2}..."):
                        weather1 = st.session_state.weather_api.get_weather(city1, units)
                        weather2 = st.session_state.weather_api.get_weather(city2, units)
                    
                    display_comparison(weather1, weather2, units)
                    st.markdown(f"""
                    <div class="success-card">
                        <div style="display: flex; align-items: center; gap: 0.5rem;">
                            <span style="font-size: 1.2rem;">✅</span>
                            <span>Comparison completed between {city1} and {city2}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                except WeatherAPIError as e:
                    st.markdown(f"""
                    <div class="error-card">
                        <div style="display: flex; align-items: center; gap: 0.5rem;">
                            <span style="font-size: 1.2rem;">❌</span>
                            <span>{str(e)}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                except Exception as e:
                    st.markdown(f"""
                    <div class="error-card">
                        <div style="display: flex; align-items: center; gap: 0.5rem;">
                            <span style="font-size: 1.2rem;">❌</span>
                            <span>An unexpected error occurred: {str(e)}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
    
    elif app_mode == "🔍 City Search":
        st.markdown('<div style="text-align: center; margin-bottom: 2rem;"><h2>🔍 City Search & Multiple Weather</h2></div>', unsafe_allow_html=True)
        
        # City search
        st.markdown("""
        <div style="margin: 2rem 0;">
            <h3 style="color: #2c3e50;">🏙️ Search Cities</h3>
        </div>
        """, unsafe_allow_html=True)
        search_query = st.text_input("Search for cities:", placeholder="e.g., London")
        
        if search_query:
            try:
                cities = st.session_state.weather_api.search_cities(search_query, 10)
                
                if cities:
                    st.markdown(f"""
                    <div style="margin: 1rem 0; padding: 1rem; background: #f8f9fa; border-radius: 12px; border-left: 4px solid #74b9ff;">
                        <strong>Found {len(cities)} cities matching '{search_query}':</strong>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    for city in cities:
                        col1, col2, col3 = st.columns([2, 1, 1])
                        with col1:
                            country = city.get('country', 'Unknown')
                            state = city.get('state', '')
                            display_name = f"{city['name']}, {state + ', ' if state else ''}{country}"
                            st.markdown(f"""
                            <div style="background: white; padding: 1rem; border-radius: 8px; margin: 0.5rem 0; 
                                        box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                                <div style="font-weight: 500; color: #2c3e50;">📍 {display_name}</div>
                            </div>
                            """, unsafe_allow_html=True)
                        
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
        
        st.markdown('<hr style="margin: 3rem 0;">', unsafe_allow_html=True)
        
        # Multiple cities weather
        st.markdown("""
        <div style="margin: 2rem 0;">
            <h3 style="color: #2c3e50;">🌍 Multiple Cities Weather</h3>
        </div>
        """, unsafe_allow_html=True)
        
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
                
                st.markdown(f"""
                <div class="success-card">
                    <div style="display: flex; align-items: center; gap: 0.5rem;">
                        <span style="font-size: 1.2rem;">✅</span>
                        <span>Successfully retrieved data for {results['successful_count']}/{results['total_requested']} cities</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Display successful results
                if results['successful']:
                    for city, weather_data in results['successful'].items():
                        with st.expander(f"🌤️ {city}"):
                            display_current_weather(weather_data, units)
                
                # Display errors
                if results['errors']:
                    st.markdown("""
                    <div style="margin: 2rem 0;">
                        <h4 style="color: #e74c3c;">❌ Failed Cities</h4>
                    </div>
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
                    <div style="display: flex; align-items: center; gap: 0.5rem;">
                        <span style="font-size: 1.2rem;">❌</span>
                        <span>Error getting multiple cities data: {str(e)}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    elif app_mode == "ℹ️ About":
        st.markdown('<div style="text-align: center; margin-bottom: 2rem;"><h2>ℹ️ About This App</h2></div>', unsafe_allow_html=True)
        
        st.markdown("""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; 
                    padding: 2rem; border-radius: 20px; margin: 2rem 0; text-align: center;">
            <h3 style="color: white !important; margin-bottom: 1rem;">🌤️ Advanced Weather App</h3>
            <p style="font-size: 1.1rem; margin: 0; opacity: 0.9;">
                A comprehensive weather application built with <strong>Streamlit</strong> and <strong>OpenWeatherMap API</strong>
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Features section
        features_col1, features_col2 = st.columns(2)
        
        with features_col1:
            st.markdown("""
            <div style="background: white; padding: 1.5rem; border-radius: 16px; 
                        box-shadow: 0 4px 20px rgba(0,0,0,0.08); margin: 1rem 0;">
                <h4 style="color: #2c3e50; margin-bottom: 1rem;">🚀 Features</h4>
                <ul style="color: #34495e; line-height: 1.8;">
                    <li>🌡️ Real-time current weather data</li>
                    <li>📅 5-day weather forecasts with hourly details</li>
                    <li>⚖️ Side-by-side city weather comparisons</li>
                    <li>🔍 City search and multiple city weather</li>
                    <li>📊 Interactive charts and visualizations</li>
                    <li>📁 Data export (JSON/CSV)</li>
                    <li>📝 Search history tracking</li>
                    <li>🌡️ Multiple unit systems (Celsius/Fahrenheit)</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        
        with features_col2:
            st.markdown("""
            <div style="background: white; padding: 1.5rem; border-radius: 16px; 
                        box-shadow: 0 4px 20px rgba(0,0,0,0.08); margin: 1rem 0;">
                <h4 style="color: #2c3e50; margin-bottom: 1rem;">⚙️ Technical Stack</h4>
                <ul style="color: #34495e; line-height: 1.8;">
                    <li><strong>Frontend:</strong> Streamlit</li>
                    <li><strong>API:</strong> OpenWeatherMap</li>
                    <li><strong>Charts:</strong> Plotly</li>
                    <li><strong>Data:</strong> Pandas</li>
                    <li><strong>HTTP:</strong> Requests with retry logic</li>
                </ul>
                <h4 style="color: #2c3e50; margin: 1rem 0;">📊 Data Sources</h4>
                <ul style="color: #34495e; line-height: 1.8;">
                    <li>Current weather data</li>
                    <li>5-day/3-hour forecasts</li>
                    <li>Geocoding for city search</li>
                    <li>Air quality data (where available)</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        
        # Production features
        st.markdown("""
        <div style="background: linear-gradient(135deg, #00b894 0%, #00a085 100%); color: white; 
                    padding: 2rem; border-radius: 16px; margin: 2rem 0;">
            <h4 style="color: white !important; text-align: center; margin-bottom: 1.5rem;">🚀 Production Features</h4>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1rem; text-align: center;">
                <div style="background: rgba(255,255,255,0.1); padding: 1rem; border-radius: 12px;">
                    <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">✅</div>
                    <div style="font-weight: 500;">Error handling and retry logic</div>
                </div>
                <div style="background: rgba(255,255,255,0.1); padding: 1rem; border-radius: 12px;">
                    <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">✅</div>
                    <div style="font-weight: 500;">Response caching</div>
                </div>
                <div style="background: rgba(255,255,255,0.1); padding: 1rem; border-radius: 12px;">
                    <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">✅</div>
                    <div style="font-weight: 500;">Input validation</div>
                </div>
                <div style="background: rgba(255,255,255,0.1); padding: 1rem; border-radius: 12px;">
                    <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">✅</div>
                    <div style="font-weight: 500;">Logging and monitoring</div>
                </div>
                <div style="background: rgba(255,255,255,0.1); padding: 1rem; border-radius: 12px;">
                    <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">✅</div>
                    <div style="font-weight: 500;">Rate limiting protection</div>
                </div>
                <div style="background: rgba(255,255,255,0.1); padding: 1rem; border-radius: 12px;">
                    <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">✅</div>
                    <div style="font-weight: 500;">Mobile-responsive design</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Configuration and metrics
        config_col1, config_col2 = st.columns(2)
        
        with config_col1:
            st.markdown("""
            <div style="background: white; padding: 1.5rem; border-radius: 16px; 
                        box-shadow: 0 4px 20px rgba(0,0,0,0.08); margin: 1rem 0;">
                <h4 style="color: #2c3e50; margin-bottom: 1rem;">🔧 Configuration</h4>
                <ul style="color: #34495e; line-height: 1.8;">
                    <li><strong>API Provider:</strong> OpenWeatherMap</li>
                    <li><strong>Update Frequency:</strong> Real-time</li>
                    <li><strong>Cache Duration:</strong> 10 minutes</li>
                    <li><strong>Max Retries:</strong> 3 attempts</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        
        with config_col2:
            st.markdown("""
            <div style="background: white; padding: 1.5rem; border-radius: 16px; 
                        box-shadow: 0 4px 20px rgba(0,0,0,0.08); margin: 1rem 0;">
                <h4 style="color: #2c3e50; margin-bottom: 1rem;">📊 Metrics Included</h4>
                <ul style="color: #34495e; line-height: 1.8;">
                    <li>Temperature (current, min, max, feels like)</li>
                    <li>Humidity and pressure</li>
                    <li>Wind speed and direction</li>
                    <li>Weather conditions and visibility</li>
                    <li>Sunrise and sunset times</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        
        # Tip section
        st.markdown("""
        <div style="background: linear-gradient(135deg, #74b9ff 0%, #0984e3 100%); color: white; 
                    padding: 1.5rem; border-radius: 16px; margin: 2rem 0; text-align: center;">
            <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">💡</div>
            <strong>Tip:</strong> Use the sidebar to switch between different modes and adjust settings!
        </div>
        """, unsafe_allow_html=True)
        
        # API status check with enhanced styling
        if st.button("🔍 Test API Connection", key="test_api"):
            try:
                with st.spinner("Testing API connection..."):
                    test_weather = st.session_state.weather_api.get_weather("London", "metric")
                
                st.markdown("""
                <div class="success-card">
                    <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 1rem;">
                        <span style="font-size: 1.2rem;">✅</span>
                        <span style="font-weight: 600;">API connection successful!</span>
                    </div>
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
                    <div style="display: flex; align-items: center; gap: 0.5rem;">
                        <span style="font-size: 1.2rem;">❌</span>
                        <span>API connection failed: {str(e)}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    # Enhanced Footer
    st.markdown('<hr style="margin: 3rem 0; border: none; height: 2px; background: linear-gradient(135deg, #74b9ff 0%, #0984e3 100%);">', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="footer">
        <div style="background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%); 
                    padding: 2rem; border-radius: 16px; box-shadow: 0 4px 20px rgba(0,0,0,0.08);">
            <div style="text-align: center;">
                <div style="font-size: 1.5rem; margin-bottom: 1rem;">🌤️</div>
                <div style="font-size: 1.1rem; font-weight: 600; color: #2c3e50; margin-bottom: 0.5rem;">
                    Advanced Weather App
                </div>
                <div style="color: #7f8c8d; font-size: 0.95rem;">
                    Built with ❤️ using Streamlit & OpenWeatherMap API
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
