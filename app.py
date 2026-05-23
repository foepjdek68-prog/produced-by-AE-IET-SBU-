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

# ปรับรื้อระบบ Layout ใหม่เพื่อความยืดหยุ่น ป้องกันเนื้อหาตกขอบหรือโดนขอบหน้าจอตัดขาด
st.markdown("""
    <style>
    /* ปรับแต่ง Container หลักให้ยืดหยุ่นและสกรอลล์ได้อย่างเป็นธรรมชาติ */
    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 3.5rem !important; /* เว้นพื้นที่ด้านล่างสุดไม่ให้ทับ Footer */
        padding-left: 2rem !important;
        padding-right: 2rem !important;
    }
    
    /* โทนสีพื้นหลังหลักสอดคล้องกับ GitHub config.toml ของคุณ */
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
    
    /* บล็อกแสดงตัวเลขชี้วัดระดับผู้บริหาร (Metric Cards) */
    div[data-testid="stMetric"] {
        background: linear-gradient(135deg, #1e293b 0%, #020617 100%);
        padding: 10px 16px !important;
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
        font-size: 22px !important;
        font-weight: 700 !important;
        color: #22d3ee !important; /* สีฟ้า Primary สว่างชัดเจนตามแบบ config */
    }
    
    /* กรอบหน้าต่างควบคุมเนื้อหาหลัก (Content Cards) */
    .content-card {
        background-color: #1e293b;
        padding: 16px;
        border-radius: 8px;
        border: 1px solid #334155;
        margin-bottom: 1rem;
    }
    .card-title {
        font-size: 13px;
        font-weight: 600;
        color: #f8fafc;
        margin-bottom: 14px;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        border-left: 3px solid #22d3ee;
        padding-left: 8px;
    }
    
    /* ปรับแต่งสไตล์หัวตารางและเนื้อหาภายใน Streamlit Dataframe */
    div[data-testid="stDataFrame"] {
        border: 1px solid #334155 !important;
        border-radius: 4px;
    }
    
    /* ซ่อนโครงสร้างแถบเครื่องมือดั้งเดิมของระบบ */
    footer {visibility: hidden;}
    header {visibility: hidden;}
    div[data-testid="stToolbar"] {visibility: hidden !important;}
    
    /* เครดิตองค์กรวางตัวแบบเป็นทางการที่มุมขวาล่าง */
    .corporate-footer {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        display: flex;
        justify-content: flex-end;
        align-items: center;
        gap: 12px;
        z-index: 999;
        background: rgba(2, 6, 23, 0.9);
        padding: 8px 2rem;
        border-top: 1px solid #334155;
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
# 2. DATA BRIDGE SYSTEM (FastAPI Pipeline Ready)
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
        # กลไกสำรองกรณี Backend Server ยังไม่ได้เปิด (Mock ค่าดึงตามผังข้อมูล Air4Thai + TMD + Satellite)
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
METRIC_MAP = {"คาร์บอนไดออกไซด์ (CO₂)": "co2", "มีเทน (CH₄)": "ch4", "ไนโตรเจนไดออกไซด์ (NO₂)": "no2", "อุณหภูมิพื้นผิว (TEMP)": "temp"}
UNIT_MAP = {"co2": "ppm", "ch4": "ppb", "no2": "ppb", "temp": "°C"}

# =====================================================================
# 3. INTERACTION CONTROL PANEL (TOP BAR)
# =====================================================================
col_title, col_ctrl1, col_ctrl2 = st.columns([2.2, 0.9, 0.9])

with col_title:
    st.markdown("""
        <div style='padding-top: 4px;'>
            <h1 style='color:#f8fafc; font-size:24px; font-weight:700; margin-bottom:0px;'>GHGs Emission Tracking & Climate Analytics</h1>
            <p style='color:#64748b; font-size:12px; margin:0;'>National Environmental Monitoring Platform • Live Data Sync Enabled</p>
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
# 4. EXECUTIVE SUMMARY STRIPS (ROW 1)
# =====================================================================
region_data = df_latest[df_latest['region'] == selected_region].iloc[0]

m1, m2, m3, m4, m5, m6 = st.columns(6)
m1.metric(label="CO₂ Emission", value=f"{int(region_data['co2'])} ppm")
m2.metric(label="CH₄ Level", value=f"{int(region_data['ch4'])} ppb")
m3.metric(label="NO₂ Concentration", value=f"{region_data['no2']:.1f} ppb")
m4.metric(label="Ambient Temp", value=f"{region_data['temp']:.1f} °C")
m5.metric(label="PM 2.5 (TMD API)", value=f"{region_data['pm25']:.1f} µg/m³")
m6.metric(label="Humidity (TMD API)", value=f"{int(region_data['humidity'])} %")

st.markdown("<div style='margin-bottom: 15px;'></div>", unsafe_allow_html=True)

# =====================================================================
# 5. MAIN ANALYTICS WORKSPACE (3-COLUMN ANALYTICS SUITE)
# =====================================================================
col_map, col_rank, col_trend = st.columns([1.2, 0.9, 1.2])

# --- คอลัมน์ 1: Geospatial Mapping (PyDeck ขนาดพอดีคาร์ด) ---
with col_map:
    st.markdown("<div class='content-card'>", unsafe_allow_html=True)
    st.markdown("<div class='card-title'>Station Network & Geospatial Mapping</div>", unsafe_allow_html=True)
    
    df_latest['radius'] = (df_latest[selected_metric] / df_latest[selected_metric].max()) * 30000 + 15000
    view_state = pdk.ViewState(latitude=13.5, longitude=100.8, zoom=5.2, pitch=10)
    
    layer = pdk.Layer(
        "ScatterplotLayer",
        df_latest,
        get_position="[lon, lat]",
        get_color="[34, 211, 238, 180]" if selected_metric == "co2" else "[34, 197, 94, 180]",
        get_radius="radius",
        pickable=True
    )
    
    # กำหนดความสูงแผนที่ไว้ที่ 360px เพื่อให้บรรจุในกรอบ Content Card ได้อย่างพอดี ไม่ทะลุออกไปด้านล่าง
    st.pydeck_chart(pdk.Deck(
        map_style="https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json",
        initial_view_state=view_state,
        layers=[layer],
        height=360
    ), use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# --- คอลัมน์ 2: ตารางเปรียบเทียบค่าวิเคราะห์ (จำกัดความสูง Dataframe) ---
with col_rank:
    st.markdown("<div class='content-card'>", unsafe_allow_html=True)
    st.markdown("<div class='card-title'>ตารางเปรียบเทียบค่าวิเคราะห์รายภูมิภาค</div>", unsafe_allow_html=True)
    
    df_rank = df_latest.sort_values(by=selected_metric, ascending=False).copy()
    df_display = df_rank[['th_name', selected_metric]].rename(
        columns={'th_name': 'ภูมิภาค', selected_metric: f'ค่าวิเคราะห์ ({UNIT_MAP[selected_metric]})'}
    )
    
    # ปรับความสูงตารางเหลือ 360px เพื่อให้แมตช์พอดีกับแผนที่และเห็นครบทุกภูมิภาคโดยมี Scrollbar ในตารางเอง
    st.dataframe(df_display, hide_index=True, use_container_width=True, height=360)
    st.markdown("</div>", unsafe_allow_html=True)

# --- คอลัมน์ 3: Time-Series Trend Analysis (กำหนดความสูงตัวกราฟพอดีคาร์ด) ---
with col_trend:
    st.markdown("<div class='content-card'>", unsafe_allow_html=True)
    st.markdown("<div class='card-title'>Trend Analysis (TimescaleDB 24h Data Logs)</div>", unsafe_allow_html=True)
    
    df_region_history = df_history[df_history['region'] == selected_region].sort_values('timestamp')
    
    # ปรับความสูงกราฟ Plotly เป็น 350px เพื่อให้สเกลตัวเลขด้านล่างไม่ตกขอบการ์ด
    fig = px.area(df_region_history, x='timestamp', y=selected_metric, height=350)
    
    fig.update_layout(
        margin=dict(l=15, r=15, t=10, b=30), # เพิ่มพื้นที่ขอบล่าง (b=30) เพื่อให้เห็นแกนเวลาชัดเจน
        paper_bgcolor='rgba(0,0,0,0)', 
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color="#64748b", size=10),
        xaxis=dict(showgrid=False, nticks=5, tickformat="%H:%M", title=None),
        yaxis=dict(showgrid=True, gridcolor="rgba(51,65,85,0.3)", title=None)
    )
    fig.update_traces(
        line_color='#22d3ee', 
        fillcolor='rgba(34, 211, 238, 0.06)',
        line_width=2
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# =====================================================================
# 6. INSTITUTION CREDITS & FOOTER BAR
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
