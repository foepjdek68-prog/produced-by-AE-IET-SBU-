import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# 1. INITIAL SETUP (ตั้งค่าหน้าจอให้กว้างพอดีสัดส่วน)
st.set_page_config(layout="wide", page_title="Environmental & GHG Dashboard", initial_sidebar_state="collapsed")

# 2. COMPACT CYBER DARK THEME CSS (ปรับลดขนาดโครงสร้างให้กะทัดรัด ไม่ใหญ่เกินไป)
st.markdown("""
    <style>
        ::-webkit-scrollbar { display: none; }
        html, body, [data-testid="stAppViewContainer"] { 
            background-color: #0b111e !important;
            color: #ffffff !important;
        }
        /* กระชับพื้นที่ขอบหน้าจอ */
        .block-container { padding: 0.6rem 1.2rem !important; }
        
        /* ส่วนหัวข้อหลัก ขนาดพอดีคำ */
        .main-title-box { text-align: center; margin-bottom: 10px; }
        .title-main { font-size: 19px; font-weight: 800; color: #ffffff; letter-spacing: 0.5px; margin: 0; }
        .title-sub { font-size: 12px; color: #64748b; margin-top: 2px; }
        
        /* แถบควบคุมบนหน้าจอ */
        .control-bar {
            background-color: #0f172a; padding: 6px 12px; border-radius: 6px;
            border: 1px solid #1e293b; margin-bottom: 10px;
        }
        
        /* กล่องแสดงผลย่อย (Compact Box) */
        .panel-box {
            background-color: #0f172a; border: 1px solid #1e293b; border-radius: 6px;
            padding: 10px; height: 100%; box-shadow: 0 4px 10px rgba(0,0,0,0.3);
        }
        .panel-title { font-size: 11px; color: #38bdf8; font-weight: 700; margin-bottom: 6px; text-transform: uppercase; }
        
        /* การ์ดสรุปตัวเลขแบบพอดีสายตา */
        .metric-card-compact {
            background: linear-gradient(180deg, #141b2d 0%, #0c101b 100%);
            border: 1px solid #22d3ee33; border-radius: 6px; padding: 8px 12px; text-align: center;
        }
        .card-label { font-size: 10px; color: #94a3b8; font-weight: 600; }
        .card-value { font-size: 24px; font-weight: 800; color: #22d3ee; margin: 2px 0; }
        .card-unit { font-size: 11px; color: #475569; font-weight: bold; }

        /* 🔒 ล็อกส่วน INPUT ของ SELECTBOX เพื่อให้จิ้มเลือกได้อย่างเดียว แป้นพิมพ์ไม่เด้ง */
        div[data-baseweb="select"] input {
            pointer-events: none !important;
            caret-color: transparent !important;
        }
        div[data-baseweb="select"] { background-color: #1e293b !important; border: 1px solid #334155 !important; border-radius: 4px; }
        div[data-baseweb="select"] * { color: #ffffff !important; font-size: 12px !important; }
        label[data-testid="stWidgetLabel"] { font-size: 11px !important; color: #94a3b8 !important; margin-bottom: 2px !important; font-weight: 600; }
    </style>
""", unsafe_allow_html=True)

# 3. RELIABLE DATA MATRIX (คลังข้อมูลมลพิษ)
years_30y = [1930, 1950, 1970, 1990, 2000, 2010, 2026]

CORE_DATA = {
    "ภาคกลาง (Central Thailand)": {
        "co2_now": 421.5, "ch4_now": 1919.4, "no2_now": 330.8, "temp_anomaly": 1.8, "aqi_val": 85, "aqi_txt": "ปานกลาง (Moderate)", "co_now": 1.2,
        "co2_history": [290, 312, 335, 362, 378, 395, 421.5],
        "ch4_history": [1620, 1690, 1740, 1810, 1845, 1880, 1919.4],
        "no2_history": [150, 190, 225, 270, 295, 315, 330.8],
        "map_coords": [13.7563, 100.5018],
        "time_modes": {
            "1 เดือนล่าสุด (1 Month)": {"x": ["สัปดาห์ 1", "สัปดาห์ 2", "สัปดาห์ 3", "สัปดาห์ 4"], "pm25": [35, 58, 85, 42], "temp": [26, 28, 29, 27]},
            "1 ปีล่าสุด (1 Year)": {"x": ["ม.ค.", "มี.ค.", "พ.ค.", "ก.ค.", "ก.ย.", "พ.ย."], "pm25": [65, 85, 30, 15, 22, 45], "temp": [24, 28, 30, 28, 26, 24]},
            "5 ปีล่าสุด (5 Years)": {"x": ["2022", "2023", "2024", "2025", "2026"], "pm25": [38, 42, 45, 40, 43], "temp": [1.4, 1.5, 1.7, 1.6, 1.8]}
        },
        "breakdown": {"PM2.5": [40, 35, 25], "PM10": [50, 40, 10], "NO₂": [45, 35, 20], "SO₂": [80, 15, 5]}
    },
    "ภาคเหนือ (Northern Thailand)": {
        "co2_now": 412.8, "ch4_now": 1850.2, "no2_now": 120.4, "temp_anomaly": 2.4, "aqi_val": 165, "aqi_txt": "เริ่มมีผลต่อสุขภาพ", "co_now": 2.3,
        "co2_history": [288, 305, 328, 352, 368, 384, 412.8],
        "ch4_history": [1590, 1640, 1700, 1760, 1790, 1820, 1850.2],
        "no2_history":
