import streamlit as st
import pandas as pd
import plotly.express as px
import pydeck as pdk
import sqlite3
import os

# ตั้งค่าหน้าจอ
st.set_page_config(page_title="Tracking GHGs Emission", layout="wide", initial_sidebar_state="collapsed")

# --- CSS & Credit ---
st.markdown("""
    <style>
    .block-container { padding: 1rem 2rem !important; }
    [data-testid="stMetricValue"] { font-size: 24px !important; color: #2dd4bf !important; }
    .credit { position: fixed; bottom: 10px; right: 20px; color: #64748b; font-size: 10px; z-index: 1000; }
    .main-title { font-size: 24px; font-weight: bold; }
    </style>
    <div class="credit">produced by AE-IET [SBU]</div>
    """, unsafe_allow_html=True)

# ฟังก์ชันเชื่อมต่อฐานข้อมูล
def get_db_connection():
    # หาไฟล์ในโฟลเดอร์ data
    db_path = os.path.join(os.path.dirname(__file__), 'data', 'ghg_data.db')
    if os.path.exists(db_path):
        return sqlite3.connect(db_path)
    return None

# ข้อมูลตั้งค่า
REGION_MAP = {"ภาคเหนือ": "North", "ภาคกลาง": "Central", "ภาคใต้": "South", "ภาคอีสาน": "Northeast", "ภาคตะวันออก": "East", "ภาคตะวันตก": "West"}
METRIC_MAP = {"คาร์บอนไดออกไซด์ (CO₂)": "co2", "มีเทน (CH₄)": "ch4", "ไนโตรเจน (NO₂)": "no2", "อุณหภูมิ (Temp)": "temp"}
COORDS = {"North": [18.78, 98.98], "Central": [13.75, 100.50], "South": [7.88, 98.39], "Northeast": [14.97, 102.10], "East": [12.92, 100.88], "West": [13.52, 99.81]}

# Header
col1, col2, col3, col4 = st.columns([0.6, 2, 1, 1])
with col1:
    st.image("https://upload.wikimedia.org/wikipedia/th/thumb/a/a2/Southeast_Bangkok_University_Logo.png/200px-Southeast_Bangkok_University_Logo.png", width=70)
with col2:
    st.markdown('<p class="main-title">Dashboard “Tracking GHGs Emission”</p>', unsafe_allow_html=True)
    st.caption("อัปเดตข้อมูล: ทุก ๆ 1 ชั่วโมง")

with col3: s_region = REGION_MAP[st.selectbox("📍 พื้นที่:", list(REGION_MAP.keys()), index=1)]
with col4: 
    s_thai_metric = st.selectbox("📊 ดัชนี:", list(METRIC_MAP.keys()), index=0)
    s_metric = METRIC_MAP[s_thai_metric]

# ดึงข้อมูล
conn = get_db_connection()
if conn:
    try:
        latest = pd.read_sql(f"SELECT * FROM ghg_logs WHERE region='{s_region}' ORDER BY timestamp DESC LIMIT 1", conn).iloc[0]
        history = pd.read_sql(f"SELECT * FROM ghg_logs WHERE region='{s_region}' ORDER BY timestamp DESC LIMIT 15", conn)
        all_data = pd.read_sql("SELECT region, MAX(co2) as co2, MAX(ch4) as ch4, MAX(no2) as no2, MAX(temp) as temp FROM ghg_logs GROUP BY region", conn)
        conn.close()

        st.markdown("---")
        # สรุปตัวเลข
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("CO₂ Level", f"{int(latest['co2'])} ppm")
        m2.metric("Methane (CH₄)", f"{latest['ch4']:.1f} ppb")
        m3.metric("Nitrogen (NO₂)", f"{latest['no2']:.1f} ppb")
        m4.metric("Temperature", f"{int(latest['temp'])}°C")

        # แผนที่และกราฟ
        l, r = st.columns([1.5, 1])
        with l:
            st.markdown("### 🗺️ แผนที่พยากรณ์โครงข่ายสถานี")
            all_data['lat'] = all_data['region'].map(lambda x: COORDS[x][0]); all_data['lon'] = all_data['region'].map(lambda x: COORDS[x][1])
            st.pydeck_chart(pdk.Deck(map_style="mapbox://styles/mapbox/dark-v10", initial_view_state=pdk.ViewState(latitude=13.0, longitude=101.0, zoom=5),
                layers=[pdk.Layer("ScatterplotLayer", all_data, get_position="[lon, lat]", get_color="[45, 212, 191, 180]", get_radius=40000)]))
        with r:
            st.markdown(f"### 📈 แนวโน้ม ทุก ๆ 1 ชั่วโมง")
            fig = px.line(history.sort_values('timestamp'), x='timestamp', y=s_metric, height=200, color_discrete_sequence=['#2dd4bf'])
            fig.update_layout(margin=dict(l=0, r=0, t=5, b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)
            
            st.markdown(f"### 🏆 อันดับ{s_thai_metric.split(' (')[0]}สูงสุด")
            inv_m = {v: k for k, v in REGION_MAP.items()}
            all_data['ภูมิภาค'] = all_data['region'].map(inv_m)
            st.dataframe(all_data[['ภูมิภาค', s_metric]].sort_values(s_metric, ascending=False), hide_index=True, use_container_width=True)
    except: st.info("🔄 กำลังรอข้อมูลจากโครงข่าย... (โปรดรันไฟล์บันทึกข้อมูลก่อน)")
else: st.error("⚠️ ไม่พบฐานข้อมูลในโฟลเดอร์ data/ghg_data.db")