import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# 1. SETUP & CONFIGURATION (ตั้งค่าหน้าจอขยายกว้างเต็มจอ)
st.set_page_config(layout="wide", page_title="Environmental & GHG Dashboard")

# 2. CLEAN & READABLE MODERN CSS (เน้นตัวใหญ่ สบายตา ไม่อึดอัด)
st.markdown("""
    <style>
        /* ปล่อยให้หน้าเพจเลื่อนลงได้ตามธรรมชาติ ตัวหนังสือจะได้ไม่ถูกบีบจนเล็ก */
        html, body, [data-testid="stAppViewContainer"] { 
            background-color: #0b111e !important;
            color: #ffffff !important;
            font-family: 'Helvetica Neue', Arial, sans-serif;
        }
        .block-container { padding: 1.5rem 2.0rem !important; }
        
        /* ส่วนหัวข้อหลักใหญ่ชัดเจน */
        .main-title-box { text-align: center; margin-bottom: 25px; padding-bottom: 15px; border-bottom: 2px solid #1e293b; }
        .title-main { font-size: 26px; font-weight: 800; color: #ffffff; letter-spacing: 0.5px; }
        .title-sub { font-size: 16px; color: #94a3b8; margin-top: 5px; }
        
        /* แผงควบคุมกลุ่มปุ่มกด */
        .control-section {
            background-color: #0f172a; padding: 15px; border-radius: 8px; 
            border: 1px solid #1e293b; margin-bottom: 20px;
        }
        
        /* กล่องเนื้อหาแยกเป็นสัดส่วน */
        .panel-box {
            background-color: #0f172a; border: 1px solid #1e293b; border-radius: 8px;
            padding: 15px; height: 100%; box-shadow: 0 4px 6px rgba(0,0,0,0.2); margin-bottom: 15px;
        }
        .panel-title { font-size: 15px; color: #38bdf8; font-weight: 700; margin-bottom: 10px; text-transform: uppercase; }
        
        /* การ์ดแสดงตัวเลขตัวใหญ่พิเศษ */
        .metric-card-large {
            background: linear-gradient(180deg, #141b2d 0%, #0c101b 100%);
            border: 1px solid #22d3ee44; border-radius: 8px; padding: 15px; text-align: center;
        }
        .card-label { font-size: 13px; color: #94a3b8; font-weight: 600; margin-bottom: 5px; }
        .card-value { font-size: 32px; font-weight: 800; color: #22d3ee; }
        .card-unit { font-size: 14px; color: #64748b; font-weight: bold; }
        
        /* ปรับแต่งสไตล์ปุ่มกดวิทยุ (Radio) ให้ดูเหมือนแถบเมนูจิ้มง่าย */
        div[data-testid="stRadio"] > label { font-size: 14px !important; font-weight: 700 !important; color: #38bdf8 !important; margin-bottom: 6px; }
        div[data-testid="stRadio"] div[role="radiogroup"] { gap: 15px; }
    </style>
""", unsafe_allow_html=True)

# 3. RELIABLE DATA MATRIX (ฐานข้อมูลสารมลพิษ)
years_30y = [1930, 1950, 1970, 1990, 2000, 2010, 2026]

CORE_DATA = {
    "📌 ภาคกลาง (Central)": {
        "co2_now": 421.5, "ch4_now": 1919.4, "no2_now": 330.8, "temp_anomaly": 1.8, "aqi_val": 85, "aqi_txt": "คุณภาพอากาศปานกลาง (Moderate)", "co_now": 1.2,
        "co2_history": [290, 312, 335, 362, 378, 395, 421.5],
        "ch4_history": [1620, 1690, 1740, 1810, 1845, 1880, 1919.4],
        "no2_history": [150, 190, 225, 270, 295, 315, 330.8],
        "map_coords": [13.7563, 100.5018],
        "time_modes": {
            "📊 1 เดือนล่าสุด": {"x": ["สัปดาห์ 1", "สัปดาห์ 2", "สัปดาห์ 3", "สัปดาห์ 4"], "pm25": [35, 58, 85, 42], "temp": [26, 28, 29, 27]},
            "📊 1 ปีล่าสุด": {"x": ["ม.ค.", "มี.ค.", "พ.ค.", "ก.ค.", "ก.ย.", "พ.ย."], "pm25": [65, 85, 30, 15, 22, 45], "temp": [24, 28, 30, 28, 26, 24]},
            "📊 5 ปีล่าสุด": {"x": ["2022", "2023", "2024", "2025", "2026"], "pm25": [38, 42, 45, 40, 43], "temp": [1.4, 1.5, 1.7, 1.6, 1.8]}
        },
        "breakdown": {"PM2.5": [40, 35, 25], "PM10": [50, 40, 10], "NO₂": [45, 35, 20], "SO₂": [80, 15, 5]}
    },
    "📌 ภาคเหนือ (North)": {
        "co2_now": 412.8, "ch4_now": 1850.2, "no2_now": 120.4, "temp_anomaly": 2.4, "aqi_val": 165, "aqi_txt": "เริ่มมีผลต่อสุขภาพ (Unhealthy)", "co_now": 2.3,
        "co2_history": [288, 305, 328, 352, 368, 384, 412.8],
        "ch4_history": [1590, 1640, 1700, 1760, 1790, 1820, 1850.2],
        "no2_history": [60, 75, 90, 102, 110, 115, 120.4],
        "map_coords": [18.7883, 98.9853],
        "time_modes": {
            "📊 1 เดือนล่าสุด": {"x": ["สัปดาห์ 1", "สัปดาห์ 2", "สัปดาห์ 3", "สัปดาห์ 4"], "pm25": [90, 120, 165, 80], "temp": [22, 25, 27, 24]},
            "📊 1 ปีล่าสุด": {"x": ["ม.ค.", "มี.ค.", "พ.ค.", "ก.ค.", "ก.ย.", "พ.ย."], "pm25": [95, 150, 45, 12, 18, 65], "temp": [19, 26, 29, 27, 24, 21]},
            "📊 5 ปีล่าสุด": {"x": ["2022", "2023", "2024", "2025", "2026"], "pm25": [55, 62, 70, 58, 66], "temp": [1.9, 2.1, 2.4, 2.2, 2.4]}
        },
        "breakdown": {"PM2.5": [15, 25, 60], "PM10": [30, 30, 40], "NO₂": [70, 20, 10], "SO₂": [90, 8, 2]}
    }
}

