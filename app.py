import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

# ==========================================
# 1. PREMIUM PRODUCTION-READY CSS STYLESHEET
# ==========================================
st.set_page_config(layout="wide", page_title="Intelligent Environmental & GHG Dashboard")

# การฉีด CSS อย่างปลอดภัยเพื่อปรับปรุงสไตล์คอนเทนเนอร์แท้ของ Streamlit ให้ตรงปกต้นฉบับ
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&family=Sarabun:wght@400;700&display=swap');
        
        /* ตั้งค่าธีมพื้นหลังหน้าเว็บโดยรวม */
        html, body, [data-testid="stAppViewContainer"] {
            background-color: #0b111e !important;
            color: #f8fafc !important;
            font-family: 'Inter', 'Sarabun', sans-serif;
        }
        
        /* ซ่อน Scrollbar ส่วนเกินและจัดการ Padding */
        ::-webkit-scrollbar { display: none; }
        .block-container { padding: 1.5rem 2.5rem !important; }
        
        /* 📦 จัดการกล่องการ์ดผ่านการโมดิฟายด์ Streamlit Border Container แท้ */
        div[data-testid="stVerticalBlockBorderEffect"] {
            background-color: #121826 !important;
            border: 1px solid #1e293b !important;
            border-radius: 12px !important;
            padding: 18px !important;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
        }
        
        /* หัวข้อประจำการ์ดย่อย */
        .card-header {
            font-size: 11px;
            font-weight: 800;
            color: #94a3b8;
            letter-spacing: 1px;
            margin-bottom: 8px;
            text-transform: uppercase;
        }
        
        /* ล็อกรูปลักษณ์ช่อง Dropdown เลือกข้อมูล */
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
        
        /* 💧 การจัดการแสดงผลตารางและคลื่นแม่น้ำ */
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
# 2. FIXED REGIONAL DATA ENGINE
# ==========================================
years = [1930, 1950, 1970, 1990, 2000, 2010, 2026]
months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

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
# 3. TOP TELEMETRY TITLE HEADER
# ==========================================
st.markdown("""
<div style="text-align: center; margin-bottom: 25px;">
    <h1 style="color: #ffffff; font-size: 25px; font-weight: 800; margin: 0; letter-spacing: 0.5px;">INTELLIGENT ENVIRONMENTAL & GHG MONITORING DASHBOARD (THAILAND)</h1>
    <div style="color: #38bdf8; font-size: 14px; font-weight: 700; margin-top: 5px; letter-spacing: 0.5px;">แดชบอร์ดอัจฉริยะติดตามก๊าซเรือนกระจกและมลพิษ (ประเทศไทย)</div>
</div>
""", unsafe_allow_html=True)

# ==========================================
# 4. CONTROL BAR FILTERS
# ==========================================
col_f1, col_f2, col_f3, col_f4 = st.columns([2.5, 3, 3, 3])
with col_f1:
    st.markdown('<div style="font-family: monospace; font-size: 14px; color: #10b981; font-weight: 800; margin-top: 28px;">⏱️ MARCH 2026 | 13:58:55</div>', unsafe_allow_html=True)
with col_f2:
    selected_reg = st.selectbox("REGION:", list(DATA_SET.keys()))
with col_f3:
    st.selectbox("DATA SOURCE:", ["ALL SYSTEMS INTEGRATED", "SATELLITE BACKBONE"])
with col_f4:
    st.selectbox("TIME RANGE:", ["1 MONTH WINDOW", "30 YEARS HISTORICAL"])

st.markdown("<div style='margin-bottom: 15px;'></div>", unsafe_allow_html=True)
ctx = DATA_SET[selected_reg]

# ==========================================
# 5. TIER 1: HIGH-END ARC GAUGES (KEY environmental METRICS)
# ==========================================
st.markdown('<div style="font-size: 12px; font-weight: 800; color: #94a3b8; letter-spacing: 1px; margin-bottom: 10px;">KEY ENVIRONMENTAL METRICS</div>', unsafe_allow_html=True)
g1, g2, g3 = st.columns(3)

def generate_clean_gauge(value, min_val, max_val, title_text, color):
    fig = go.Figure(go.Indicator(
        mode="gauge",
        value=value,
        gauge={
            'axis': {'range':
