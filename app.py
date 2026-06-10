import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

# ==========================================
# 1. PREMIUM CYBER INFOGRAPHIC STYLE SHEET
# ==========================================
st.set_page_config(layout="wide", page_title="Intelligent Environmental Dashboard")

st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&family=Sarabun:wght@400;700&display=swap');
        
        ::-webkit-scrollbar { display: none; }
        
        html, body, [data-testid="stAppViewContainer"] { 
            background-color: #0b111e !important;
            color: #f8fafc !important;
            font-family: 'Inter', 'Sarabun', sans-serif;
        }
        .block-container { padding: 1.2rem 2.0rem !important; }
        
        /* 📦 กล่องการ์ดแยกชิ้นตามแบบ Infographic */
        .premium-box {
            background-color: #121826;
            border: 1px solid #1e293b;
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 12px;
        }
        
        .box-title {
            font-size: 11px;
            font-weight: 800;
            color: #94a3b8;
            letter-spacing: 0.8px;
            margin-bottom: 10px;
            text-transform: uppercase;
        }
        
        /* 🔒 ล็อก Dropdown และสไตล์ตัวเลือก */
        div[data-baseweb="select"] input { pointer-events: none !important; caret-color: transparent !important; }
        div[data-baseweb="select"] { background-color: #1a2333 !important; border: 1px solid #2e3c54 !important; border-radius: 4px; }
        div[data-baseweb="select"] * { color: #ffffff !important; font-size: 12px !important; }
        label[data-testid="stWidgetLabel"] { font-size: 11px !important; color: #94a3b8 !important; font-weight: bold; }
        
        /* 💧 ออกแบบระบบสายน้ำไหลและปุ่มสถานะ (Water Badge Engine) */
        .river-row {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 4px 0;
            height: 42px;
        }
        .river-name { font-size: 12px; font-weight: 700; color: #38bdf8; min-width: 110px; }
        .river-svg { flex-grow: 1; margin: 0 10px; height: 20px; }
        .badge-container { display: flex; gap: 6px; }
        .status-pill { padding: 3px 10px; border-radius: 12px; font-size: 9px; font-weight: 800; text-align: center; color: white; width: 65px; }
        .pill-green { background-color: #10b981; box-shadow: 0 0 8px rgba(16,185,129,0.3); }
        .pill-red { background-color: #ef4444; box-shadow: 0 0 8px rgba(239,68,68,0.3); }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. FIXED STATIC DATA REGISTRY
# ==========================================
years = [1930, 1950, 1970, 1990, 2000, 2010, 2026]
months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

DATA_SET = {
    "📌 CENTRAL (ภาคกลาง)": {
        "co2": 421.5, "co2_sub": "+0.3% vs. last month", "co2_sub_col": "#ef4444",
        "temp": 1.8, "temp_lbl": "+1.8°C", "aqi": 85, "aqi_lbl": "Moderate", "aqi_col": "#eab308",
        "co2_history": [250, 390, 510, 680, 830, 1020, 1420],
        "pm25": [12, 15, 19, 25, 32, 29, 21, 14, 12, 11, 13, 15],
        "temp_list": [18, 19, 22, 26, 29, 28, 27, 26, 25, 23, 20, 18]
    },
    "📌 NORTH (ภาคเหนือ)": {
        "co2": 412.8, "co2_sub": "+0.1% vs. last month", "co2_sub_col": "#10b981",
        "temp": 2.4, "temp_lbl": "+2.4°C", "aqi": 165, "aqi_lbl": "Unhealthy", "aqi_col": "#ef4444",
        "co2_history": [210, 310, 430, 570, 710, 890, 1150],
        "pm25": [45, 68, 95, 120, 75, 30, 22, 19, 24, 38, 48, 55],
        "temp_list": [14, 17, 23, 28, 27, 26, 25, 24, 23, 21, 17, 14]
    }
}

# ==========================================
# 3. TOP TELEMETRY TITLE HEADER
# ==========================================
st.markdown("""
<div style="text-align: center; margin-bottom: 18px;">
    <h1 style="color: #ffffff; font-size: 23px; font-weight: 800; margin: 0; letter-spacing: 0.5px;">INTELLIGENT ENVIRONMENTAL & GHG MONITORING DASHBOARD (THAILAND)</h1>
    <div style="color: #38bdf8; font-size: 13px; font-weight: 700; margin-top: 3px;">แดชบอร์ดอัจฉริยะติดตามก๊าซเรือนกระจกและมลพิษ (ประเทศไทย)</div>
</div>
""", unsafe_allow_html=True)

# ==========================================
# 4. CONTROL BAR FILTERS
