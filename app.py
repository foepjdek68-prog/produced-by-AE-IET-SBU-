import streamlit as st
import pandas as pd
import plotly.express as px
import pydeck as pdk
import sqlite3
import os

# 1. ตั้งค่าหน้าจอ (Wide Mode)
st.set_page_config(page_title="GHGs Monitoring SBU", layout="wide", initial_sidebar_state="collapsed")

# --- 🎨 CSS: ปรับโทนสีและตำแหน่งโลโก้เครดิต ---
st.markdown("""
    <style>
    /* พื้นหลังแอปสีเทาดำ Charcoal */
    .stApp { background-color: #111827; } 
    
    /* ตกแต่ง Metric Cards */
    div[data-testid="stMetric"] { 
        background: #1f2937; 
        padding: 15px; 
        border-radius: 12px; 
        border-left: 5px solid #22d3ee;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    [data-testid="stMetricValue"] { color: #22d3ee !important; font-weight: bold; }

    /* โลโก้เครดิตมุมขวาล่าง (Floating Logo) */
    .credit-container {
        position: fixed;
        bottom: 20px;
        right: 20px;
        z-index: 1000;
        text-align: center;
        background: rgba(31, 41, 55, 0.8);
        padding: 10px;
        border-radius: 10px;
        border: 1px solid rgba(255,255,255,0.1);
        backdrop-filter: blur(5px);
    }
    .credit-logo { width: 60px; margin-bottom: 5px; }
    .credit-text { color: #9ca3af; font-size: 10px; font-weight: 600; }
    </style>
    
    <div class="credit-container">
        <img src="https://upload.wikimedia.org/wikipedia/th/thumb/a/a2/Southeast_Bangkok_University_Logo.png/200px-Southeast_Bangkok_University_Logo.png" class="credit-logo">
        <div class="credit-text">Produced by AE-IET [SBU]</div>
    </div>
    """, unsafe_allow_html=True)

# --- 🛠️ ส่วนจัดการข้อมูล ---
def get_db_connection():
    db_path = os.path.join(os.path.dirname(__file__), 'data', 'ghg_data.db')
    return sqlite3.connect(db_path) if os.path.exists(db_path) else None

METRIC_MAP = {"คาร์บอนไดออกไซด์ (CO₂)": "co2", "มีเทน (CH₄)": "ch4", "ไนโตรเจน (NO₂)": "no2", "อุณหภูมิ (Temp)": "temp"}
REGION_MAP = {"ภาคเหนือ": "North", "ภาคกลาง": "Central", "ภาคใต้": "South", "ภาคอีสาน": "Northeast", "ภาคตะวันออก": "East", "ภาคตะวันตก": "West"}
COORDS = {"North": [18.78, 98.98], "Central": [13.75, 100.50], "South": [7.88, 98.39], "Northeast": [14.97, 102.10], "East": [12.92, 100.88], "West": [13.52, 99.81]}

# --- 🔝 Header & Selection ---
h_col1, h_col2 = st.columns([2, 1.2])
with h_col1:
    st.markdown('<h2 style="color:white; margin:0;">TRACKING GHGs EMISSION</h2>', unsafe_allow_html=True)
    st.markdown('<p style="color:#9ca3af;">Environmental Monitoring Dashboard</p>', unsafe_allow_html=True)

with h_col2:
    s1, s2 = st.columns(2)
    with s1: s_region = REGION_MAP[st.selectbox("📍 ภูมิภาค:", list(REGION_MAP.keys()), index=1)]
    with s2: 
        s_thai_metric = st.selectbox("📊 ดัชนี:", list(METRIC_MAP.keys()), index=0)
        s_metric = METRIC_MAP[s_thai_metric]

st.markdown("---")

# --- 📊 Dashboard Content ---
conn = get_db_connection()
if conn:
    try:
        # ดึงข้อมูลจาก Database
        latest = pd.read_sql(f"SELECT * FROM ghg_logs WHERE region='{s_region}' ORDER BY timestamp DESC LIMIT 1", conn).iloc[0]
        history = pd.read_sql(f"SELECT * FROM ghg_logs WHERE region='{s_region}' ORDER BY timestamp DESC LIMIT 15", conn)
        all_data = pd.read_sql("SELECT region, MAX(co2) as co2, MAX(ch4) as ch4, MAX(no2) as no2, MAX(temp) as temp FROM ghg_logs GROUP BY region", conn)
        conn.close()

        # 1. แถบ Metric Cards
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("CO₂ Level", f"{int(latest['co2'])} ppm")
        m2.metric("Methane (CH₄)", f"{latest['ch4']:.1f} ppb")
        m3.metric("Nitrogen (NO₂)", f"{latest['no2']:.1f} ppb")
        m4.metric("Temperature", f"{int(latest['temp'])}°C")

        st.write("")

        # 2. การจัดเลย์เอาต์ (แก้ NameError โดยการประกาศตัวแปรก่อนเรียกใช้)
        col_left_map, col_right_data = st.columns([1.2, 1])

        with col_left_map:
            st.markdown("##### 🗺️ แผนที่โครงข่ายสถานี (2D View)")
            all_data['lat'] = all_data['region'].map(lambda x: COORDS[x][0])
            all_data['lon'] = all_data['region'].map(lambda x: COORDS[x][1])
            
            # ปรับ Map Style เป็นสีกรมท่าตัดกับแอปสีดำ
            st.pydeck_chart(pdk.Deck(
                map_style="mapbox://styles/mapbox/dark-v11",
                initial_view_state=pdk.ViewState(latitude=13.5, longitude=101, zoom=5),
                layers=[
                    pdk.Layer(
                        "ScatterplotLayer",
                        all_data,
                        get_position="[lon, lat]",
                        get_color="[34, 211, 238, 180]", # สีฟ้า Cyan
                        get_radius=50000,
                    )
                ],
            ))

        with col_right_data:
            # กราฟแนวโน้ม
            st.markdown(f"##### 📈 แนวโน้ม {s_thai_metric.split(' (')[0]}")
            history['timestamp'] = pd.to_datetime(history['timestamp'])
            fig = px.line(history.sort_values('timestamp'), x='timestamp', y=s_metric, height=230, color_discrete_sequence=['#22d3ee'])
            fig.update_layout(margin=dict(l=0, r=0, t=10, b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="#9ca3af")
            st.plotly_chart(fig, use_container_width=True)
            
            # ตารางอันดับ
            st.markdown("##### 🏆 อันดับค่ามลพิษสูงสุด")
            df_rank = all_data.sort_values(by=s_metric, ascending=False)
            inv_map = {v: k for k, v in REGION_MAP.items()}
            df_rank['ภูมิภาค'] = df_rank['region'].map(inv_map)
            st.dataframe(df_rank[['ภูมิภาค', s_metric]], hide_index=True, use_container_width=True, height=160)

    except Exception as e:
        st.error(f"เกิดข้อผิดพลาด: {e}")
else:
    st.error("⚠️ ไม่พบฐานข้อมูลระบบในโฟลเดอร์ data/")
