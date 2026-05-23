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

# จัดโครงสร้าง CSS ใหม่ บีบทุกอย่างให้ฟิตภายใน 1 หน้าจอเบราว์เซอร์แบบ No-Scroll
st.markdown("""
    <style>
    /* บีบพื้นที่หน้าจอหลักให้พอดี 100% ของความสูงหน้าจอแสดงผล */
    .block-container {
        padding-top: 0.8rem !important;
        padding-bottom: 0.2rem !important;
        padding-left: 1.5rem !important;
        padding-right: 1.5rem !important;
        height: 100vh;
        overflow: hidden;
    }
    
    /* สีพื้นหลังหลัก Slate Dark ตาม config.toml ของคุณ */
    .stApp {
        background-color: #020617;
    }
    
    /* ปรับแต่งช่องเลือก Dropdown */
    div[data-baseweb="select"] {
        background-color: #1e293b !important;
        border-radius: 6px !important;
        border: 1px solid #334155 !important;
    }
    div[data-baseweb="select"] input {
        caret-color: transparent !important;
        pointer-events: none !important;
    }
    
    /* บล็อกแสดงตัวเลขสรุป (Metric Cards) */
    div[data-testid="stMetric"] {
        background: linear-gradient(135deg, #1e293b 0%, #020617 100%);
        padding: 6px 12px !important;
        border-radius: 8px;
        border: 1px solid #334155;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    div[data-testid="stMetricLabel"] {
        color: #94a3b8 !important;
        font-size: 12px !important;
        font-weight: 600 !important;
    }
    div[data-testid="stMetricValue"] {
        font-size: 18px !important;
        font-weight: 700 !important;
        color: #22d3ee !important;
    }
    
    /* กล่องหน้าต่างเนื้อหา (Content Cards) คำนวณความสูงแบบยืดหยุ่นตามหน้าจอคนดู */
    .content-card {
        background-color: #1e293b;
        padding: 12px;
        border-radius: 8px;
        border: 1px solid #334155;
        height: 52vh; /* ปรับขนาดให้พอดีสัดส่วนหน้าจอคอมพิวเตอร์พกพาและตั้งโต๊ะ */
        display: flex;
        flex-direction: column;
    }
    .card-title {
        font-size: 13px;
        font-weight: 600;
        color: #f8fafc;
        margin-bottom: 8px;
        border-left: 3px solid #22d3ee;
        padding-left: 8px;
    }
    
    /* ซ่อนโครงสร้างและปุ่มควบคุมของระบบที่ทำให้หน้าจอล้น */
    footer {visibility: hidden;}
    header {visibility: hidden;}
    div[data-testid="stToolbar"] {visibility: hidden !important;}
    
    /* ดักซ่อนแถบระบบ "Manage app" ของ Streamlit Cloud ไม่ให้บังข้อมูลด้านล่าง */
    div[data-testid="stConnectionStatus"] {display: none !important;}
    .stDeployButton {display: none !important;}
    iframe[title="Manage app"] {display: none !important;}
    div.viewerBadge_container__1QS1A {display: none !important;}
    #MainMenu {visibility: hidden;}
    
    /* แถบเครดิตสถาบันแบบเรียบง่าย */
    .corporate-footer {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        display: flex;
        justify-content: flex-end;
        align-items: center;
        gap: 10px;
        z-index: 999;
        background: #020617;
        padding: 4px 1.5rem;
        border-top: 1px solid #334155;
    }
    .corporate-footer img {
        height: 18px;
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
    </style>
    """, unsafe_allow_html=True)

# =====================================================================
# 2. DATA BRIDGE SYSTEM (FastAPI Ready with Mock Backup)
# =====================================================================
BACKEND_API_URL = "http://localhost:8000/api/v1/ghg-metrics"

@st.cache_data(ttl=300)
def fetch_dashboard_data():
    try:
        response = requests.get(BACKEND_API_URL, timeout=2)
        if response.status_code == 200:
            data = response.json()
            return pd.DataFrame(data['latest']), pd.DataFrame(data['history'])
    except Exception:
        # ข้อมูลจำลองภาษาไทยสำหรับคนทั่วไปเข้าใจง่าย
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
# 3. INTERACTION CONTROL PANEL (TOP BAR)
# =====================================================================
col_title, col_ctrl1, col_ctrl2 = st.columns([2.3, 0.85, 0.85])

with col_title:
    st.markdown("""
        <div style='padding-top: 2px;'>
            <h1 style='color:#f8fafc; font-size:20px; font-weight:700; margin-bottom:0px;'>ระบบวิเคราะห์ข้อมูลก๊าซเรือนกระจกและสภาพภูมิอากาศ</h1>
            <p style='color:#64748b; font-size:11px; margin:0;'>แพลตฟอร์มติดตามสถานการณ์สิ่งแวดล้อมแห่งชาติ • ข้อมูลอัปเดตแบบเรียลไทม์</p>
        </div>
    """, unsafe_allow_html=True)

with col_ctrl1:
    selected_region_th = st.selectbox("เลือกภูมิภาค", list(REGION_MAP.keys()), index=0)
    selected_region = REGION_MAP[selected_region_th]

with col_ctrl2:
    selected_metric_th = st.selectbox("เลือกสารมลพิษ/ตัวชี้วัด", list(METRIC_MAP.keys()), index=0)
    selected_metric = METRIC_MAP[selected_metric_th]

st.markdown("<div style='margin-bottom: 5px;'></div>", unsafe_allow_html=True)

