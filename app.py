import streamlit as st
import pandas as pd
import plotly.express as px
import pydeck as pdk
import sqlite3
import os

# 1. ตั้งค่าหน้าจอ (ปรับกว้างพิเศษและปิด Sidebar)
st.set_page_config(page_title="Tracking GHGs Emission", layout="wide", initial_sidebar_state="collapsed")

# --- 🎨 CSS: เน้นความสมดุลและความเล็กลงของวิดเจ็ต ---
st.markdown("""
    <style>
    .block-container { padding: 1.5rem 2.5rem !important; }
    
    /* ปรับขนาด Metric ให้เล็กและพอดีหน้าจอ */
    [data-testid="stMetricValue"] { font-size: 18px !important; color: #2dd4bf !important; }
    [data-testid="stMetricLabel"] { font-size: 12px !important; color: #94a3b8 !important; }
    [data-testid="stMetric"] { background: #1e293b; padding: 10px; border-radius: 8px; }

    /* ปรับส่วนหัวให้ไม่เบียด */
    .main-title { font-size: 20px; font-weight: bold; color: white; margin: 0; }
    .sub-title { font-size: 12px; color: #94a3b8; margin: 0; }
    .credit { position: fixed; bottom: 8px; right: 15px; color: #475569; font-size: 9px; z-index: 1000; }
    
    /* ลดระยะห่างเส้นคั่น */
    hr { margin: 0.8rem 0 !important; }
    </style>
    <div class="credit">produced by AE-IET [SBU]</div>
    """, unsafe_allow_html=True)

# --- 🛠️ ฟังก์ชันเชื่อมต่อฐานข้อมูล ---
def get_db_connection():
    base_dir = os.path.dirname(__file__)
    db_path = os.path.join(base_dir, 'data', 'ghg_data.db')
    return sqlite3.connect(db_path) if os.path.exists(db_path) else None

METRIC_MAP = {"คาร์บอนไดออกไซด์ (CO₂)": "co2", "มีเทน (CH₄)": "ch4", "ไนโตรเจน (NO₂)": "no2", "อุณหภูมิ (Temp)": "temp"}
REGION_MAP = {"ภาคเหนือ": "North", "ภาคกลาง": "Central", "ภาคใต้": "South", "ภาคอีสาน": "Northeast", "ภาคตะวันออก": "East", "ภาคตะวันตก": "West"}
COORDS = {"North": [18.78, 98.98], "Central": [13.75, 100.50], "South": [7.88, 98.39], "Northeast": [14.97, 102.10], "East": [12.92, 100.88], "West": [13.52, 99.81]}

# --- 🔝 HEADER (จัดให้เล็กลง) ---
h_col1, h_col2 = st.columns([2.5, 1.5])
with h_col1:
    l_col, t_col = st.columns([0.3, 3])
    with l_col: st.image("https://upload.wikimedia.org/wikipedia/th/thumb/a/a2/Southeast_Bangkok_University_Logo.png/200px-Southeast_Bangkok_University_Logo.png", width=55)
    with t_col:
        st.markdown('<p class="main-title">Dashboard “Tracking GHGs Emission”</p>', unsafe_allow_html=True)
        st.markdown('<p class="sub-title">อัปเดตข้อมูล: ทุก ๆ 1 ชั่วโมง</p>', unsafe_allow_html=True)

with h_col2:
    s1, s2 = st.columns(2)
    with s1: s_region = REGION_MAP[st.selectbox("📍 ภูมิภาค:", list(REGION_MAP.keys()), index=1)]
    with s2: 
        s_thai_metric = st.selectbox("📊 ดัชนี:", list(METRIC_MAP.keys()), index=0)
        s_metric = METRIC_MAP[s_thai_metric]

st.markdown("---")

# --- 📊 แสดงผลข้อมูล ---
conn = get_db_connection()
if conn:
    try:
        latest = pd.read_sql(f"SELECT * FROM ghg_logs WHERE region='{s_region}' ORDER BY timestamp DESC LIMIT 1", conn).iloc[0]
        history = pd.read_sql(f"SELECT * FROM ghg_logs WHERE region='{s_region}' ORDER BY timestamp DESC LIMIT 15", conn)
        all_data = pd.read_sql("SELECT region, MAX(co2) as co2, MAX(ch4) as ch4, MAX(no2) as no2, MAX(temp) as temp FROM ghg_logs GROUP BY region", conn)
        conn.close()

        # 1. แถบสรุปตัวเลข (เล็กลงและมีกรอบ)
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("CO₂ Level", f"{int(latest['co2'])} ppm")
        m2.metric("Methane (CH₄)", f"{latest['ch4']:.1f} ppb")
        m3.metric("Nitrogen (NO₂)", f"{latest['no2']:.1f} ppb")
        m4.metric("Temperature", f"{int(latest['temp'])}°C")

        st.write("") 

        # 2. ปรับสมดุล: แผนที่เล็กลง (1 ส่วน) : กราฟและตาราง (1.2 ส่วน)
        col_map, col_data = st.columns([1, 1.2])
        
        with col_map:
            st.markdown("### 🗺️ แผนที่โครงข่าย")
            all_data['lat'] = all_data['region'].map(lambda x: COORDS[x][0]); all_data['lon'] = all_data['region'].map(lambda x: COORDS[x][1])
            # ปรับ Zoom และ Pitch ให้เห็นภาพรวมไทยแบบพอดี
            st.pydeck_chart(pdk.Deck(
                map_style="mapbox://styles/mapbox/dark-v10",
                initial_view_state=pdk.ViewState(latitude=13.2, longitude=101.0, zoom=4.8, pitch=0),
                layers=[pdk.Layer("ScatterplotLayer", all_data, get_position="[lon, lat]", get_color="[45, 212, 191, 160]", get_radius=45000)],
                height=350 # จำกัดความสูงแผนที่
            ))

        with col_data:
            # กราฟแนวโน้ม
            st.markdown(f"### 📈 แนวโน้ม ทุก ๆ 1 ชั่วโมง")
            history['timestamp'] = pd
