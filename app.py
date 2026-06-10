import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime

# ==========================================
# 1. PAGE AND ASSET CONFIGURATION
# ==========================================
st.set_page_config(layout="wide", page_title="Intelligent Environmental & GHG Dashboard")

# ฉีดสไตล์ CSS สำหรับการปรับแต่งส่วนติดต่อผู้ใช้ระดับองค์กร (Enterprise UI)
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght=400;600;700;800&family=Sarabun:wght=400;700&display=swap');
        
        html, body, [data-testid="stAppViewContainer"] {
            background-color: #0b111e !important;
            color: #f8fafc !important;
            font-family: 'Inter', 'Sarabun', sans-serif;
        }
        
        ::-webkit-scrollbar { display: none; }
        .block-container { padding: 1.5rem 2.5rem !important; }
        
        .stElementContainer div[data-testid="stVerticalBlockBorderEffect"] {
            background-color: #121826 !important;
            border: 1px solid #1e293b !important;
            border-radius: 12px !important;
            padding: 20px !important;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
        }
        
        .card-header {
            font-size: 11px;
            font-weight: 800;
            color: #94a3b8;
            letter-spacing: 1px;
            margin-bottom: 12px;
            text-transform: uppercase;
        }
        
        div[data-baseweb="select"] {
            background-color: #1a2333 !important;
            border: 1px solid #2e3c54 !important;
            border-radius: 6px;
        }
        div[data-baseweb="select"] * {
            color: #ffffff !important;
            font-size: 13px !important;
        }
        label[data-testid="stWidgetLabel"] {
            font-size: 11px !important;
            color: #94a3b8 !important;
            font-weight: 700;
            text-transform: uppercase;
        }
        
        .river-table { width: 100%; border-collapse: collapse; margin-top: 5px; }
        .river-row { height: 45px; border-bottom: 1px solid #1e293b; }
        .river-name { font-size: 13px; font-weight: 700; color: #38bdf8; width: 30%; }
        .river-wave { width: 40%; text-align: center; }
        .river-badges { width: 30%; text-align: right; display: flex; justify-content: flex-end; gap: 8px; align-items: center; height: 45px; }
        .status-badge {
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 10px;
            font-weight: 800;
            color: #ffffff;
            letter-spacing: 0.5px;
            display: inline-block;
            min-width: 65px;
            text-align: center;
        }
        .badge-pass { background-color: #10b981; box-shadow: 0 0 10px rgba(16, 185, 129, 0.2); }
        .badge-warn { background-color: #ef4444; box-shadow: 0 0 10px rgba(239, 68, 68, 0.2); }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. DATA INFRASTRUCTURE (MOCK ENGINE)
# ==========================================
years = [1930, 1950, 1970, 1990, 2000, 2010, 2026]
months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

# ตรวจสอบและแก้ไขชื่อตัวแปรให้สมบูรณ์ ป้องกันการเกิด NameError
DATA_SET = {
    "CENTRAL (ภาคกลาง)": {
        "co2": 421.5, "co2_sub": "+0.3% vs. last month", "co2_sub_col": "#ef4444",
        "temp": 1.8, "temp_lbl": "+1.8°C", "aqi": 85, "aqi_lbl": "Moderate", "aqi_col": "#eab308",
        "co2_history": [250, 390, 520, 680, 810, 1020, 1420],
        "pm25": [12, 14, 18, 26, 32, 28, 22, 15, 12, 11, 13, 16],
        "temp_list": [18, 19, 22, 26, 29, 28, 27, 26, 25, 23, 20, 18]
    },
    "NORTH (ภาคเหนือ)": {
        "co2": 412.8, "co2_sub": "+0.1% vs. last month", "co2_sub_col": "#10b981",
        "temp": 2.4, "temp_lbl": "+2.4°C", "aqi": 165, "aqi_lbl": "Unhealthy", "aqi_col": "#ef4444",
        "co2_history": [210, 310, 430, 570, 710, 890, 1150],
        "pm25": [45, 68, 95, 120, 75, 30, 22, 19, 24, 38, 48, 55],
        "temp_list": [14, 17, 23, 28, 27, 26, 25, 24, 23, 21, 17, 14]
    }
}

# ==========================================
# 3. HEADER SECTION
# ==========================================
st.markdown("""
<div style="text-align: center; margin-bottom: 25px;">
    <h1 style="color: #ffffff; font-size: 25px; font-weight: 800; margin: 0; letter-spacing: 0.5px;">INTELLIGENT ENVIRONMENTAL & GHG MONITORING DASHBOARD (THAILAND)</h1>
    <div style="color: #38bdf8; font-size: 14px; font-weight: 700; margin-top: 5px; letter-spacing: 0.5px;">แดชบอร์ดอัจฉริยะติดตามก๊าซเรือนกระจกและมลพิษ (ประเทศไทย)</div>
</div>
""", unsafe_allow_html=True)

# ==========================================
# 4. CONTROL PANEL FILTERS
# ==========================================
col_f1, col_f2, col_f3, col_f4 = st.columns([2.8, 2.9, 3.1, 3.2])
with col_f1:
    time_now = datetime.now().strftime("%B %Y | %H:%M:%S").upper()
    st.markdown(f'<div style="font-family: monospace; font-size: 14px; color: #10b981; font-weight: 800; margin-top: 28px;">⏱️ {time_now}</div>', unsafe_allow_html=True)
with col_f2:
    selected_reg = st.selectbox("REGION:", list(DATA_SET.keys()))
with col_f3:
    st.selectbox("DATA SOURCE:", ["ALL SYSTEMS INTEGRATED", "SATELLITE BACKBONE"])
with col_f4:
    st.selectbox("TIME RANGE:", ["1 MONTH WINDOW", "30 YEARS HISTORICAL"])

st.markdown("<div style='margin-bottom: 15px;'></div>", unsafe_allow_html=True)
ctx = DATA_SET[selected_reg]

# ==========================================
# 5. VISUALIZATION: KPI GAUGES
# ==========================================
st.markdown('<div style="font-size: 12px; font-weight: 800; color: #94a3b8; letter-spacing: 1px; margin-bottom: 10px;">KEY ENVIRONMENTAL METRICS</div>', unsafe_allow_html=True)
g1, g2, g3 = st.columns(3)

def generate_clean_gauge(value, min_val, max_val, title_text, color):
    fig = go.Figure(go.Indicator(
        mode="gauge",
        value=value,
        gauge={
            'axis': {'range': [min_val, max_val], 'visible': False},
            'bar': {'color': color, 'thickness': 0.26},
            'bgcolor': '#1a2333',
            'borderwidth': 0
        }
    ))
    fig.update_layout(
        title={'text': f"<b>{title_text}</b>", 'font': {'size': 11, 'color': '#94a3b8', 'family': 'Inter'}, 'y': 0.95},
        height=100,
        margin=dict(t=40, b=10, l=35, r=35),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    return fig

with g1:
    with st.container(border=True):
        st.plotly_chart(generate_clean_gauge(ctx["co2"], 350, 500, "1 🔵 ATMOSPHERIC CO₂ LEVEL", "#38bdf8"), use_container_width=True, config={'displayModeBar': False})
        st.markdown(f'<div style="text-align: center; font-size: 26px; font-weight: 800; color: #ffffff; margin-top: -15px;">{ctx["co2"]} <span style="font-size:14px; color:#94a3b8; font-weight:400;">ppm</span></div>', unsafe_allow_html=True)
        st.markdown(f'<div style="text-align: center; font-size: 11px; font-weight: 700; color: {ctx["co2_sub_col"]}; margin-bottom: 5px;">{ctx["co2_sub"]}</div>', unsafe_allow_html=True)

with g2:
    with st.container(border=True):
        # แก้ไขอาร์กิวเมนต์สีของกราฟ Gauge ให้เป็น String Literal ห้ามใส่ตัวแปรลอย ป้องกัน NameError
        st.plotly_chart(generate_clean_gauge(ctx["temp"], 0, 4, "2 🟠 AV. TEMPERATURE ANOMALY", "#f97316"), use_container_width=True, config={'displayModeBar': False})
        st.markdown(f'<div style="text-align: center; font-size: 26px; font-weight: 800; color: #f97316; margin-top: -15px;">{ctx["temp_lbl"]}</div>', unsafe_allow_html=True)
        st.markdown('<div style="text-align: center; font-size: 11px; font-weight: 700; color: #64748b; margin-bottom: 5px;">Anomaly Threshold</div>', unsafe_allow_html=True)

with g3:
    with st.container(border=True):
        st.plotly_chart(generate_clean_gauge(ctx["aqi"], 0, 200, "3 🟡 AIR QUALITY INDEX (AQI)", ctx["aqi_col"]), use_container_width=True, config={'displayModeBar': False})
        st.markdown(f'<div style="text-align: center; font-size: 26px; font-weight: 800; color: #ffffff; margin-top: -15px;">{ctx["aqi"]}</div>', unsafe_allow_html=True)
        st.markdown(f'<div style="text-align: center; font-size: 11px; font-weight: 700; color: {ctx["aqi_col"]}; margin-bottom: 5px;">{ctx["aqi_lbl"]}</div>', unsafe_allow_html=True)

# ==========================================
# 6. VISUALIZATION: REGIONAL MAP & TIMELINES
# ==========================================
m_left, m_right = st.columns([1.1, 1.0])

with m_left:
    with st.container(border=True):
        st.markdown('<div class="card-header" style="color:#38bdf8;">GHG & POLLUTION HOTSPOTS (BANGKOK & PERIPHERY)</div>', unsafe_allow_html=True)
        
        grid_res = 100
        x_axis = np.linspace(0, 10, grid_res)
        y_axis = np.linspace(0, 10, grid_res)
        MX, MY = np.meshgrid(x_axis, y_axis)
        MZ = np.exp(-((MX - 5)**2 + (MY - 5)**2) / 5.5) * 160 + np.exp(-((MX - 7.5
