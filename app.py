import streamlit as st
import pandas as pd
import plotly.express as px
import pydeck as pdk
import sqlite3
import os

# 1. ตั้งค่าหน้าจอ
st.set_page_config(page_title="Tracking GHGs Emission", layout="wide", initial_sidebar_state="collapsed")

# --- 🎨 CSS: ตกแต่ง UI และใส่ Credit มุมล่างขวา ---
st.markdown("""
    <style>
    html, body, [data-testid="stAppViewContainer"] { max-height: 100vh; overflow: hidden; }
    .block-container { padding: 1rem 2rem !important; }
    header, footer { visibility: hidden; }
    [data-testid="stMetricValue"] { font-size: 24px !important; color: #2dd4bf !important; }
    
    /* สไตล์สำหรับ Credit produced by AE-IET [SBU] */
    .credit { 
        position: fixed; 
        bottom: 10px; 
        right: 20px; 
        color: #64748b; 
        font-size: 10px; 
        font-family: sans-serif;
        z-index: 1000;
    }
    .main-title { font-size: 26px; font-weight: bold; margin-bottom: -5px; }
    </style>
    <div class="credit">produced by AE-IET [SBU]</div>
    """, unsafe_allow_html=True)

# --- 🛠️ ฟังก์ชันเชื่อมต่อฐานข้อมูล ---
def get_db_connection():
    base_dir = os.path.dirname(__file__)
    # ค้นหาไฟล์ในโฟลเดอร์ data
    db_path = os.path.join(base_dir, 'data', 'ghg_data.db')
    if os.path.exists(db_path):
        return sqlite3.connect(db_path)
    return None

# --- ข้อมูลพิกัดและตัวเลือกดัชนี (ใช้ Unicode สำหรับเลขห้อย) ---
COORDS = {"North": [18.78, 98.98], "Central": [13.75, 100.50], "South": [7.88, 98.39], "Northeast": [14.97, 102.10], "East": [12.92, 100.88], "West": [13.52, 99.81]}
REGION_MAP = {"ภาคเหนือ": "North", "ภาคกลาง": "Central", "ภาคใต้": "South", "ภาคอีสาน": "Northeast", "ภาคตะวันออก": "East", "ภาคตะวันตก": "West"}
METRIC_MAP = {"คาร์บอนไดออกไซด์ (CO₂)": "co2", "มีเทน (CH₄)": "ch4", "ไนโตรเจน (NO₂)": "no2", "อุณหภูมิ (Temp)": "temp"}

# --- Header: SBU Logo + Title ---
col_logo, col_title, col_reg, col_met = st.columns([0.6, 2, 1, 1])
with col_logo:
    # เปลี่ยนเป็น Logo SBU ตามรูปที่ส่งมา
    st.image("https://upload.wikimedia.org/wikipedia/th/thumb/a/a2/Southeast_Bangkok_University_Logo.png/200px-Southeast_Bangkok_University_Logo.png", width=70)

with col_title:
    st.markdown('<p class="main-title">Dashboard “Tracking GHGs Emission”</p>', unsafe_allow_html=True)
    st.caption("อัปเดตข้อมูล: ทุก ๆ 1 ชั่วโมง")

with col_reg:
    s_region = REGION_MAP[st.selectbox("📍 เลือกภูมิภาค:", list(REGION_MAP.keys()), index=1)]
with col_met:
    s_thai_metric = st.selectbox("📊 เลือกดัชนี:", list(METRIC_MAP.keys()), index=0)
    s_metric = METRIC_MAP[s_thai_metric]

# --- ส่วนแสดงผล ---
conn = get_db_connection()
if conn:
    try:
        latest = pd.read_sql(f"SELECT * FROM ghg_logs WHERE region='{s_region}' ORDER BY timestamp DESC LIMIT 1", conn).iloc[0]
        history = pd.read_sql(f"SELECT * FROM ghg_logs WHERE region='{s_region}' ORDER BY timestamp DESC LIMIT 15", conn)
        all_data = pd.read_sql("SELECT region, co2, ch4, no2, temp FROM ghg_logs GROUP BY region", conn)
        conn.close()

        st.markdown("---")
        # 1. แถบสรุปตัวเลข (Metric)
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("CO₂ Level", f"{int(latest['co2'])} ppm")
        m2.metric("Methane (CH₄)", f"{latest['ch4']:.1f} ppb")
        m3.metric("Nitrogen (NO₂)", f"{latest['no2']:.1f} ppb")
        m4.metric("Temperature", f"{int(latest['temp'])}°C")

        # 2. แผนที่และกราฟ
        col_l, col_r = st.columns([1.6, 1])
        with col_l:
            st.markdown("### 🗺️ แผนที่พยากรณ์โครงข่ายสถานี")
            all_data['lat'] = all_data['region'].map(lambda x: COORDS[x][0]); all_data['lon'] = all_data['region'].map(lambda x: COORDS[x][1])
            st.pydeck_chart(pdk.Deck(
                map_style="mapbox://styles/mapbox/dark-v10",
                initial_view_state=pdk.ViewState(latitude=13.0, longitude=101.0, zoom=4.5, pitch=40),
                layers=[pdk.Layer("ScatterplotLayer", all_data, get_position="[lon, lat]", get_color="[45, 212, 191, 180]", get_radius=50000)]
            ))

        with col_r:
            clean_name = s_thai_metric.split(" (")[0]
            st.markdown(f"### 📈 แนวโน้ม ทุก ๆ 1 ชั่วโมง")
            history['timestamp'] = pd.to_datetime(history['timestamp'])
            fig = px.line(history.sort_values('timestamp'), x='timestamp', y=s_metric, height=180, color_discrete_sequence=['#2dd4bf'])
            fig.update_layout(margin=dict(l=0, r=0, t=5, b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="#94a3b8")
            st.plotly_chart(fig, use_container_width=True)

            # เปลี่ยนเป็น "อันดับคาร์บอนไดออกไซด์สูงสุด"
            st.markdown(f"### 🏆 อันดับ{clean_name}สูงสุด")
            df_rank = all_data.sort_values(by=s_metric, ascending=False)
            inv_m = {v: k for k, v in REGION_MAP.items()}
            df_rank['ภูมิภาค'] = df_rank['region'].map(inv_m)
            st.dataframe(df_rank[['ภูมิภาค', s_metric]], hide_index=True, use_container_width=True, height=140)
    except:
        st.info("🔄 กำลังดึงข้อมูลจากโครงข่าย...")
else:
    st.error("⚠️ ไม่พบฐานข้อมูล! ตรวจสอบว่ามีไฟล์ data/ghg_data.db ใน GitHub หรือไม่")
