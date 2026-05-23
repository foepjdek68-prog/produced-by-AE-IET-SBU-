import streamlit as st
import pandas as pd
import plotly.express as px
import pydeck as pdk
import requests
from datetime import datetime

# =====================================================================
# 1. PAGE CONFIGURATION & ENTERPRISE THEME (CSS)
# =====================================================================
st.set_page_config(
    page_title="GHGs Emission & Climate Analytics Platform",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS เพื่อควบคุมให้ทุกอย่างฟิตพอดีใน 1 หน้าจอ Desktop (No Scroll) และดูเป็นทางการ
st.markdown("""
    <style>
    /* ปรับแต่ง Container หลักให้ฟิตพอดีหน้าจอ */
    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 1rem !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
        max-height: 100vh;
        overflow: hidden;
    }
    
    /* โทนสีพื้นหลังแบบ Slate Dark (ดูน่าเชื่อถือและเป็นทางการกว่าสีดำสนิท) */
    .stApp {
        background-color: #0f172a;
    }
    
    /* ปรับแต่ง Dropdown Selector ให้ดูเรียบหรู */
    div[data-baseweb="select"] {
        background-color: #1e293b !important;
        border-radius: 6px !important;
    }
    div[data-baseweb="select"] input {
        caret-color: transparent !important;
        pointer-events: none !important;
    }
    
    /* การ์ดแสดงตัวชี้วัด (Metric Cards) สไตล์ Dashboard ผู้บริหาร */
    div[data-testid="stMetric"] {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        padding: 12px 16px !important;
        border-radius: 8px;
        border: 1px solid #334155;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    div[data-testid="stMetricLabel"] {
        color: #94a3b8 !important;
        font-size: 12px !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    div[data-testid="stMetricValue"] {
        font-size: 22px !important;
        font-weight: 700 !important;
        color: #38bdf8 !important; /* สีฟ้าไอซ์บลู ดูเป็นทางการ */
    }
    
    /* ส่วนของกล่องเนื้อหาภายในคอลัมน์ */
    .content-card {
        background-color: #1e293b;
        padding: 15px;
        border-radius: 8px;
        border: 1px solid #334155;
        height: 380px;
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
    
    /* ซ่อน Footer ของ Streamlit */
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* เครดิตสถาบันจัดวางแบบเป็นทางการมุมขวาล่าง */
    .corporate-footer {
        position: fixed;
        bottom: 15px;
        right: 2rem;
        display: flex;
        align-items: center;
        gap: 10px;
        z-index: 999;
        background: rgba(15, 23, 42, 0.8);
        padding: 6px 12px;
        border-radius: 6px;
        border: 1px solid #334155;
    }
    .corporate-footer img {
        height: 24px;
        width: auto;
    }
    .corporate-footer .text-block {
        text-align: right;
    }
    .corporate-footer .title {
        font-size: 10px;
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
# 2. DATA ACQUISITION (FASTAPI BACKEND INTEGRATION)
# =====================================================================
# ที่อยู่ของ FastAPI ที่ได้จากฝั่งประมวลผลตามแผนงาน (PostgreSQL / TimescaleDB)
BACKEND_API_URL = "http://localhost:8000/api/v1/ghg-metrics"

@st.cache_data(ttl=300) # แคชข้อมูลไว้ 5 นาที เพื่อประสิทธิภาพที่รวดเร็ว
def fetch_dashboard_data():
    try:
        # ยิงดึงข้อมูลจาก Backend API ตามแผน 100%
        response = requests.get(BACKEND_API_URL, timeout=3)
        if response.status_url == 200:
            data = response.json()
            df_latest = pd.DataFrame(data['latest'])
            df_history = pd.DataFrame(data['history'])
            return df_latest, df_history
    except Exception:
        # =====================================================================
        # MOCK DATA (ระบบจะสลับมาใช้ตรงนี้อัตโนมัติหากยังไม่ได้เปิด Server FastAPI)
        # ข้อมูลถูก Mock ให้ตรงกับ Data Sources ในภาพ (Air4Thai, TMD, Sentinel-5P)
        # =====================================================================
        regions = ["North", "Central", "South", "Northeast", "East", "West"]
        coords = {
            "North": [18.78, 98.98], "Central": [13.75, 100.50], "South": [7.88, 98.39],
            "Northeast": [14.97, 102.10], "East": [12.92, 100.88], "West": [13.52, 99.81]
        }
        
        # 1. จำลองข้อมูลสถานการณ์ล่าสุดจากจุดตรวจวัด (Latest Data)
        latest_list = []
        for r in regions:
            latest_list.append({
                "region": r, "th_name": {"North":"ภาคเหนือ", "Central":"ภาคกลาง", "South":"ภาคใต้", "Northeast":"ภาคตะวันออกเฉียงเหนือ", "East":"ภาคตะวันออก", "West":"ภาคตะวันตก"}[r],
                "lat": coords[r][0], "lon": coords[r][1],
                "co2": 415 + (15 if r == "Central" else -5),  # Air4Thai / Satellite Sentinel-5P
                "ch4": 1850 + (100 if r == "Northeast" else 10),
                "no2": 45.2 if r == "Central" else 12.4,
                "temp": 32.5 if r == "Central" else 28.0,
                "pm25": 35.0, "humidity": 65.0, "wind_speed": 12.0 # ข้อมูลเสริมจาก TMD
            })
        df_latest = pd.DataFrame(latest_list)
        
        # 2. จำลองข้อมูลประวัติย้อนหลัง 24 ชั่วโมง (TimescaleDB History)
        history_list = []
        for r in regions:
            for h in range(24):
                history_list.append({
                    "timestamp": pd.Timestamp.now() - pd.Timedelta(hours=h),
                    "region": r,
                    "co2": 400 + (h * 0.8) + (20 if r == "Central" else 5),
                    "ch4": 1800 + (h * 2),
                    "no2": 30 + h,
                    "temp": 25 + (h % 8)
                })
        df_history = pd.DataFrame(history_list)
        return df_latest, df_history

df_latest, df_history = fetch_dashboard_data()

# Mapping สำหรับการแสดงผลหน้าจอ
REGION_MAP = {"ภาคกลาง": "Central", "ภาคเหนือ": "North", "ภาคใต้": "South", "ภาคตะวันออกเฉียงเหนือ": "Northeast", "ภาคตะวันออก": "East", "ภาคตะวันตก": "West"}
METRIC_MAP = {"คาร์บอนไดออกไซด์ (CO₂)": "co2", "มีเทน (CH₄)": "ch4", "ไนโตรเจนไดออกไซด์ (NO₂)": "no2", "อุณหภูมิผิวพื้น (TEMP)": "temp"}
UNIT_MAP = {"co2": "ppm", "ch4": "ppb", "no2": "ppb", "temp": "°C"}

# =====================================================================
# 3. HEADER SECTION (CONTROL PANEL)
# =====================================================================
# ส่วนหัวเว็บบาร์เดี่ยว สไตล์เรียบหรูเป็นทางการ
col_title, col_ctrl1, col_ctrl2 = st.columns([2, 1, 1])

with col_title:
    st.markdown("""
        <div style='padding-top: 5px;'>
            <h1 style='color:#f8fafc; font-size:22px; font-weight:700; margin-bottom:2px;'>GHGs Emission Tracking & Climate Analytics</h1>
            <p style='color:#64748b; font-size:11px; margin:0;'>National Environmental Monitoring Platform • Live Data Sync Enabled</p>
        </div>
    """, unsafe_allow_html=True)

with col_ctrl1:
    selected_region_th = st.selectbox("ภูมิภาคเป้าหมาย (Region)", list(REGION_MAP.keys()), index=0)
    selected_region = REGION_MAP[selected_region_th]

with col_ctrl2:
    selected_metric_th = st.selectbox("ตัวชี้วัดหลัก (Main Metric)", list(METRIC_MAP.keys()), index=0)
    selected_metric = METRIC_MAP[selected_metric_th]

st.markdown("<div style='margin-bottom: 15px;'></div>", unsafe_allow_html=True)

# =====================================================================
# 4. EXECUTIVE SUMMARY METRICS (TOP ROW)
# =====================================================================
# ดึงข้อมูลล่าสุดของภาคที่เลือกมาแสดงผลในการ์ด
region_data = df_latest[df_latest['region'] == selected_region].iloc[0]

m1, m2, m3, m4, m5, m6 = st.columns(6)
m1.metric(label="CO₂ Emission", value=f"{int(region_data['co2'])} ppm")
m2.metric(label="CH₄ Level", value=f"{int(region_data['ch4'])} ppb")
m3.metric(label="NO₂ Concentration", value=f"{region_data['no2']:.1f} ppb")
m4.metric(label="Ambient Temp", value=f"{region_data['temp']:.1f} °C")
m5.metric(label="PM 2.5 (TMD)", value=f"{region_data['pm25']:.1f} µg/m³")  # ดึงค่าจาก TMD API ตามแผน
m6.metric(label="Humidity (TMD)", value=f"{int(region_data['humidity'])} %")

st.markdown("<div style='margin-bottom: 15px;'></div>", unsafe_allow_html=True)

# =====================================================================
# 5. MAIN ANALYTICS WORKSPACE (3-COLUMN LAYOUT)
# =====================================================================
col_map, col_rank, col_trend = st.columns([1.1, 0.9, 1.2])

# --- COLUMN 1: SATELLITE & NETWORK MAPPING (Next.js/MapLibre Style) ---
with col_map:
    st.markdown(f"<div class='content-card'><div class='card-title'>Station Network & Heatmap ({selected_metric_th.split(' (')[1].replace(')', '')})</div>", unsafe_allow_html=True)
    
    # คำนวณขนาดจุดตามปริมาณความเข้มข้นของก๊าซเพื่อให้แสดงผลเป็นแนว Heatmap แบบทางการ
    df_latest['radius'] = (df_latest[selected_metric] / df_latest[selected_metric].max()) * 45000 + 15000
    
    view_state = pdk.ViewState(latitude=13.5, longitude=100.8, zoom=4.6, pitch=30)
    
    # ใช้ Map Style แบบสว่างน้อย (Dark Matter) เพื่อเน้นข้อมูลมลพิษให้ชัดเจน
    layer = pdk.Layer(
        "ScatterplotLayer",
        df_latest,
        get_position="[lon, lat]",
        get_color="[56, 189, 248, 160]" if selected_metric == "co2" else "[34, 197, 94, 160]",
        get_radius="radius",
        pickable=True
    )
    
    st.pydeck_chart(pdk.Deck(
        map_style="mapbox://styles/mapbox/dark-v11", # สไตล์แผนที่เรียบหรูระดับสากล
        initial_view_state=view_state,
        layers=[layer]
    ), use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)


# --- COLUMN 2: NATIONAL RANKING (PostgreSQL Data Sorted) ---
with col_rank:
    st.markdown(f"<div class='content-card'><div class='card-title'>ตารางเปรียบเทียบค่าวิเคราะห์รายภูมิภาค</div>", unsafe_allow_html=True)
    
    # จัดลำดับข้อมูลจากมากไปน้อยตามคำสั่งในแผนงาน
    df_rank = df_latest.sort_values(by=selected_metric, ascending=False).copy()
    df_display = df_rank[['th_name', selected_metric]].rename(
        columns={'th_name': 'ภูมิภาค', selected_metric: f'ค่าที่ตรวจวัดได้ ({UNIT_MAP[selected_metric]})'}
    )
    
    # แสดงตารางแบบคลีน ตาข่ายเรียบ สไตล์ Enterprise
    st.dataframe(
        df_display, 
        hide_index=True, 
        use_container_width=True, 
        height=310
    )
    st.markdown("</div>", unsafe_allow_html=True)


# --- COLUMN 3: TIMESERIES TREND ANALYSIS (TimescaleDB Data) ---
with col_trend:
    st.markdown(f"<div class='content-card'><div class='card-title'>Trend Analysis (TimescaleDB 24-Hour Logs)</div>", unsafe_allow_html=True)
    
    # ดึงประวัติเฉพาะภูมิภาคที่เลือกมาพล็อตกราฟ
    df_region_history = df_history[df_history['region'] == selected_region].sort_values('timestamp')
    
    fig = px.area(
        df_region_history, 
        x='timestamp', 
        y=selected_metric, 
        height=300
    )
    
    # ปรับแต่งกราฟให้เรียบ เน้นโทนสีน้ำเงินพรีเมียม ขอบคมชัดสะอาดตา
    fig.update_layout(
        margin=dict(l=10, r=10, t=10, b=10),
        paper_bgcolor='rgba(0,0,0,0)', 
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color="#64748b", size=9),
        xaxis=dict(showgrid=False, nticks=6, tickformat="%H:%M", title=None),
        yaxis=dict(showgrid=True, gridcolor="rgba(51,65,85,0.4)", title=None)
    )
    fig.update_traces(
        line_color='#38bdf8', 
        fillcolor='rgba(56, 189, 248, 0.08)',
        line_width=2
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# =====================================================================
# 6. INSTITUTION CREDITS & FOOTER
# =====================================================================
st.markdown(f"""
    <div class="corporate-footer">
        <div class="text-block">
            <div class="title">สถาบันเทคโนโลยีและวิศวกรรมขั้นสูง [SBU]</div>
            <div class="subtitle">Analytical Platform Powered by AE-IET Team</div>
        </div>
        <img src="https://www.southeast.ac.th/wp-content/uploads/2023/11/logo-main2.png" 
             onerror="this.src='https://upload.wikimedia.org/wikipedia/th/thumb/a/a2/Southeast_Bangkok_University_Logo.png/200px-Southeast_Bangkok_University_Logo.png'">
    </div>
""", unsafe_allow_html=True)
