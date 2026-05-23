import streamlit as st
import pandas as pd
import plotly.express as px
import pydeck as pdk
import requests

# =====================================================================
# 1. PAGE CONFIGURATION & ENTERPRISE THEME (CSS)
# =====================================================================
st.set_page_config(
    page_title="ระบบวิเคราะห์ข้อมูลสภาพภูมิอากาศและก๊าซเรือนกระจก",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
    <style>
    .block-container {
        padding-top: 0.5rem !important;
        padding-bottom: 1.0rem !important;
        padding-left: 1.5rem !important;
        padding-right: 1.5rem !important;
    }
    
    .stApp {
        background-color: #020617;
    }
    
    div[data-baseweb="select"] {
        background-color: #1e293b !important;
        border-radius: 6px !important;
        border: 1px solid #334155 !important;
    }
    div[data-baseweb="select"] input {
        caret-color: transparent !important;
        pointer-events: none !important;
    }
    
    div[data-testid="stMetric"] {
        background: linear-gradient(135deg, #1e293b 0%, #020617 100%);
        padding: 4px 10px !important;
        border-radius: 6px;
        border: 1px solid #334155;
    }
    div[data-testid="stMetricLabel"] {
        color: #94a3b8 !important;
        font-size: 11px !important;
        font-weight: 600 !important;
    }
    div[data-testid="stMetricValue"] {
        font-size: 17px !important;
        font-weight: 700 !important;
        color: #22d3ee !important;
    }
    
    .compact-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 11.5px;
        color: #e2e8f0;
    }
    .compact-table th {
        background-color: #0f172a;
        color: #94a3b8;
        text-align: left;
        padding: 6px 8px;
        font-weight: 600;
        border-bottom: 1px solid #334155;
    }
    .compact-table td {
        padding: 6px 8px;
        border-bottom: 1px solid #1e293b;
    }
    .compact-table tr:hover {
        background-color: #1e293b;
    }
    
    footer {visibility: hidden; display: none !important;}
    header {visibility: hidden; display: none !important;}
    div[data-testid="stToolbar"] {visibility: hidden !important;}
    div[data-testid="stConnectionStatus"] {display: none !important;}
    .stDeployButton {display: none !important;}
    iframe[title="Manage app"] {display: none !important;}
    button[title="View source code"] {display: none !important;}
    </style>
    """, unsafe_allow_html=True)

# =====================================================================
# 2. DATA BRIDGE SYSTEM
# =====================================================================
BACKEND_API_URL = "http://localhost:8000/api/v1/ghg-metrics"

@st.cache_data(ttl=300)
def fetch_dashboard_data():
    try:
        response = requests.get(BACKEND_API_URL, timeout=1.5)
        if response.status_code == 200:
            data = response.json()
            return pd.DataFrame(data['latest']), pd.DataFrame(data['history'])
    except Exception:
        regions = ["North", "Central", "South", "Northeast", "East", "West"]
        coords = {
            "North": [18.78, 98.98], "Central": [13.75, 100.50], "South": [7.88, 98.39],
            "Northeast": [14.97, 102.10], "East": [12.92, 100.88], "West": [13.52, 99.81]
        }
        
        latest_list = []
        for r in regions:
            latest_list.append({
                "region": r, 
                "th_name": {"North":"ภาคเหนือ", "Central":"ภาคกลาง", "South":"ภาคใต้", "Northeast":"ภาคอีสาน", "East":"ภาคตะตะวันออก", "West":"ภาคตะวันตก"}[r],
                "lat": coords[r][0], "lon": coords[r][1],
                "co2": 433 if r == "Central" else 412,
                "ch4": 1865 if r == "Central" else 1810,
                "no2": 42.1 if r == "Central" else 12.4,
                "temp": 33.2 if r == "Central" else 29.0,
                "pm25": 22.4 if r == "Central" else 35.0, 
                "humidity": 64.0
            })
        
        history_list = []
        months = ["มิ.ย.", "ก.ค.", "ส.ค.", "ก.ย.", "ต.ค.", "พ.ย.", "ธ.ค.", "ม.ค.", "ก.พ.", "มี.ค.", "เม.ย.", "พ.ค."]
        for r in regions:
            for idx, m in enumerate(months):
                history_list.append({
                    "month": m,
                    "region": r,
                    "co2": 415 + (idx * 2.1) + (14 if r == "Central" else 1),
                    "ch4": 1800 + (idx * 7.5) + (50 if r == "Central" else 4),
                    "no2": 20 + (idx * 1.5) + (15 if r == "Central" else 2),
                    "temp": 28 + (idx % 4),
                    "pm25": 15 + (idx * 4.5 if idx > 6 else idx * 0.8),
                    "humidity": 78 - (idx * 1.8)
                })
        return pd.DataFrame(latest_list), pd.DataFrame(history_list)

df_latest, df_history = fetch_dashboard_data()

REGION_MAP = {"ภาคกลาง": "Central", "ภาคเหนือ": "North", "ภาคใต้": "South", "ภาคอีสาน": "Northeast", "ภาคตะวันออก": "East", "ภาคตะวันตก": "West"}
METRIC_MAP = {
    "คาร์บอนไดออกไซด์ (CO₂)": "co2", 
    "ก๊าซมีเทน (CH₄)": "ch4", 
    "ไนโตรเจนไดออกไซด์ (NO₂)": "no2", 
    "อุณหภูมิอากาศ (TEMP)": "temp",
    "ฝุ่น PM 2.5": "pm25",
    "ความชื้นในอากาศ (HUMIDITY)": "humidity"
}
UNIT_MAP = {"co2": "ppm", "ch4": "ppb", "no2": "ppb", "temp": "°C", "pm25": "µg/m³", "humidity": "%"}

# =====================================================================
# 3. BRANDING HEADER & TOP CONTROL BAR
# =====================================================================
col_brand_logo, col_title_text, col_ctrl1, col_ctrl2 = st.columns([0.35, 1.95, 0.85, 0.85])

with col_brand_logo:
    st.markdown("""
        <div style='display: flex; align-items: center; height: 4
