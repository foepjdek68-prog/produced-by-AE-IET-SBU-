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

# จัดโครงสร้าง CSS ใหม่ บีบทุกอย่างให้อยู่ในหน้าเดียวแบบ 100% No-Scroll
st.markdown("""
    <style>
    /* บีบเนื้อหาทั้งหมดไม่ให้หลุดขอบหน้าจอหลัก ป้องกันการเกิด Scrollbar */
    .block-container {
        padding-top: 0.5rem !important;
        padding-bottom: 0px !important;
        padding-left: 1.5rem !important;
        padding-right: 1.5rem !important;
        height: 100vh;
        overflow: hidden;
    }
    
    /* ธีมสีพื้นหลัง (#020617 ตามที่ตั้งค่าใน config.toml) */
    .stApp {
        background-color: #020617;
    }
    
    /* สไตล์ Dropdown ป้องกันผู้ใช้พิมพ์ข้อความแปลกปลอม */
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
    
    /* ปรับแต่งตารางข้อมูล (HTML Table) ให้คอมแพคที่สุด */
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
METRIC_MAP = {
    "คาร์บอนไดออกไซด์ (CO₂)": "co2", 
    "มีเทน (CH₄)": "ch4", 
    "ไนโตรเจนไดออกไซด์ (NO₂)": "no2", 
    "อุณหภูมิอากาศ (TEMP)": "temp"
}
UNIT_MAP = {"co2": "ppm", "ch4": "ppb", "no2": "ppb", "temp": "°C"}

# =====================================================================
# 3. INTERACTION CONTROL PANEL & BRANDING HEADER (TOP BAR)
# =====================================================================
col_brand_logo, col_title_text, col_ctrl1, col_ctrl2 = st.columns([0.35, 1.95, 0.85, 0.85])

with col_brand_logo:
    # โลโก้ ComSci สถาบันเซาธ์อีสท์บางกอก พร้อมระบบสำรองหากรูปพัง
    st.markdown("""
        <div style='display: flex; align-items: center; height: 42px; justify-content: center;'>
            <img src='https://comci.southeast.ac.th/wp-content/uploads/2023/11/logo_comsci_re-1.png' 
                 style='height: 38px; width: auto; object-fit: contain;'
                 onerror="this.src='https://www.southeast.ac.th/wp-content/uploads/2023/11/logo-main2.png'">
        </div>
    """, unsafe_allow_html=True)

with col_title_text:
    # ชูชื่อผู้จัดทำและพัฒนาโปรเจกต์ไว้อย่างชัดเจนด้านบนสุดระดับสายตา
    st.markdown("""
        <div style='padding-top: 2px;'>
            <h1 style='color:#f8fafc; font-size:16px; font-weight:700; margin-bottom:0px; line-height:1.2;'>ระบบวิเคราะห์ข้อมูลก๊าซเรือนกระจกและสภาพภูมิอากาศ</h1>
            <p style='color:#38bdf8; font-size:10px; margin:0; font-weight:500
