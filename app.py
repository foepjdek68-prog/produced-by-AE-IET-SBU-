import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# 1. SETUP: บังคับหน้ากว้าง
st.set_page_config(layout="wide", page_title="AE-IET GHG Monitor", page_icon="🌍")

# 2. CSS: Custom Styling (Cyber Environmental Theme)
# แก้ไข ERROR และปรับ Indentation ภายใน CSS f-string
st.markdown(f"""
    <style>
        /* โหลดฟอนต์ */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&family=Sarabun:wght@300;400;600;700&display=swap');

        /* ปรับแต่งพื้นหลังและฟอนต์หลัก */
        html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {{
            background-color: #050910 !important;
            color: #e2e8f0 !important;
            font-family: 'Inter', 'Sarabun', sans-serif !important;
        }}

        /* ซ่อน Scrollbar */
        ::-webkit-scrollbar {{ width: 0px; background: transparent; }}
        
        /* ปรับ Padding ของเนื้อหาหลัก */
        .block-container {{
            padding-top: 1.5rem !important;
            padding-bottom: 0rem !important;
            padding-left: 3rem !important;
            padding-right: 3rem !important;
        }}

        /* --- สไตล์หัวข้อ --- */
        .main-title {{
            font-size: 28px;
            font-weight: 700;
            color: #ffffff;
            letter-spacing: -0.5px;
            margin-bottom: 2px;
        }}
        .sub-title {{
            font-size: 14px;
            color: #36d399; /* Emerald */
            margin-bottom: 20px;
            font-weight: 300;
        }}

        /* --- Custom Metric Cards System --- */
        .metric-container {{
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
        }}
        .metric-card {{
            flex: 1;
            background: rgba(17, 25, 40, 0.75);
            backdrop-filter: blur(4px);
            border-radius: 12px;
            border: 1px solid rgba(255, 255, 255, 0.06);
            padding: 15px 20px;
            transition: transform 0.2s ease, border-color 0.2s ease;
        }}
        .metric-card:hover {{
            transform: translateY(-2px);
            border-color: rgba(34, 211, 238, 0.3);
        }}
        .metric-label {{
            font-size: 12px;
            color: #94a3b8;
            margin-bottom: 8px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        .metric-value {{
            display: flex;
            align-items: baseline;
        }}
        .metric-value-value {{
            font-size: 26px;
            font-weight: 700;
            color: #22d3ee; /* Cyan */
            line-height: 1;
        }}
        .metric-value-unit {{
            font-size: 14px;
            color: #64748b;
            margin-left: 4px;
            font-weight: 400;
        }}
        .metric-status {{
            font-size: 11px;
            margin-top: 6px;
            font-weight: 400;
        }}

        /* --- สไตล์กราฟและ Info Card --- */
        .chart-block, .info-card {{
            background: rgba(17, 25, 40, 0.5);
            border-radius: 12px;
            border: 1px solid rgba(255, 255, 255, 0.04);
            padding: 20px;
            height: 340px; /* บังคับความสูงให้เท่ากัน */
        }}
        
        .chart-caption, .info-caption {{
            font-size: 13px;
            color: #94a3b8;
            margin-bottom: 15px;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 8px;
        }}

        /* --- Sidebar Styling --- */
        section[data-testid="stSidebar"] {{
            background-color: #0b1120 !important;
            border-right: 1px solid rgba(255,255,255,0.05);
        }}
        /* ปรับแต่ง Selectbox/Radio ใน Sidebar */
        div[data-baseweb="select"] > div, div[data-testid="stMarkdownContainer"] p {{
            font-size: 14px !important;
        }}
        
        /* สไตล์แบรนด์ดิ้งด้านล่าง Sidebar */
        .brand-box {{
            margin-top: auto;
            padding: 20px;
            background: rgba(34, 211, 238, 0.03);
            border-radius: 12px;
            border: 1px solid rgba(34, 211, 238, 0.08);
            margin-bottom: 20px;
            text-align: center;
        }}

        /* สีสถานะ */
        .status-safe {{ color: #10b981; }}
        .status-warning {{ color: #fbbf24; }}
        .status-moderate {{ color: #f97316; }}
        .status-normal {{ color: #a7f3d0; }}

    </style>
""", unsafe_allow_html=True)

# 3. BASE DATA
# เพิ่มรหัสสี CSS สำหรับแต่ละสถานะเพื่อใช้ใน Custom HTML
database = {
    "CO₂ (ppm)": {"current": 433, "base": 415, "unit": "ppm", "status": "ปกติ (Safe)", "stat_class": "status-safe"},
    "CH₄ (ppb)": {"current": 1865, "base": 1820, "unit": "ppb", "status": "ปกติ (Safe)", "stat_class": "status-safe"},
    "NO₂ (ppb)": {"current": 42.1, "base": 35.0, "unit": "ppb", "status": "เฝ้าระวัง (Warning)", "stat_class": "status-warning"},
    "PM 2.5 (µg/m³)": {"current": 22.4, "base": 15.0, "unit": "µg/m³", "status": "ปานกลาง (Moderate)", "stat_class": "status-moderate"},
    "Temp (°C)": {"current": 33.2, "base": 31.5, "unit": "°C", "status": "ปกติ (Normal)", "stat_class": "status-normal"},
    "Humid (%)": {"current": 64.0, "base": 60.0, "unit": "%", "status": "ปกติ (Normal)", "stat_class": "status-normal"}
}

# 4. SIDEBAR CONTROL
with st.sidebar:
    st.markdown("### 📋 Panel ควบคุม")
    selected = st.selectbox("ตัวแปรที่ต้องการวิเคราะห์:", list(database.keys()))
    mode = st.radio("ช่วงเวลา:", ["รายวัน (30 วัน)", "รายเดือน (12 เดือน)"], horizontal=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # เครดิตด้านล่าง
    st.markdown(f"""
        <div class="brand-box">
            <img src="https://comci.southeast.ac.th/2025/img/SBU.png" width="50" style="margin-bottom:10px;">
            <div style="font-weight:700; color:white; font-size: 14px; letter-spacing:0.5px;">AE-IET [SBU]</div>
            <div style="font-size:11px; color:#64748b; margin-top:4px;">Engineering & Data Science Team</div>
            <div style="font-size:10px; color:#475569; margin-top:2px;">© 2026 Build</div>
        </div>
    """, unsafe_allow_html=True)

# 5. MAIN CONTENT AREA

# --- Header ---
st.markdown('<div class="main-title">🌍 Intelligent GHG Emission & Air Quality Tracker</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">ระบบติดตามสถานะก๊าซเรือนกระจกและคุณภาพอากาศอัจฉริยะพิกัดสถานีวิจัย</div>', unsafe_allow_html=True)

# --- Top Part: Custom Metric Cards ---
# สร้าง HTML สำหรับ 6 กล่อง Metric และปรับ Indentation ให้สมดุล
metric_html = '<div class="metric-container">'
for key, info in database.items():
    label_short = key.split(' ')[0]
    metric_html += f"""
        <div class="metric-card">
            <div class="metric-
