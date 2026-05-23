import streamlit as st
import pandas as pd
import plotly.express as px
import pydeck as pdk
import requests

# =====================================================================
# 1. PAGE CONFIGURATION & ENTERPRISE THEME (CSS)
# =====================================================================
st.set_page_config(
    page_title="GHGs Emission & Climate Analytics Platform",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS ควบคุมให้แสดงผลจบใน 1 หน้าจอ Desktop ระดับผู้บริหาร
st.markdown("""
    <style>
    /* บีบหน้าจอให้ฟิตพอดี ไม่ให้มี Scrollbar เลื่อนลงล่าง */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 0.5rem !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
        max-height: 100vh;
        overflow: hidden;
    }
    
    /* โทนสีพื้นหลัง Slate Dark ดูสุขุมและเป็นทางการ */
    .stApp {
        background-color: #0f172a;
    }
    
    /* สไตล์ Dropdown ป้องกันผู้ใช้พิมพ์ข้อความลงไป */
    div[data-baseweb="select"] {
        background-color: #1e293b !important;
        border-radius: 6px !important;
    }
    div[data-baseweb="select"] input {
        caret-color: transparent !important;
        pointer-events: none !important;
    }
    
    /* บล็อกสรุปตัวเลข (Metric Cards) */
    div[data-testid="stMetric"] {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        padding: 8px 14px !important;
        border-radius: 8px;
        border: 1px solid #334155;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    div[data-testid="stMetricLabel"] {
        color: #94a3b8 !important;
        font-size: 11px !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    div[data-testid="stMetricValue"] {
        font-size: 20px !important;
        font-weight: 700 !important;
        color: #38bdf8 !important;
    }
    
    /* กล่องหน้าต่างเนื้อหา (Cards) */
    .content-card {
        background-color: #1e293b;
        padding: 15px;
        border-radius: 8px;
        border: 1px solid #334155;
        height: 380px; /* ล็อกความสูงหน้าต่างหลัก */
    }
    .card-title {
        font-size: 13px;
        font-weight: 600;
        color: #f8fafc;
        margin-bottom: 12px;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        border-left: 3px solid #38bdf8;
        padding-left: 8px;
    }
    
    /* ซ่อนแถบเครื่องมือดั้งเดิมของ Streamlit */
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* เครดิตสถาบันมุมล่างขวา */
    .corporate-footer {
        position: fixed;
        bottom: 10px;
        right: 2rem;
        display: flex;
        align-items: center;
        gap: 10px;
        z-index: 999;
        background: rgba(15, 23, 42, 0.85);
        padding: 5px 10px;
        border-radius: 6px;
        border: 1px solid #334155;
    }
    .corporate-footer img {
        height: 22px;
        width: auto;
    }
    .corporate-footer .text-block {
        text-align: right;
    }
    .corporate-footer .title {
        font-size: 9px;
        font-weight: 600;
        color: #e2e8f0;
    }
    .corporate-footer .subtitle {
        font-size: 8px;
        color: #64748b;
    }
    </style>
    """, unsafe_allow_html=True)

# =====================================================================
# 2. DATA ACQUISITION & INTEGRATION (FastAPI Ready)
# =====================================================================
BACKEND_API_URL = "http://localhost:8000/api/v1/ghg-metrics"

@st.cache_data(ttl=300)
def fetch_dashboard_data():
    try:
        response = requests.get(BACKEND_API_URL, timeout=3)
        if response.status_code == 200:
            data = response.json()
            return pd.DataFrame(data['latest']), pd.DataFrame(data['history'])
    except Exception:
        # ระบบจะสลับมาใช้ข้อมูลจำลองกลุ่มนี้อัตโนมัติหากยังไม่ได้เปิด Server Backend
        regions = ["North", "Central", "South", "Northeast", "East", "West"]
        coords = {
            "North": [18.78, 98.98], "Central": [13.75, 100.50], "South": [7.88, 98.39],
            "Northeast": [14.97, 102.10], "East": [12.92, 100.88], "West": [13.52, 99.81]
        }
        
        # 1. จำลองข้อมูลสถานการณ์ล่าสุด (Air4Thai + TMD + Satellite)
        latest_list = []
        for r in regions:
            latest_list.append({
                "region": r, 
                "th_name": {"North":"ภาคเหนือ", "Central":"ภาคกลาง", "South":"ภาคใต้", "Northeast":"ภาคอีสาน", "East":"ภาคตะวันออก", "West":"ภาคตะวันตก"}[r],
                "lat": coords[r][0], "lon": coords[r][1],
                "co2": 415 + (15 if r == "Central" else -5),
                "ch4": 1850 + (100 if r == "Northeast" else 10),
                "no2": 45.2 if r == "Central" else 12.4,
                "temp": 32.5 if r == "Central" else 28.0,
                "pm25": 38.5 if r == "North" else 24.0, 
                "humidity": 68.0
            })
        df_latest = pd.DataFrame(latest_list)
        
        # 2. จำลองข้อมูลล็อคประวัติ 24 ชั่วโมง (TimescaleDB)
        history_list = []
        for r in regions:
            for h in range(24):
                history_list.append({
                    "timestamp": pd.Timestamp.now() - pd.Timedelta(hours=h),
                    "region": r,
                    "co2": 405 + (h * 0.5) + (15 if r == "Central" else 2),
                    "ch4": 1820 + (h * 1.5),
                    "no2": 25 + h,
                    "temp": 26 + (h % 6)
                })
        return df_latest, pd.DataFrame(history_list)

df_latest, df_history = fetch_dashboard_data()

REGION_MAP = {"ภาคกลาง": "Central", "ภาคเหนือ": "North", "ภาคใต้": "South", "ภาคอีสาน": "Northeast", "ภาคตะวันออก": "East", "ภาคตะวันตก": "West"}
METRIC_MAP = {"คาร์บอนไดออกไซด์ (CO₂)": "co2", "มีเทน (CH₄)": "ch4", "ไนโตรเจนไดออกไซด์ (NO₂)": "no2", "อุณหภูมิพื้นผิว (TEMP)": "temp"}
UNIT_MAP = {"co2": "ppm", "ch4": "ppb", "no2": "ppb", "temp": "°C"}

# =====================================================================
# 3. HEADER SECTION (CONTROL PANEL)
# =====================================================================
col_title, col_ctrl1, col_ctrl2 = st.columns([2.2, 0.9, 0.9])

with col_title:
    st.markdown("""
        <div style='padding-top: 2px;'>
            <h1 style='color:#f8fafc; font-size:22px; font-weight:700; margin-bottom:0px;'>GHGs Emission Tracking & Climate Analytics</h1>
            <p style='color:#64748b; font-size:11px; margin:0;'>National Environmental Monitoring Platform • Live Data Sync Enabled</p>
        </div>
    """, unsafe_allow_html=True)

with col_ctrl1:
    selected_region_th = st.selectbox("ภูมิภาคเป้าหมาย (Region)", list(REGION_MAP.keys()), index=0)
    selected_region = REGION_MAP[selected_region_th]

with col_ctrl2:
    selected_metric_th = st.selectbox("ตัวชี้วัดหลัก (Main Metric)", list(METRIC_MAP.keys()), index=0)
    selected_metric = METRIC_MAP[selected_metric_th]

st.markdown("<div style='margin-bottom: 10px;'></div>", unsafe_allow_html=True)

# =====================================================================
# 4. EXECUTIVE SUMMARY METRICS (TOP ROW)
# =====================================================================
region_data = df_latest[df_latest['region'] == selected_region].iloc[0]

m1, m2, m3, m4, m5, m6 = st.columns(6)
m1.metric(label="CO₂ Emission", value=f"{int(region_data['co2'])} ppm")
m2.metric(label="CH₄ Level", value=f"{int(region_data['ch4'])} ppb")
m3.metric(label="NO₂ Concentration", value=f"{region_data['no2']:.1f} ppb")
m4.metric(label="Ambient Temp", value=f"{region_data['temp']:.1f} °C")
m5.metric(label="PM 2.5 (TMD API)", value=f"{region_data['pm25']:.1f} µg/m³")
m6.metric(label="Humidity (TMD API)", value=f"{int(region_data['humidity'])} %")

st.markdown("<div style='margin-bottom: 10px;'></div>", unsafe_allow_html=True)

# =====================================================================
# 5. MAIN ANALYTICS WORKSPACE (3-COLUMN LAYOUT)
# =====================================================================
col_map, col_rank, col_trend = st.columns([1.1, 0.9, 1.2])

# --- COLUMN 1: MAP VIEW (Carto Dark - No Token Required) ---
with col_map:
    st.markdown(f"<div class='content-card'><div class='card-title'>Station Network & Heatmap</div>", unsafe_allow_html=True)
    
    # คำนวณรัศมีเพื่อทำเป็นจุด Heatmap เน้นสถานการณ์มลพิษ
    df_latest['radius'] = (df_latest[selected_metric] / df_latest[selected_metric].max()) * 40000 + 15000
    
    view_state = pdk.ViewState(latitude=13.2, longitude=101.0, zoom=4.7, pitch=15)
    
    layer = pdk.Layer(
        "ScatterplotLayer",
        df_latest,
        get_position="[lon, lat]",
        get_color="[56, 189, 248, 170]" if selected_metric == "co2" else "[34, 197, 94, 170]",
        get_radius="radius",
        pickable=True
    )
    
    # เปลี่ยนมาใช้สไตล์แผนที่แบบเปิดบริการสาธารณะ ไม่ต้องระบุ Token ใน config.toml อีกต่อไป
    st.pydeck_chart(pdk.Deck(
        map_style="
