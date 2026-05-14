import streamlit as st
import pandas as pd
import plotly.express as px
import pydeck as pdk
import sqlite3
import os

# 1. ตั้งค่าหน้าจอ (ปรับ Padding ให้กว้างขึ้น)
st.set_page_config(page_title="Tracking GHGs Emission", layout="wide", initial_sidebar_state="collapsed")

# --- 🎨 CSS: แก้ปัญหาตัวหนังสือซ้อนกัน และจัด Layout ---
st.markdown("""
    <style>
    .block-container { padding: 2rem 3rem !important; }
    [data-testid="stMetricValue"] { font-size: 22px !important; color: #2dd4bf !important; }
    [data-testid="stMetricLabel"] { font-size: 14px !important; }
    .credit { position: fixed; bottom: 10px; right: 20px; color: #64748b; font-size: 10px; z-index: 1000; }
    .main-title { font-size: 24px; font-weight: bold; margin-bottom: -5px; }
    /* เพิ่มระยะห่างระหว่างกราฟและตัวเลข */
    .stPlotlyChart { margin-top: 10px; }
    </style>
    <div class="credit">produced by AE-IET [SBU]</div>
    """, unsafe_allow_html=True)

# --- 🛠️ ฟังก์ชันเชื่อมต่อฐานข้อมูล ---
def get_db_connection():
    base_dir = os.path.dirname(__file__)
    db_path = os.path.join(base_dir, 'data', 'ghg_data.db')
    return sqlite3.connect(db_path) if os.path.exists(db_path) else None

# ตัวเลือกดัชนี
METRIC_MAP = {"คาร์บอนไดออกไซด์ (CO₂)": "co2", "มีเทน (CH₄)": "ch4", "ไนโตรเจน (NO₂)": "no2", "อุณหภูมิ (Temp)": "temp"}
REGION_MAP = {"ภาคเหนือ": "North", "ภาคกลาง": "Central", "ภาคใต้": "South", "ภาคอีสาน": "Northeast", "ภาคตะวันออก": "East", "ภาคตะวันตก": "West"}
COORDS = {"North": [18.78, 98.98], "Central": [13.75, 100.50], "South": [7.88, 98.39], "Northeast": [14.97, 102.10], "East": [12.92, 100.88], "West": [13.52, 99.81]}

# --- Header: SBU Logo + Title ---
col_head1, col_head2 = st.columns([3, 1.5])
with col_head1:
    col_l, col_t = st.columns([0.4, 2])
    with col_l:
        st.image("https://upload.wikimedia.org/wikipedia/th/thumb/a/a2/Southeast_Bangkok_University_Logo.png/200px-Southeast_Bangkok_University_Logo.png", width=70)
    with col_t:
        st.markdown('<p class="main-title">Dashboard “Tracking GHGs Emission”</p>', unsafe_allow_html=True)
        st.caption("อัปเดตข้อมูล: ทุก ๆ 1 ชั่วโมง")

with col_head2:
    c1, c2 = st.columns(2)
    with c1: s_region = REGION_MAP[st.selectbox("📍 ภูมิภาค:", list(REGION_MAP.keys()), index=1)]
    with c2: 
        s_thai_metric = st.selectbox("📊 ดัชนี:", list(METRIC_MAP.keys()), index=0)
        s_metric = METRIC_MAP[s_thai_metric]

# --- แสดงผลข้อมูล ---
conn = get_db_connection()
if conn:
    try:
        latest = pd.read_sql(f"SELECT * FROM ghg_logs WHERE region='{s_region}' ORDER BY timestamp DESC LIMIT 1", conn).iloc[0]
        history = pd.read_sql(f"SELECT * FROM ghg_logs WHERE region='{s_region}' ORDER BY timestamp DESC LIMIT 15", conn)
        all_data = pd.read_sql("SELECT region, MAX(co2) as co2, MAX(ch4) as ch4, MAX(no2) as no2, MAX(temp) as temp FROM ghg_logs GROUP BY region", conn)
        conn.close()

        st.markdown("---")
        # 1. แถบสรุปตัวเลข (เพิ่มช่องไฟ)
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("CO₂ Level", f"{int(latest['co2'])} ppm")
        m2.metric("Methane (CH₄)", f"{latest['ch4']:.1f} ppb")
        m3.metric("Nitrogen (NO₂)", f"{latest['no2']:.1f} ppb")
        m4.metric("Temperature", f"{int(latest['temp'])}°C")

        st.write("") # เว้นวรรค

        # 2. แผนที่และกราฟ (ปรับสัดส่วน)
        col_l, col_r = st.columns([1.5, 1])
        with col_l:
            st.markdown("### 🗺️ แผนที่พยากรณ์โครงข่ายสถานี")
            all_data['lat'] = all_data['region'].map(lambda x: COORDS[x][0]); all_data['lon'] = all_data['region'].map(lambda x: COORDS[x][1])
            st.pydeck_chart(pdk.Deck(map_style="mapbox://styles/mapbox/dark-v10", initial_view_state=pdk.ViewState(latitude=13.5, longitude=101.0, zoom=5, pitch=40),
                layers=[pdk.Layer("ScatterplotLayer", all_data, get_position="[lon, lat]", get_color="[45, 212, 191, 180]", get_radius=40000)]))

        with col_r:
            st.markdown(f"### 📈 แนวโน้ม ทุก ๆ 1 ชั่วโมง")
            history['timestamp'] = pd.to_datetime(history['timestamp'])
            fig = px.line(history.sort_values('timestamp'), x='timestamp', y=s_metric, height=220, color_discrete_sequence=['#2dd4bf'])
            fig.update_layout(margin=dict(l=0, r=0, t=10, b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="#94a3b8")
            st.plotly_chart(fig, use_container_width=True)

            st.markdown(f"### 🏆 อันดับ{s_thai_metric.split(' (')[0]}สูงสุด")
            df_rank = all_data.sort_values(by=s_metric, ascending=False)
            inv_m = {v: k for k, v in REGION_MAP.items()}
            df_rank['ภูมิภาค'] = df_rank['region'].map(inv_m)
            st.dataframe(df_rank[['ภูมิภาค', s_metric]], hide_index=True, use_container_width=True, height=180)
    except Exception as e: st.info(f"🔄 กำลังรอข้อมูล... ({e})")
else: st.error("⚠️ ไม่พบฐานข้อมูล")
