import streamlit as st
import pandas as pd
import plotly.express as px
import pydeck as pdk
import sqlite3
import os

# 1. ตั้งค่าพื้นฐาน
st.set_page_config(page_title="GHGs Monitoring SBU", layout="wide", initial_sidebar_state="collapsed")

# --- 🎨 CSS: ปรับสีพื้นหลังแอปเป็นสีเทาดำ เพื่อให้ต่างจากแผนที่สีกรมท่า ---
st.markdown("""
    <style>
    .stApp { background-color: #111827; } /* สีเทาดำ Charcoal */
    .block-container { padding: 1rem 2rem !important; }
    
    /* การ์ดตัวเลขสรุป */
    div[data-testid="stMetric"] { 
        background: #1f2937; 
        padding: 15px; 
        border-radius: 12px; 
        border-left: 5px solid #06b6d4;
    }
    [data-testid="stMetricValue"] { color: #22d3ee !important; font-weight: bold; }
    
    /* ส่วนหัว */
    .header-text { font-size: 26px; font-weight: 800; color: #f9fafb; margin: 0; }
    .sub-text { font-size: 13px; color: #9ca3af; margin-bottom: 10px; }
    hr { border-top: 1px solid #374151; margin: 1rem 0 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 🛠️ ฟังก์ชันดึงข้อมูล ---
def get_db_connection():
    db_path = os.path.join(os.path.dirname(__file__), 'data', 'ghg_data.db')
    return sqlite3.connect(db_path) if os.path.exists(db_path) else None

METRIC_MAP = {"คาร์บอนไดออกไซด์ (CO₂)": "co2", "มีเทน (CH₄)": "ch4", "ไนโตรเจน (NO₂)": "no2", "อุณหภูมิ (Temp)": "temp"}
REGION_MAP = {"ภาคเหนือ": "North", "ภาคกลาง": "Central", "ภาคใต้": "South", "ภาคอีสาน": "Northeast", "ภาคตะวันออก": "East", "ภาคตะวันตก": "West"}
COORDS = {"North": [18.78, 98.98], "Central": [13.75, 100.50], "South": [7.88, 98.39], "Northeast": [14.97, 102.10], "East": [12.92, 100.88], "West": [13.52, 99.81]}

# --- 🔝 ส่วนหัวและตัวเลือก ---
c1, c2 = st.columns([2, 1])
with c1:
    st.markdown('<p class="header-text">TRACKING GHGs EMISSION</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-text">produced by AE-IET [SBU]</p>', unsafe_allow_html=True)

with c2:
    s_col1, s_col2 = st.columns(2)
    with s_col1:
        region_thai = st.selectbox("📍 พื้นที่:", list(REGION_MAP.keys()), index=1)
        s_region = REGION_MAP[region_thai]
    with s_col2:
        metric_thai = st.selectbox("📊 ดัชนี:", list(METRIC_MAP.keys()), index=0)
        s_metric = METRIC_MAP[metric_thai]

st.markdown("---")

# --- 📊 ส่วนแสดงผลหลัก ---
conn = get_db_connection()
if conn:
    try:
        # ดึงข้อมูล
        latest = pd.read_sql(f"SELECT * FROM ghg_logs WHERE region='{s_region}' ORDER BY timestamp DESC LIMIT 1", conn).iloc[0]
        history = pd.read_sql(f"SELECT * FROM ghg_logs WHERE region='{s_region}' ORDER BY timestamp DESC LIMIT 15", conn)
        all_data = pd.read_sql("SELECT region, MAX(co2) as co2, MAX(ch4) as ch4, MAX(no2) as no2, MAX(temp) as temp FROM ghg_logs GROUP BY region", conn)
        conn.close()

        # 1. แสดงค่า Metric 4 ตัว
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("CO₂", f"{int(latest['co2'])} ppm")
        m2.metric("CH₄", f"{latest['ch4']:.1f} ppb")
        m3.metric("NO₂", f"{latest['no2']:.1f} ppb")
        m4.metric("Temp", f"{int(latest['temp'])}°C")

        st.write("")

        # 2. **แก้บัคตรงนี้** สร้าง col_map และ col_right ก่อนใช้งาน
        col_map, col_right = st.columns([1.2, 1])

        with col_map:
            st.markdown("##### 🗺️ แผนที่โครงข่าย (สีกรมท่า)")
            all_data['lat'] = all_data['region'].map(lambda x: COORDS[x][0])
            all_data['lon'] = all_data['region'].map(lambda x: COORDS[x][1])
            
            # ปรับ Map Style ให้เป็นสีกรมท่า (Dark) ตัดกับพื้นหลังแอปที่เป็นสีเทาดำ
            st.pydeck_chart(pdk.Deck(
                map_style="mapbox://styles/mapbox/dark-v11",
                initial_view_state=pdk.ViewState(latitude=13.5, longitude=101, zoom=5.1),
                layers=[
                    pdk.Layer(
                        "ScatterplotLayer",
                        all_data,
                        get_position="[lon, lat]",
                        get_color="[34, 211, 238, 200]", # สีฟ้า Cyan
                        get_radius=50000,
                    )
                ],
            ))

        with col_right:
            # กราฟแนวโน้ม
            st.markdown(f"##### 📈 แนวโน้ม {metric_thai.split(' (')[0]}")
            history['timestamp'] = pd.to_datetime(history['timestamp'])
            fig = px.line(history.sort_values('timestamp'), x='timestamp', y=s_metric, height=240, color_discrete_sequence=['#22d3ee'])
            fig.update_layout(margin=dict(l=0, r=0, t=10, b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="#9ca3af")
            st.plotly_chart(fig, use_container_width=True)
            
            # ตารางอันดับ
            st.markdown(f"##### 🏆 อันดับค่ามลพิษสูงสุด")
            df_rank = all_data.sort_values(by=s_metric, ascending=False)
            df_rank['ภูมิภาค'] = df_rank['region'].map({v: k for k, v in REGION_MAP.items()})
            st.dataframe(df_rank[['ภูมิภาค', s_metric]], hide_index=True, use_container_width=True, height=180)

    except Exception as e:
        st.error(f"เกิดข้อผิดพลาดในการโหลดข้อมูล: {e}")
else:
    st.error("⚠️ ไม่พบฐานข้อมูล ghg_data.db ในโฟลเดอร์ data/")
