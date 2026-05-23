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

# ปรับ Layout บีบพื้นที่แนวตั้งขั้นสูงสุดเพื่อล็อกให้อยู่ใน 1 หน้าจอเป๊ะ ไม่ต้องเลื่อน
st.markdown("""
    <style>
    /* บีบเนื้อหาทั้งหมดไม่ให้หลุดขอบหน้าจอหลัก */
    .block-container {
        padding-top: 0.4rem !important;
        padding-bottom: 0px !important;
        padding-left: 1.5rem !important;
        padding-right: 1.5rem !important;
        height: 100vh;
        overflow: hidden;
    }
    
    /* ธีมสีพื้นหลังตามไฟล์ config ของคุณ */
    .stApp {
        background-color: #020617;
    }
    
    /* สไตล์ Dropdown ควบคุมทิศทางและล็อกการพิมพ์ */
    div[data-baseweb="select"] {
        background-color: #1e293b !important;
        border-radius: 6px !important;
        border: 1px solid #334155 !important;
    }
    div[data-baseweb="select"] input {
        caret-color: transparent !important;
        pointer-events: none !important;
    }
    
    /* บล็อกแสดงตัวเลขสรุป (Metric Cards) แบบประหยัดพื้นที่ */
    div[data-testid="stMetric"] {
        background: linear-gradient(135deg, #1e293b 0%, #020617 100%);
        padding: 4px 10px !important;
        border-radius: 6px;
        border: 1px solid #334155;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
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
    
    /* กรอบหน้าต่างเนื้อหาหลักควบคุมความสูงแบบปลอดภัยสูงสุด */
    .content-card {
        background-color: #1e293b;
        padding: 10px 12px;
        border-radius: 8px;
        border: 1px solid #334155;
        height: 250px; /* ล็อกความสูงพอดีคำ เพื่อดึงข้อมูลที่จมดีดกลับขึ้นมา */
        overflow: hidden;
    }
    .card-title {
        font-size: 12px;
        font-weight: 600;
        color: #f8fafc;
        margin-bottom: 8px;
        border-left: 3px solid #22d3ee;
        padding-left: 6px;
    }
    
    /* ปรับแต่งตารางแบบเรียบง่าย (st.table) ให้เข้ากับ Dark Mode และคอมแพคกระชับ */
    .styled-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 11px;
        color: #e2e8f0;
    }
    .styled-table th {
        background-color: #0f172a;
        color: #94a3b8;
        text-align: left;
        padding: 5px 8px;
        font-weight: 600;
        border-bottom: 1px solid #334155;
    }
    .styled-table td {
        padding: 5px 8px;
        border-bottom: 1px solid #1e293b;
    }
    .styled-table tr:hover {
        background-color: #334155;
    }
    
    /* ซ่อนแถบเครื่องมือดั้งเดิมทั้งหมด */
    footer {visibility: hidden; display: none !important;}
    header {visibility: hidden; display: none !important;}
    div[data-testid="stToolbar"] {visibility: hidden !important;}
    
    /* คำสั่งสคริปต์ขั้นเด็ดขาดดักซ่อนปุ่มดำ "Manage app" ของระบบคลาวด์ */
    div[data-testid="stConnectionStatus"] {display: none !important;}
    .stDeployButton {display: none !important;}
    iframe[title="Manage app"] {display: none !important;}
    div[class^="viewerBadge_container"] {display: none !important;}
    button[title="View source code"] {display: none !important;}
    </style>
    """, unsafe_allow_html=True)

# =====================================================================
# 2. DATA BRIDGE SYSTEM (FastAPI Ready with Mock Backup)
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
                "th_name": {"North":"ภาคเหนือ", "Central":"ภาคกลาง", "South":"ภาคใต้", "Northeast":"ภาคอีสาน", "East":"ภาคตะวันออก", "West":"ภาคตะวันตก"}[r],
                "lat": coords[r][0], "lon": coords[r][1],
                "co2": 433 if r == "Central" else 412,
                "ch4": 1865 if r == "Central" else 1810,
                "no2": 42.1 if r == "Central" else 12.4,
                "temp": 33.2 if r == "Central" else 29.0,
                "pm25": 22.4 if r == "Central" else 35.0, 
                "humidity": 64.0
            })
        
        history_list = []
        for r in regions:
            for h in range(24):
                history_list.append({
                    "timestamp": pd.Timestamp.now() - pd.Timedelta(hours=h),
                    "region": r,
                    "co2": 410 + (h * 0.8) + (23 if r == "Central" else 2),
                    "ch4": 1810 + (h * 1.6) + (55 if r == "Central" else 0),
                    "no2": 20 + h + (22 if r == "Central" else 0),
                    "temp": 26 + (h % 6)
                })
        return pd.DataFrame(latest_list), pd.DataFrame(history_list)

df_latest, df_history = fetch_dashboard_data()

REGION_MAP = {"ภาคกลาง": "Central", "ภาคเหนือ": "North", "ภาคใต้": "South", "ภาคอีสาน": "Northeast", "ภาคตะวันออก": "East", "ภาคตะวันตก": "West"}
METRIC_MAP = {"คาร์บอนไดออกไซด์ (CO₂)": "co2", "มีเทน (CH₄)": "ch4", "ไนโตรเจนไดออกไซด์ (NO₂)": "no2", "อุณหภูมิอากาศ (TEMP)": "temp"}
UNIT_MAP = {"co2": "ppm", "ch4": "ppb", "no2": "ppb", "temp": "°C"}

# =====================================================================
# 3. INTERACTION CONTROL PANEL & BRANDING HEADER (TOP BAR)
# =====================================================================
# ปรับสัดส่วน Layout แถวบนสุดเพื่อแทรกโลโก้คณะและชื่อผู้จัดทำให้อยู่ระดับสายตาอย่างชัดเจน
col_brand_logo, col_title_text, col_ctrl1, col_ctrl2 = st.columns(
