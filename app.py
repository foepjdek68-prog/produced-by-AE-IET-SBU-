import streamlit as st
import pandas as pd
import plotly.express as px
import pydeck as pdk
import requests

# =====================================================================
# 1. PAGE CONFIGURATION & ARCHITECTURAL THEME
# =====================================================================
st.set_page_config(
    page_title="ระบบวิเคราะห์ข้อมูลสภาพภูมิอากาศและก๊าซเรือนกระจก",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
    <style>
    .block-container {
        padding-top: 0.6rem !important;
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
        padding: 6px 10px !important;
        border-radius: 6px;
        border: 1px solid #334155;
    }
    div[data-testid="stMetricLabel"] {
        color: #94a3b8 !important;
        font-size: 11px !important;
        font-weight: 600 !important;
    }
    div[data-testid="stMetricValue"] {
        font-size: 16px !important;
        font-weight: 700 !important;
        color: #22d3ee !important;
    }
    
    .compact-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 11px;
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
# 3. BRANDING HEADER & SUMMARY CARDS
# =====================================================================
col_brand_logo, col_title_text, _ = st.columns([0.4, 2.0, 1.6])

with col_brand_logo:
    st.markdown("""
        <div style='display: flex; align-items: center; height: 42px; justify-content: center;'>
            <img src='https://comci.southeast.ac.th/wp-content/uploads/2023/11/logo_comsci_re-1.png' 
                 style='height: 38px; width: auto; object-fit: contain;'>
        </div>
    """, unsafe_allow_html=True)

with col_title_text:
    st.markdown("""
        <div style='padding-top: 2px;'>
            <h1 style='color:#f8fafc; font-size:16px; font-weight:700; margin-bottom:0px; line-height:1.2;'>ระบบวิเคราะห์ข้อมูลก๊าซเรือนกระจกและสภาพภูมิอากาศ</h1>
            <p style='color:#38bdf8; font-size:10px; margin:0; font-weight:500;'>
                คณะวิทยาศาสตร์และคอมพิวเตอร์ [SBU] • พัฒนาโดยทีมวิเคราะห์ข้อมูลวิศวกรรมขั้นสูง AE-IET
            </p>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='margin-bottom: 4px;'></div>", unsafe_allow_html=True)

m1, m2, m3, m4, m5, m6 = st.columns(6)
m1.metric(label="คาร์บอนไดออกไซด์ (CO₂)", value="433 ppm")
m2.metric(label="ก๊าซมีเทน (CH₄)", value="1865 ppb")
m3.metric(label="ไนโตรเจนไดออกไซด์ (NO₂)", value="42.1 ppb")
m4.metric(label="อุณหภูมิอากาศ", value="33.2 °C")
m5.metric(label="ฝุ่น PM 2.5", value="22.4 µg/m³")
m6.metric(label="ความชื้นในอากาศ", value="64 %")

st.markdown("<div style='margin-bottom: 8px;'></div>", unsafe_allow_html=True)

# =====================================================================
# 4. ROW 1 & 2 DYNAMIC EXECUTION CONTROL
# =====================================================================
# ประกาศตัวแปรรับค่าก่อนเรนเดอร์ UI เพื่อความเสถียรของ Data-Binding โดยไม่ใส่ on_change ค้างลูป
if 'metric_select' not in st.session_state:
    st.session_state.metric_select = list(METRIC_MAP.keys())[0]
if 'region_select' not in st.session_state:
    st.session_state.region_select = list(REGION_MAP.keys())[0]

# =====================================================================
# 5. ROW 1: UPPER ANALYTICS GRID (ตาราง และ กราฟเทรนด์ 1 ปี)
# =====================================================================
row1_left, row1_right = st.columns([1.4, 2.6])

current_metric = METRIC_MAP[st.session_state.metric_select]
current_region = REGION_MAP[st.session_state.region_select]

with row1_left:
    with st.container(border=True):
        st.markdown(f"<div style='font-size: 11px; font-weight: 600; color: #f8fafc; border-left: 3px solid #22d3ee; padding-left: 6px; margin-bottom: 6px;'>เปรียบเทียบรายภูมิภาค ({UNIT_MAP[current_metric]})</div>", unsafe_allow_html=True)
        
        df_rank = df_latest.sort_values(by=current_metric, ascending=False)
        
        table_html = f"<table class='compact-table'><tr><th>ภูมิภาค</th><th>ค่าตรวจวัด</th></tr>"
        for _, row in df_rank.iterrows():
            bg_style = "style='background-color: #1e293b; font-weight: bold; color: #22d3ee;'" if row['region'] == current_region else ""
            table_html += f"<tr {bg_style}><td>{row['th_name']}</td><td>{row[current_metric]:.1f}</td></tr>"
        table_html += "</table>"
        
        st.markdown(table_html, unsafe_allow_html=True)

with row1_right:
    with st.container(border=True):
        st.markdown(f"<div style='font-size: 11px; font-weight: 600; color: #f8fafc; border-left: 3px solid #38bdf8; padding-left: 6px; margin-bottom: 6px;'>แนวโน้มสถานการณ์ {st.session_state.region_select} ในรอบ 1 ปี (สถิติรายเดือน)</div>", unsafe_allow_html=True)
        
        df_region_history = df_history[df_history['region'] == current_region]
        
        fig = px.area(df_region_history, x='month', y=current_metric, height=165)
        fig.update_layout(
            margin=dict(l=20, r=20, t=10, b=20),
            paper_bgcolor='rgba(0,0,0,0)', 
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color="#64748b", size=9),
            xaxis=dict(showgrid=False, title=None),
            yaxis=dict(showgrid=True, gridcolor="rgba(51,65,85,0.15)", title=None)
        )
        fig.update_traces(
            line_color='#38bdf8', 
            fillcolor='rgba(56, 189, 248, 0.05)',
            line_width=1.5
        )
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

st.markdown("<div style='margin-bottom: 4px;'></div>", unsafe_allow_html=True)

# =====================================================================
# 6. ROW 2: LOWER CONTROL & INTEGRATED MAP (ยัดแผนที่ลงใต้กล่องควบคุมขวาล่าง)
# =====================================================================
_, row2_right = st.columns([1.5, 2.5])

with row2_right:
    with st.container(border=True):
        st.markdown("<div style='font-size: 11px; font-weight: 600; color: #94a3b8; margin-bottom: 6px;'>แผงควบคุมระบบข้อมูลและแผนที่เชิงพื้นที่</div>", unsafe_allow_html=True)
        
        select_col1, select_col2 = st.columns(2)
        with select_col1:
            st.selectbox("เลือกสารมลพิษ/ตัวชี้วัด", list(METRIC_MAP.keys()), key="metric_select")
        with select_col2:
            st.selectbox("เลือกภูมิภาค", list(REGION_MAP.keys()), key="region_select")
            
        st.markdown("<div style='margin-bottom: 6px;'></div>", unsafe_allow_html=True)
        
        # จัดการ Render แผนที่แบบประหยัดเนื้อที่ไว้ข้างใต้ปุ่มตามสั่ง
        df_latest['radius'] = (df_latest[current_metric] / df_latest[current_metric].max()) * 6000 + 4000
        view_state = pdk.ViewState(latitude=13.6, longitude=101.2, zoom=4.4, pitch=0)
        
        layer = pdk.Layer(
            "ScatterplotLayer",
            df_latest,
            get_position="[lon, lat]",
            get_color="[239, 68, 68, 180]" if "co2" in current_metric or "pm25" in current_metric else "[34, 211, 238, 180]",
            get_radius="radius",
            pickable=True
        )
        
        st.pydeck_chart(pdk.Deck(
            map_style="https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json",
            initial_view_state=view_state,
            layers=[layer],
            height=125
        ), use_container_width=True)