# =====================================================================
# 4. EXECUTIVE SUMMARY STRIPS (ROW 1 - ตัวชี้วัดภาษาไทย)
# =====================================================================
region_data = df_latest[df_latest['region'] == selected_region].iloc[0]

m1, m2, m3, m4, m5, m6 = st.columns(6)
m1.metric(label="คาร์บอนไดออกไซด์ (CO₂)", value=f"{int(region_data['co2'])} ppm")
m2.metric(label="ก๊าซมีเทน (CH₄)", value=f"{int(region_data['ch4'])} ppb")
m3.metric(label="ไนโตรเจนไดออกไซด์ (NO₂)", value=f"{region_data['no2']:.1f} ppb")
m4.metric(label="อุณหภูมิอากาศ", value=f"{region_data['temp']:.1f} °C")
m5.metric(label="ฝุ่น PM 2.5", value=f"{region_data['pm25']:.1f} µg/m³")
m6.metric(label="ความชื้นในอากาศ", value=f"{int(region_data['humidity'])} %")

st.markdown("<div style='margin-bottom: 5px;'></div>", unsafe_allow_html=True)

# =====================================================================
# 5. MAIN ANALYTICS WORKSPACE (3-COLUMN LAYOUT)
# =====================================================================
col_map, col_rank, col_trend = st.columns([1.1, 0.85, 1.05])

# --- คอลัมน์ 1: แผนที่แสดงจุดตรวจวัดเชิงพื้นที่ ---
with col_map:
    st.markdown("<div class='content-card'>", unsafe_allow_html=True)
    st.markdown("<div class='card-title'>แผนที่แสดงจุดตรวจวัดและระดับความหนาแน่น</div>", unsafe_allow_html=True)
    
    df_latest['radius'] = (df_latest[selected_metric] / df_latest[selected_metric].max()) * 25000 + 15000
    view_state = pdk.ViewState(latitude=13.6, longitude=100.8, zoom=4.9, pitch=0)
    
    layer = pdk.Layer(
        "ScatterplotLayer",
        df_latest,
        get_position="[lon, lat]",
        get_color="[34, 211, 238, 190]" if selected_metric == "co2" else "[34, 197, 94, 190]",
        get_radius="radius",
        pickable=True
    )
    
    st.pydeck_chart(pdk.Deck(
        map_style="https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json",
        initial_view_state=view_state,
        layers=[layer]
    ), use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# --- คอลัมน์ 2: ตารางเปรียบเทียบข้อมูลรายภาค ---
with col_rank:
    st.markdown("<div class='content-card'>", unsafe_allow_html=True)
    st.markdown("<div class='card-title'>ตารางเปรียบเทียบค่าวิเคราะห์รายภูมิภาค</div>", unsafe_allow_html=True)
    
    df_rank = df_latest.sort_values(by=selected_metric, ascending=False).copy()
    df_display = df_rank[['th_name', selected_metric]].rename(
        columns={'th_name': 'ภูมิภาค', selected_metric: f'ค่าที่ตรวจวัดได้ ({UNIT_MAP[selected_metric]})'}
    )
    
    # ปล่อยให้ตารางคำนวณความสูงตามพื้นที่การ์ดหลักอัตโนมัติ
    st.dataframe(df_display, hide_index=True, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# --- คอลัมน์ 3: กราฟเส้นแสดงแนวโน้มย้อนหลัง 24 ชั่วโมง ---
with col_trend:
    st.markdown("<div class='content-card'>", unsafe_allow_html=True)
    st.markdown("<div class='card-title'>กราฟแสดงแนวโน้มสถานการณ์ย้อนหลัง (24 ชั่วโมง)</div>", unsafe_allow_html=True)
    
    df_region_history = df_history[df_history['region'] == selected_region].sort_values('timestamp')
    
    # ถอดพิกเซลความสูงออก เพื่อให้ Plotly ขยายตัวตามพื้นที่ความสูง vh ของการ์ดครอบแบบอัตโนมัติ
    fig = px.area(df_region_history, x='timestamp', y=selected_metric)
    
    fig.update_layout(
        margin=dict(l=10, r=10, t=5, b=25),
        paper_bgcolor='rgba(0,0,0,0)', 
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color="#64748b", size=10),
        xaxis=dict(showgrid=False, nticks=5, tickformat="%H:%M", title=None),
        yaxis=dict(showgrid=True, gridcolor="rgba(51,65,85,0.25)", title=None),
        autosize=True
    )
    fig.update_traces(
        line_color='#22d3ee', 
        fillcolor='rgba(34, 211, 238, 0.05)',
        line_width=2
    )
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    st.markdown("</div>", unsafe_allow_html=True)

# =====================================================================
# 6. INSTITUTION CREDITS & FOOTER BAR
# =====================================================================
st.markdown(f"""
    <div class="corporate-footer">
        <div class="text-block">
            <span class="title">สถาบันเทคโนโลยีและวิศวกรรมขั้นสูง [SBU] • พัฒนาโดยทีมงานวิเคราะห์ข้อมูล AE-IET</span>
        </div>
        <img src="https://www.southeast.ac.th/wp-content/uploads/2023/11/logo-main2.png" 
             onerror="this.src='https://upload.wikimedia.org/wikipedia/th/thumb/a/a2/Southeast_Bangkok_University_Logo.png/200px-Southeast_Bangkok_University_Logo.png'">
    </div>
""", unsafe_allow_html=True)
