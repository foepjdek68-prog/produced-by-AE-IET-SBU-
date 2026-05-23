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

# ล็อกการแสดงผลให้อยู่ในหน้าจอเดียว (No-Scroll 100%) พร้อมซ่อนปุ่มระบบคลาวด์
st.markdown("""
    <style>
    .block-container {
        padding-top: 0.4rem !important;
        padding-bottom: 0px !important;
        padding-left: 1.2rem !important;
        padding-right: 1.2rem !important;
        height: 100vh;
        overflow: hidden;
    }
    
    .stApp {
        background-color: #020617;
    }
    
    /* สไตล์กล่อง Dropdown */
    div[data-baseweb="select"] {
        background-color: #1e293b !important;
        border-radius: 6px !important;
        border: 1px solid #334155 !important;
    }
    div[data-baseweb="select"] input {
        caret-color: transparent !important;
        pointer-events: none !important;
    }
    
    /* สไตล์กล่อง Metric Cards ให้บางและกะทัดรัด */
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
        font-size: 16px !important;
        font-weight: 700 !important;
        color: #22d3ee !important;
    }
    
    /* สไตล์ตารางข้อมูลรายภาคให้คอมแพคที่สุด */
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
        padding: 5px 6px;
        font-weight: 600;
        border-bottom: 1px solid #334155;
    }
    .compact-table td {
        padding: 5px 6px;
        border-bottom: 1px solid #1e293b;
    }
    .compact-table tr:hover {
        background-color: #1e293b;
    }
    
    /* ดักซ่อนส่วนเกินและปุ่ม Manage app ของระบบคลาวด์ */
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
# 2. DATA BRIDGE SYSTEM (ดึงค่าสารมลพิษครบถ้วนทุกมิติ)
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
        # ระบบสำรองข้อมูลจำลองกรณีเชื่อมต่อ FastAPI สแตนด์บาย
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
                    "temp": 26 + (h % 6),
                    "pm25": 20 + (h * 0.5),
                    "humidity": 60 + (h % 5)
                })
        return pd.DataFrame(latest_list), pd.DataFrame(history_list)

df_latest, df_history = fetch_dashboard_data()

REGION_MAP = {"ภาคกลาง": "Central", "ภาคเหนือ": "North", "ภาคใต้": "South", "ภาคอีสาน": "Northeast", "ภาคตะวันออก": "East", "ภาคตะวันตก": "West"}

# เพิ่มดัชนีมลพิษและสิ่งแวดล้อมให้ครบถ้วนทุกตัวตามโครงสร้างระบบ
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
# 3. BRANDING HEADER (แถบส่วนหัวคงที่ สะอาดตา ไม่มีตัวเลือกกวนใจ)
# =====================================================================
col_brand_logo, col_title_text, col_spacer = st.columns([0.35, 1.95, 1.7])

with col_brand_logo:
    st.markdown("""
        <div style='display: flex; align-items: center; height: 42px; justify-content: center;'>
            <img src='https://comci.southeast.ac.th/wp-content/uploads/2023/11/logo_comsci_re-1.png' 
                 style='height: 38px; width: auto; object-fit: contain;'
                 onerror="this.src='https://www.southeast.ac.th/wp-content/uploads/2023/11/logo-main2.png'">
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

st.markdown("<div style='margin-bottom: 2px;'></div>", unsafe_allow_html=True)

# =====================================================================
# 4. EXECUTIVE SUMMARY STRIPS (แสดงค่าสรุปคงที่แบบเรียลไทม์)
# =====================================================================
# ตั้งต้นเลือกพื้นที่หลักจากภาพเพื่อดึงโปรไฟล์ภูมิภาคขึ้นมาสแตนด์บาย
selected_region = "Central" 
region_data = df_latest[df_latest['region'] == selected_region].iloc[0]

m1, m2, m3, m4, m5, m6 = st.columns(6)
m1.metric(label="คาร์บอนไดออกไซด์ (CO₂)", value=f"{int(region_data['co2'])} ppm")
m2.metric(label="ก๊าซมีเทน (CH₄)", value=f"{int(region_data['ch4'])} ppb")
m3.metric(label="ไนโตรเจนไดออกไซด์ (NO₂)", value=f"{region_data['no2']:.1f} ppb")
m4.metric(label="อุณหภูมิอากาศ", value=f"{region_data['temp']:.1f} °C")
m5.metric(label="ฝุ่น PM 2.5", value=f"{region_data['pm25']:.1f} µg/m³")
m6.metric(label="ความชื้นในอากาศ", value=f"{int(region_data['humidity'])} %")

st.markdown("<div style='margin-bottom: 4px;'></div>", unsafe_allow_html=True)

# =====================================================================
# 5. CONTROL WORKSPACE (ย้ายกล่องเลือกมลพิษและพื้นที่ลงมารวมกลุ่มที่นี่)
# =====================================================================
with st.container(border=True):
    ctrl_col1, ctrl_col2, ctrl_col_text = st.columns([1.2, 1.2, 2.0])
    with ctrl_col1:
        selected_metric_th = st.selectbox("🎯 เลือกสารมลพิษ/ตัวชี้วัดข้อมูล", list(METRIC_MAP.keys()), index=0)
        selected_metric = METRIC_MAP[selected_metric_th]
    with ctrl_col2:
        selected_region_th = st.selectbox("📍 เลือกภูมิภาควิเคราะห์แนวโน้ม", list(REGION_MAP.keys()), index=0)
        selected_region = REGION_MAP[selected_region_th]
    with ctrl_col_text:
        st.markdown(f"""
            <div style='padding-top: 18px; font-size: 11.5px; color: #94a3b8; line-height: 1.4;'>
                💡 <b>ศูนย์ควบคุมการวิเคราะห์ร่วม:</b> ตารางเปรียบเทียบเชิงพื้นที่และกราฟเส้นแสดงแนวโน้มด้านล่าง 
                จะแปรผันตามสารมลพิษ <b>{selected_metric_th}</b> และภูมิภาคที่เลือกพร้อมกันโดยอัตโนมัติ
            </div>
        """, unsafe_allow_html=True)

# =====================================================================
# 6. MAIN ANALYTICS DISPLAY LAYER (3-COLUMN LAYOUT)
# =====================================================================
col_map, col_rank, col_trend = st.columns([1.1, 0.9, 1.0])

# --- คอลัมน์ 1: แผนที่แสดงจุดตรวจวัดเชิงพื้นที่ ---
with col_map:
    with st.container(border=True):
        st.markdown("<div style='font-size: 11px; font-weight: 600; color: #f8fafc; border-left: 3px solid #22d3ee; padding-left: 6px; margin-bottom: 8px;'>แผนที่แสดงจุดตรวจวัดเชิงพื้นที่</div>", unsafe_allow_html=True)
        
        df_latest['radius'] = (df_latest[selected_metric] / df_latest[selected_metric].max()) * 20000 + 12000
        view_state = pdk.ViewState(latitude=13.4, longitude=100.6, zoom=4.6, pitch=0)
        
        layer = pdk.Layer(
            "ScatterplotLayer",
            df_latest,
            get_position="[lon, lat]",
            get_color="[239, 68, 68, 190]" if "co2" in selected_metric or "pm25" in selected_metric else "[34, 211, 238, 190]",
            get_radius="radius",
            pickable=True
        )
        
        st.pydeck_chart(pdk.Deck(
            map_style="https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json",
            initial_view_state=view_state,
            layers=[layer],
            height=165
        ), use_container_width=True)

# --- คอลัมน์ 2: ตารางเปรียบเทียบข้อมูลรายภาค (ทำงานร่วมกับ Dropdown มลพิษ) ---
with col_rank:
    with st.container(border=True):
        st.markdown(f"<div style='font-size: 11px; font-weight: 600; color: #f8fafc; border-left: 3px solid #22d3ee; padding-left: 6px; margin-bottom: 8px;'>เปรียบเทียบรายภูมิภาค ({UNIT_MAP[selected_metric]})</div>", unsafe_allow_html=True)
        
        df_rank = df_latest.sort_values(by=selected_metric, ascending=False)
        
        table_html = f"<table class='compact-table'><tr><th>ภูมิภาค</th><th>ค่าตรวจวัด</th></tr>"
        for _, row in df_rank.iterrows():
            # ไฮไลต์บรรทัดภูมิภาคที่ผู้ใช้กำลังเลือกดูแนวโน้มเพื่อให้สังเกตง่ายขึ้น
            bg_style = "style='background-color: #1e293b; font-weight: bold; color: #22d3ee;'" if row['region'] == selected_region else ""
            table_html += f"<tr {bg_style}><td>{row['th_name']}</td><td>{row[selected_metric]:.1f}</td></tr>"
        table_html += "</table>"
        
        st.markdown(table_html, unsafe_allow_html=True)
        st.markdown("<div style='margin-bottom: 3px;'></div>", unsafe_allow_html=True)

# --- คอลัมน์ 3: กราฟเส้นแสดงแนวโน้มย้อนหลัง 24 ชั่วโมง (ทำงานร่วมกันแบบ Dynamic) ---
with col_trend:
    with st.container(border=True):
        st.markdown(f"<div style='font-size: 11px; font-weight: 600; color: #f8fafc; border-left: 3px solid #38bdf8; padding-left: 6px; margin-bottom: 8px;'>แนวโน้มสถานการณ์ {selected_region_th} (24 ชม.)</div>", unsafe_allow_html=True)
        
        df_region_history = df_history[df_history['region'] == selected_region].sort_values('timestamp')
        
        fig = px.area(df_region_history, x='timestamp', y=selected_metric, height=165)
        fig.update_layout(
            margin=dict(l=10, r=10, t=5, b=15),
            paper_bgcolor='rgba(0,0,0,0)', 
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color="#64748b", size=9),
            xaxis=dict(showgrid=False, nticks=4, tickformat="%H:%M", title=None),
            yaxis=dict(showgrid=True, gridcolor="rgba(51,65,85,0.15)", title=None)
        )
        fig.update_traces(
            line_color='#38bdf8', 
            fillcolor='rgba(56, 189, 248, 0.04)',
            line_width=1.5
        )
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