# 4. TOP MAIN HEADER
st.markdown("""
<div class="main-title-box">
    <div class="title-main">INTELLIGENT ENVIRONMENTAL & GHG MONITORING DASHBOARD</div>
    <div class="title-sub">ระบบแดชบอร์ดอัจฉริยะติดตามก๊าซเรือนกระจกและมลพิษทางอากาศ (ประเทศไทย)</div>
</div>
""", unsafe_allow_html=True)

# 5. CONTROL PANEL (ปรับเป็นแบบวิทยุ ปุ่มจิ้มเลือกแนวนอน ห้ามพิมพ์ 100%)
st.markdown('<div class="control-section">', unsafe_allow_html=True)
c_col1, c_col2, c_col3 = st.columns(3)
with c_col1:
    sel_region = st.radio("📍 เลือกภูมิภาคที่ต้องการดูข้อมูล:", list(CORE_DATA.keys()), horizontal=True)
with c_col2:
    sel_metric = st.radio("💨 เลือกก๊าซมลพิษหลัก:", ["CO₂ (คาร์บอนฯ)", "CH₄ (มีเทน)", "NO₂ (ไนโตรเจนฯ)"], horizontal=True)
with c_col3:
    sel_time = st.radio("📅 เลือกช่วงเวลาแสดงผลกรรองข้อมูล:", ["📊 1 เดือนล่าสุด", "📊 1 ปีล่าสุด", "📊 5 ปีล่าสุด"], horizontal=True)
st.markdown('</div>', unsafe_allow_html=True)

# Mapping Data ให้สอดคล้องกันตามปุ่มที่จิ้มเลือก
dataset = CORE_DATA[sel_region]
metric_short = sel_metric.split(" ")[0]

if metric_short == "CO₂":
    active_value, active_unit, active_range, active_history = dataset["co2_now"], "ppm", [250, 460], dataset["co2_history"]
elif metric_short == "CH₄":
    active_value, active_unit, active_range, active_history = dataset["ch4_now"], "ppb", [1500, 2000], dataset["ch4_history"]
else:
    active_value, active_unit, active_range, active_history = dataset["no2_now"], "ppb", [0, 400], dataset["no2_history"]

# --- 6. SECTION 1: ตัวเลขสรุปภาพรวมขนาดใหญ่ (MAIN VALUES) ---
st.markdown("### 📈 ข้อมูลสรุปสถานการณ์ปัจจุบัน (Current Summary)")
m_col1, m_col2, m_col3 = st.columns(3)

with m_col1:
    st.markdown(f'<div class="metric-card-large"><div class="card-label">1. ระดับก๊าซ {metric_short} ในชั้นบรรยากาศ</div><div class="card-value">{active_value} <span class="card-unit">{active_unit}</span></div></div>', unsafe_allow_html=True)
with m_col2:
    st.markdown(f'<div class="metric-card-large"><div class="card-label">2. ค่าความเบี่ยงเบนอุณหภูมิสะสม</div><div class="card-value" style="color:#f97316;">+{dataset["temp_anomaly"]} <span class="card-unit">°C</span></div></div>', unsafe_allow_html=True)
with m_col3:
    aqi_color = "#eab308" if dataset["aqi_val"] <= 100 else "#ef4444"
    st.markdown(f'<div class="metric-card-large"><div class="card-label">3. ดัชนีคุณภาพอากาศสากล (AQI)</div><div class="card-value" style="color:{aqi_color};">{dataset["aqi_val"]}</div><div style="font-size:12px; color:{aqi_color}; font-weight:bold; margin-top:2px;">{dataset["aqi_txt"]}</div></div>', unsafe_allow_html=True)

# --- 7. SECTION 2: แผงกราฟขนาดใหญ่ มองง่าย สบาย
