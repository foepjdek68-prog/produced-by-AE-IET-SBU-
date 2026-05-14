import streamlit as st
import pandas as pd
import plotly.express as px
import pydeck as pdk
import sqlite3
import os

# 1. ตั้งค่าหน้าจอ
st.set_page_config(page_title="Tracking GHGs Emission", layout="wide", initial_sidebar_state="collapsed")

# --- 🎨 CSS: บังคับให้ Logo และ Title อยู่ด้านบนสุด ไม่ให้มีที่ว่าง ---
st.markdown("""
    <style>
    /* ลด Padding ด้านบนสุด */
    .block-container { padding-top: 1rem !important; padding-bottom: 0rem !important; }
    
    /* สไตล์หัวข้อ */
    .main-title { font-size: 26px; font-weight: bold; color: white; margin: 0; }
    .sub-title { font-size: 14px; color: #94a3b8; margin-bottom: 10px; }

    /* ตกแต่ง Metric Card ให้เล็กลงแต่ชัดเจน */
    div[data-testid="stMetric"] { 
        background: #1e293b; 
        padding: 10px 15px; 
        border-radius: 8px; 
        border: 1px solid #334155;
    }
    [data-testid="stMetricValue"] { font-size: 20px !important; color: #2dd4bf !important; }
    
    /* Credit มุมล่างขวา */
    .credit { position: fixed; bottom: 10px; right: 20px; color: #475569; font-size: 10px; z-index: 1000; }
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

# --- 🔝 ส่วนหัว (Header): บังคับให้ Logo อยู่บนสุดซ้ายมือ ---
# ใช้ Column สัดส่วนกว้างเพื่อให้ Logo และ Title อยู่ติดกัน ไม่กระเด็นไปไกล
head_l, head_r = st.columns([0.5, 5])
with head_l:
    st.image("https://upload.wikimedia.org/wikipedia/th/thumb/a/a2/Southeast_Bangkok_University_Logo.png/200px-Southeast_Bangkok_University_Logo.png", width=80)
with head_r:
    st.markdown('<p class="main-title">Dashboard “Tracking GHGs Emission”</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">อัปเดตข้อมูล: ทุก ๆ 1 ชั่วโมง</p>', unsafe_allow_html=True)

# แถวสำหรับตัวเลือกและ Metrics (จัดให้อยู่ในแถวเดียวกันเพื่อประหยัดพื้นที่)
col_sel1, col_sel2, col_m1, col_m2, col_m3, col_m4 = st.columns([1, 1.2, 1, 1, 1, 1])

conn = get_db_connection()
if conn:
    try:
        # วาง Selectbox ในคอลัมน์แรกๆ
        s_region_thai = col_sel1.selectbox("📍 พื้นที่:", list(REGION_MAP.keys()), index=1)
        s_region = REGION_MAP[s_region_thai]
        s_thai_metric = col_sel2.selectbox("📊 ดัชนี:", list(METRIC_MAP.keys()), index=0)
        s_metric = METRIC_MAP[s_thai_metric]

        latest = pd.read_sql(f"SELECT * FROM ghg_logs WHERE region='{s_region}' ORDER BY timestamp DESC LIMIT 1", conn).iloc[0]
        history = pd.read_sql(f"SELECT * FROM ghg_logs WHERE region='{s_region}' ORDER BY timestamp DESC LIMIT 15", conn)
        all_data = pd.read_sql("SELECT region, MAX(co2) as co2, MAX(ch4) as ch4, MAX(no2) as no2, MAX(temp) as temp FROM ghg_logs GROUP BY region", conn)
        conn.close()

        # แสดง Metrics ต่อท้ายตัวเลือก
        col_m1.metric("CO₂", f"{int(latest['co2'])} ppm")
        col_m2.metric("CH₄", f"{latest['ch4']:.1f} ppb")
        col_m3.metric("NO₂", f"{latest['no2']:.1f} ppb")
        col_m4.metric("Temp", f"{int(latest['temp'])}°C")

        st.markdown("---")

        # --- 🏗️ ส่วนแสดงผลหลัก: [ซ้าย: แผนที่ 2D + อันดับ] [ขวา: กราฟแนวโน้ม] ---
        col_left, col_right = st.columns([1, 1.5])
        
        with col_left:
            st.markdown("##### 🗺️ แผนที่พยากรณ์โครงข่ายสถานี (2D)")
            all_data['lat'] = all_data['region'].map(lambda x: COORDS[x][0]); all_data['lon'] = all_data['region'].map(lambda x: COORDS[x][1])
            st.pydeck_chart(pdk.Deck(
                map_style="mapbox://styles/mapbox/dark-v10",
                initial_view_state=pdk.ViewState(latitude=13.5, longitude=101.0, zoom=4.5, pitch=0),
                layers=[pdk.Layer("ScatterplotLayer", all_data, get_position="[lon, lat]", get_color="[45, 212, 191, 180]", get_radius=45000)],
                height=300
            ))
            
            st.write("") # เว้นวรรค
            st.markdown(f"##### 🏆 อันดับ{s_thai_metric.split(' (')[0]}สูงสุด")
            df_rank = all_data.sort_values(by=s_metric, ascending=False)
            inv_m = {v: k for k, v in REGION_MAP.items()}
            df_rank['ภูมิภาค'] = df_rank['region'].map(inv_m)
            st.dataframe(df_rank[['ภูมิภาค', s_metric]], hide_index=True, use_container_width=True, height=200)

        with col_right:
            st.markdown(f"##### 📈 แนวโน้ม ทุก ๆ 1 ชั่วโมง")
            history['timestamp'] = pd.to_datetime(history['timestamp'])
            fig = px.line(history.sort_values('timestamp'), x='timestamp', y=s_metric, height=530, color_discrete_sequence=['#2dd4bf'])
            fig.update_layout(
                margin=dict(l=0, r=0, t=10, b=0),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(size=10)
            )
            st.plotly_chart(fig, use_container_width=True)
            
    except Exception as e: st.info(f"🔄 กำลังโหลดข้อมูล... ({e})")
else: st.error("⚠️ ไม่พบฐานข้อมูล กรุณาเช็คโฟลเดอร์ data/ghg_data.db")
