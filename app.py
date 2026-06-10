import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

# ==========================================
# 1. PAGE CONFIGURATION (กำหนดสเกลแดชบอร์ดความหนาแน่นสูง)
# ==========================================
st.set_page_config(layout="wide", page_title="Intelligent Environmental Dashboard", page_icon="🌍")

# ฉีดแนวคิด CSS เพื่อบังคับโครงสร้างพื้นหลัง และบล็อกคีย์บอร์ดในช่อง Selectbox
st.markdown("""
    <style>
        /* ซ่อน Scrollbar แนวนอนและแนวตั้งเพื่อบีบทุกอย่างให้อยู่ในหน้าเดียว */
        ::-webkit-scrollbar { display: none; }
        
        html, body, [data-testid="stAppViewContainer"] { 
            background-color: #020617 !important;
            color: #f8fafc !important;
            font-family: 'Inter', 'Sarabun', sans-serif;
        }
        .block-container { padding: 0.8rem 1.5rem !important; }
        
        /* ตกแต่งกล่องข้อความหัวเรื่องหลัก */
        .hdr-box { text-align: center; margin-bottom: 8px; }
        .hdr-title { font-size: 22px; font-weight: 800; color: #ffffff; letter-spacing: 0.5px; margin: 0; }
        .hdr-sub { font-size: 13px; color: #94a3b8; margin-top: 2px; }
        
        /* 🛠️ บังคับสไตล์กล่อง Container ของ Streamlit ให้กลายเป็นการ์ดแดชบอร์ดสีน้ำเงินเข้มตามแบบ */
        div[data-testid="stVerticalBlockBorderWrapper"] {
            background-color: #1e293b !important;
            border: 1px solid #334155 !important;
            border-radius: 6px !important;
            padding: 10px !important;
            margin-bottom: 0px !important;
        }
        
        /* ตัวหนังสือหัวข้อย่อยประจำการ์ด */
        .card-header-text { 
            font-size: 11px; color: #22d3ee; font-weight: 700; 
            margin-bottom: 4px; text-transform: uppercase; letter-spacing: 0.5px;
        }
        
        /* 🔒 ล็อกอินพุตของช่อง Selectbox ทั้งหมด ห้ามเปิดแป้นพิมพ์พิมพ์ข้อความ */
        div[data-baseweb="select"] input {
            pointer-events: none !important;
            caret-color: transparent !important;
        }
        div[data-baseweb="select"] { background-color: #020617 !important; border: 1px solid #475569 !important; border-radius: 4px; }
        div[data-baseweb="select"] * { color: #f8fafc !important; font-size: 11px !important; }
        label[data-testid="stWidgetLabel"] { font-size: 11px !important; color: #94a3b8 !important; margin-bottom: 1px !important; font-weight: bold; }
        
        /* สไตล์ไฟสถานะในตารางคุณภาพน้ำ */
        .status-dot { padding: 2px 8px; border-radius: 12px; font-size: 10px; font-weight: 800; display: inline-block; }
        .status-pass { background-color: #059669; color: #ffffff; }
        .status-warn { background-color: #dc2626; color: #ffffff; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. DATA MATRIX (ฐานข้อมูลจำลองสลับตามภูมิภาค)
# ==========================================
years_axis = [1930, 1950, 1970, 1990, 2000, 2010, 2026]
months_axis = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

REGIONAL_DATA = {
    "📌 CENTRAL (ภาคกลาง)": {
        "co2": 421.5, "temp": 1.8, "aqi": 85, "aqi_status": "Moderate", "aqi_color": "#eab308",
        "co2_history": [240, 320, 490, 680, 820, 990, 1420],
        "pm25_series": [22, 26, 35, 40, 28, 18, 15, 14, 19, 23, 25, 30],
        "temp_series": [26, 28, 30, 32, 31, 30, 29, 29, 28, 27, 26, 25]
    },
    "📌 NORTH (ภาคเหนือ)": {
        "co2": 412.8, "temp": 2.4, "aqi": 165, "aqi_status": "Unhealthy", "aqi_color": "#ef4444",
        "co2_history": [210, 270, 410, 550, 690, 840, 1150],
        "pm25_series": [45, 68, 95, 120, 75, 30, 22, 19, 24, 38, 48, 55],
        "temp_series": [20, 23, 27, 31, 30, 29, 28, 28, 27, 25, 22, 19]
    }
}

# ==========================================
# 3. HEADER
# ==========================================
st.markdown("""
<div class="hdr-box">
    <div class="hdr-title">INTELLIGENT ENVIRONMENTAL & GHG MONITORING DASHBOARD (THAILAND)</div>
    <div class="hdr-sub">ระบบแดชบอร์ดติดตามก๊าซเรือนกระจกวิเคราะห์สเกลโครงสร้างความหนาแน่นสูง</div>
</div>
""", unsafe_allow_html=True)

# ==========================================
# 4. TOP MENU CONTROL BAR (แถบเดี่ยวสำหรับตัวกรองข้อมูลทั้งหมด)
# ==========================================
with st.container():
    c1, c2, c3, c4 = st.columns([2.5, 2.5, 2.5, 2.5])
    with c1:
        st.markdown(f'<div style="font-family:monospace; font-size:12px; color:#22d3ee; font-weight:700; margin-top:16px;">🕒 MARCH 2026 | 20:26:26</div>', unsafe_allow_html=True)
    with c2:
        selected_region = st.selectbox("REGION (ภูมิภาค ตรวจสอบ)", list(REGIONAL_DATA.keys()))
    with c3:
        st.selectbox("DATA SOURCE (แหล่งอ้าง
