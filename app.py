import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# 1. SETUP & CONFIGURATION
st.set_page_config(layout="wide", page_title="Dashboard Tracking GHGs Emission", initial_sidebar_state="collapsed")

# 2. ADVANCED CSS: ถอดแบบโครงสร้าง Layout และดีไซน์แผงควบคุมจากรูปภาพ 100%
st.markdown("""
    <style>
        /* ซ่อนแถบเลื่อนและล็อกขนาดหน้าจอ */
        ::-webkit-scrollbar { display: none; }
        html, body, [data-testid="stAppViewContainer"] { 
            overflow: hidden !important; 
            height: 100vh !important; 
            background-color: #0b0f19 !important;
        }
        
        .block-container { padding: 0.8rem 1.5rem !important; }
        
        /* --- HEADER STYLING --- */
        .top-header {
            display: flex; justify-content: space-between; align-items: center;
            padding-bottom: 8px; border-bottom: 1px solid #1e293b; margin-bottom: 12px;
        }
        .main-title { font-size: 20px; font-weight: 800; color: #ffffff; letter-spacing: 0.5px; }
        .clock-display { font-family: monospace; font-size: 16px; color: #94a3b8; font-weight: 700; }

        /* --- CONTROL SELECTORS --- */
        .selector-label { font-size: 10px; color: #64748b; font-weight: 700; text-transform: uppercase; margin-bottom: 2px; }

        /* --- PANEL CONTAINER CARD --- */
        .panel-box {
            background-color: #0f172a; border: 1px solid #1e293b; border-radius: 8px;
            padding: 12px; height: 100%; box-shadow: 0 4px 20px rgba(0,0,0,0.4);
        }
        .panel-header { 
            font-size: 11px; color: #94a3b8; font-weight: 700; 
            text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px; 
        }
        
        /* --- SMALL METRIC CARD --- */
        .metric-card {
            background: linear-gradient(180deg, #141b2d 0%, #0c101b 100%);
            border: 1px solid #22d3ee33; border-radius: 6px; padding: 10px; height: 85px;
        }
        .metric-label { font-size: 10px; color: #94a3b8; font-weight: 600; }
        .metric-value { font-size: 22px; font-weight: 700; color: #22d3ee; margin-top: 2px; }
        .metric-unit { font-size: 12px; color: #64748b; font-weight: 500; }
        .metric-sub { font-size: 10px; color: #10b981; margin-top: 1px; }

        /* ปรับสไตล์ Dropdown ของ Streamlit ให้กลืนกับธีมมืด */
        div[data-baseweb="select"] { background-color: #1e293b !important; border: 1px solid #334155 !important; border-radius: 4px; }
        div[data-baseweb="select"] * { color: #ffffff !important; font-size: 12px !important; }
    </style>
""", unsafe_allow_html=True)

# 3. COMPLETE MOCK DATA (แยกค่าของแต่ละภูมิภาคให้แตกต่างกันอย่างชัดเจนเพื่อให้เห็นความเปลี่ยนแปลง)
DATA_BANK = {
    "ภาคกลาง (Bangkok & Periphery)": {
        "metrics": {
            "CO₂": {"val": 421.5, "sub": "+0.3% vs last month", "unit": "ppm"},
            "Temp Anomaly": {"val": 1.8, "sub": "Above baseline", "unit": "°C"},
            "AQI": {"val": 85, "sub": "Moderate", "unit": ""},
            "CH₄": {"val": 1919.4, "sub": "from station 1", "unit": "ppb"},
            "NO₂": {"val": 330.8, "sub": "traffic emissions", "unit": "ppb"},
            "Humidity": {"val": 64, "sub": "Relative", "unit": "%"}
        },
        "map_center": [13.7563, 100.5018],
        "line_trend": [250, 450, 680, 920, 1180, 1450],
        "stack_data": {'PM2.5': [50, 30, 20], 'PM10': [60, 25, 15], 'NO₂': [40, 35, 25], 'SO₂': [70, 15, 15], 'O₃': [55, 30, 15]},
        "river_do": ["4.2 mg/L", "2.1 mg/L", "5.5 mg/L"],
        "river_status": ["🟢 Normal", "🔴 Unhealthy", "🟢 Normal"]
    },
    "ภาคเหนือ (Chiang Mai & Upper North)": {
        "metrics": {
            "CO₂": {"val": 415.2, "sub": "+0.1% vs last month", "unit": "ppm"},
            "Temp Anomaly": {"val": 2.4, "sub": "Critical Warm", "unit": "°C"},
            "AQI": {"val": 165, "sub": "Unhealthy", "unit": ""},
            "CH₄": {"val": 1850.2, "sub": "biomass burn", "unit": "ppb"},
            "NO₂": {"val": 120.4, "sub": "agricultural", "unit": "ppb"},
            "Humidity": {"val": 42, "sub": "Dry Season", "unit": "%"}
        },
        "map_center": [18.7883, 98.9853],
        "line_trend": [180, 320, 510, 780, 990, 1210],
        "stack_data": {'PM2.5': [20, 30, 80], 'PM10': [30, 40, 50], 'NO₂': [70, 20, 10], 'SO₂': [85, 10, 5], 'O₃':
