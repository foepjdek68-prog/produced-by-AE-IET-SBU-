import streamlit as st
import pandas as pd
import plotly.express as px
import pydeck as pdk
import sqlite3
import os

# 1. ตั้งค่าหน้าจอ (ขยายเต็มจอ และซ่อน Sidebar)
st.set_page_config(page_title="Tracking GHGs Emission", layout="wide", initial_sidebar_state="collapsed")

# --- 🎨 CSS: จัดระเบียบหน้าจอให้เล็กลงและสมดุล (Compact & Professional) ---
st.markdown("""
    <style>
    /* ลด Padding รอบหน้าจอ */
    .block-container { padding: 1rem 2rem !important; }
    
    /* ปรับแต่ง Metric (ตัวเลข) ให้เล็กลงและมีระยะห่างที่พอดี */
    [data-testid="stMetricValue"] { font-size: 18px !important; color: #2dd4bf !important; }
    [data-testid="stMetricLabel"] { font-size: 12px !important; color: #94a3b8 !important; }
    div[data-testid="stMetric"] { background: #1e293b; padding: 10px; border-radius: 6px; }

    /* จัดการส่วนหัวให้เรียบหรู */
    .main-title { font-size: 20px; font-weight: bold; color: white; margin: 0; line-height: 1.2; }
    .sub-title { font-size: 12px; color: #94a3b8; margin: 0; }
    
    /* Credit มุมล่างขวา */
    .credit { position: fixed; bottom: 5px; right: 15px; color: #475569; font-size: 9px; z-index: 1000; }
    
    /* ลดระยะห่างเส้นคั่น */
    hr { margin: 0.5rem 0 !important; }
    
    /* ปรับแต่งตาราง */
    .stDataFrame { border-radius: 8px; overflow: hidden; }
    </style>
    <div class="credit">produced by AE-IET [SBU]</div>
    """, unsafe_allow_html=True)

# --- 🛠️ ฟังก์ชันเชื่อมต่อฐานข้อมูล ---
def get_db_connection():
    base_dir = os.path.dirname(__file__)
    db_path = os.path.join(base_dir, 'data', 'ghg_data.db')
    return sqlite3.connect(db_path) if os.path.exists(db_path) else None

# ตัวเลือกดัชนีและพื้นที่
METRIC_MAP = {"คาร์บอนไดออกไซด์ (CO₂)": "co2", "มีเทน (CH₄)": "ch4", "ไนโตรเจน (NO₂)": "no2", "อุณหภูมิ (Temp)": "temp"}
REGION_MAP = {"ภาคเหนือ": "North", "ภาคกลาง": "Central", "ภาคใต้": "South", "ภาคอีสาน": "Northeast", "ภาคตะวันออก": "East", "ภาคตะวันตก": "West"}
COORDS = {"North": [18.78, 98.98], "Central": [13.75, 100.50], "South": [7.88, 98.39], "Northeast": [14.97, 102.10], "East": [12.92, 100.88], "West": [13.52, 99.81]}

# --- 🔝 HEADER: จัดระเบียบให้โลโก้และชื่อไม่ซ้อนกัน ---
h_col1, h_col2 = st.columns([2, 1])

with h_col1:
    l_col, t_col = st.columns([0.3, 3])
    with l_col: 
        # โลโก้ SBU
        st.image("https://upload.wikimedia.org/wikipedia/th/thumb/a/a2/Southeast_Bangkok_University_Logo.png/200px-Southeast_Bangkok_University_Logo.png", width=50)
    with t_col:
        st.markdown('<p class="main-title">Dashboard “Tracking GHGs Emission”</p>', unsafe_allow_html=True)
        st.markdown('<p class="sub-title">อัปเดตข้อมูล: ทุก ๆ 1 ชั่วโมง</p>', unsafe_allow_html=True)

with h_col2:
    s1, s2 = st.columns(2)
    with s1: s_region = REGION_MAP[st.selectbox("📍 เลือกภูมิภาค:", list(REGION_MAP.keys()), index=1, label_visibility="collapsed")]
    with s2: 
        s_thai_metric = st.selectbox("📊 เลือกดัชนี:", list(METRIC_MAP.keys()), index=0, label_visibility="collapsed")
        s_metric = METRIC_MAP[s_thai_metric]

st.markdown("---")

# --- 📊 ส่วนแสดงผลข้อมูล ---
conn = get_db_connection()
if conn:
    try:
        latest = pd.read_sql(f"SELECT * FROM ghg_logs WHERE region='{s_region}' ORDER BY timestamp DESC LIMIT 1", conn).iloc[0]
        history = pd.read_sql(f"SELECT * FROM ghg_logs WHERE region='{s_region}' ORDER BY timestamp DESC LIMIT 15", conn)
        all_data = pd.read_sql("SELECT region, MAX(co2) as co2, MAX(ch4) as ch4, MAX(no2) as no2, MAX(temp) as temp FROM ghg_logs GROUP BY region", conn)
        conn.close()

        # 1. แถบสรุปตัวเลข (Metric Cards)
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("CO₂ Level", f"{int(latest['co2'])} ppm")
        m2.metric("Methane (CH₄)", f"{latest['ch4']:.1f} ppb")
        m3.metric("Nitrogen (NO₂)", f"{latest['no2']:.1f} ppb")
        m4.metric("Temperature", f"{int(latest['temp'])}°C")

        st.write("") # เว้นวรรคนิดหน่อย

        # 2. จัด Layout กราฟและแผนที่ให้สมดุล (แผนที่เล็กลง ข้อมูลเด่นขึ้น)
        col_left, col_mid, col_right = st.columns([1, 1.2, 0.8])
        
        with col_left:
            st.markdown("##### 🗺️ แผนที่โครงข่าย")
            all_data['lat'] = all_data['region'].map(lambda x: COORDS[x][0]); all_data['lon'] = all_data['region'].map(lambda x: COORDS[x][1])
            st.pydeck_chart(pdk.Deck(
                map_style="mapbox://styles/mapbox/dark-v10",
                initial_view_state=pdk.ViewState(latitude=13.5, longitude=101.0, zoom=4.6, pitch=0),
                layers=[pdk.Layer("ScatterplotLayer", all_data, get_position="[lon, lat]", get_color="[45, 212, 191, 160]", get_radius=40000)],
                height=300
            ))

        with col_mid:
            st.markdown(f"##### 📈 แนวโน้ม ทุก ๆ 1 ชั่วโมง")
            history['timestamp'] = pd.to_datetime(history['timestamp'])
            fig = px.line(history.sort_values('timestamp'), x='timestamp', y=s_metric, height=220, color_discrete_sequence=['#2dd4bf'])
            fig.update_layout(margin=dict(l=0, r=0, t=10, b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_size=10)
            st.plotly_chart(fig, use_container_width=True)

        with col_right:
            st.markdown(f"##### 🏆 อันดับสูงสุด")
            df_rank = all_data.sort_values(by=s_metric, ascending=False)
            inv_m = {v: k for k, v in REGION_MAP.items()}
            df_rank['ภูมิภาค'] = df_rank['region'].map(inv_m)
            st.dataframe(df_rank[['ภูมิภาค', s_metric]], hide_index=True, use_container_width=True, height=220)
            
    except Exception as e: st.info("🔄 กำลังประมวลผลข้อมูล...")
else: st.error("⚠️ ไม่พบฐานข้อมูล กรุณาตรวจสอบไฟล์ ghg_data.db")
