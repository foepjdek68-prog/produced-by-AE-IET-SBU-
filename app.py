import streamlit as st
import pandas as pd
import plotly.express as px
import pydeck as pdk
import sqlite3
import os

# 1. ตั้งค่าหน้าจอและชื่อโปรเจกต์
st.set_page_config(page_title="Tracking GHGs Emission", layout="wide", initial_sidebar_state="collapsed")

# --- 🎨 CSS: ตกแต่ง UI และใส่ Credit มุมขวาล่าง ---
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

# --- ข้อมูลพิกัดและตัวเลือกดัชนี (Unicode Subscript) ---
COORDS = {"North": [18.78, 98.98], "Central": [13.75, 100.50], "South": [7.88, 98.39], "Northeast": [14.97, 102.10], "East": [12.92, 100.88], "West": [13.52, 99.81]}
REGION_MAP = {"ภาคเหนือ": "North", "ภาคกลาง": "Central", "ภาคใต้": "South", "ภาคอีสาน": "Northeast", "ภาคตะวันออก": "East", "ภาคตะวันตก": "West"}
METRIC_MAP = {"คาร์บอนไดออกไซด์ (CO₂ร)": "co2", "มีเทน (CH₄)": "ch4", "ไนโตรเจน (NO₂)": "no2", "อุณหภูมิ (Temp)": "temp"}

def get_db_connection():
    # ดึงไฟล์จากโฟลเดอร์ data ที่คุณสร้างใหม่
    db_path = os.path.join(os.path.dirname(__file__), 'data', 'ghg_data.db')
    if not os.path.exists(db_path): return None
    return sqlite3.connect(db_path)

# --- ส่วน Header: Logo + Title ---
col_logo, col_title, col_reg, col_met = st.columns([0.6, 2, 1, 1])

with col_logo:
    # Logo มหาวิทยาลัย (เปลี่ยน URL ได้ตามต้องการ)
    st.image("https://upload.wikimedia.org/wikipedia/commons/d/d4/Logo_Srinakharinwirot_University.png", width=65)

with col_title:
    st.markdown('<p class="main-title">Dashboard “Tracking GHGs Emission”</p>', unsafe_allow_html=True)
    st.caption("อัปเดตข้อมูล: ทุก ๆ 1 ชั่วโมง")

with col_reg:
    selected_thai_region = st.selectbox("📍 เลือกภูมิภาค:", list(REGION_MAP.keys()), index=1)
    selected_region = REGION_MAP[selected_thai_region]

with col_met:
    selected_thai_metric = st.selectbox("📊 เลือกดัชนี:", list(METRIC_MAP.keys()), index=0)
    selected_metric = METRIC_MAP[selected_thai_metric]

# --- การดึงข้อมูลและแสดงผลกราฟ/แผนที่ ---
conn = get_db_connection()
if conn:
    try:
        latest_df = pd.read_sql(f"SELECT * FROM ghg_logs WHERE region='{selected_region}' ORDER BY timestamp DESC LIMIT 1", conn)
        history_df = pd.read_sql(f"SELECT * FROM ghg_logs WHERE region='{selected_region}' ORDER BY timestamp DESC LIMIT 15", conn)
        all_df = pd.read_sql("SELECT region, co2, ch4, no2, temp FROM ghg_logs GROUP BY region", conn)
        conn.close()

        if not latest_df.empty:
            latest = latest_df.iloc[0]
            st.markdown("---")
            
            # 1. แถบสรุปตัวเลข (Metrics)
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("CO₂ Level", f"{int(latest['co2'])} ppm")
            m2.metric("Methane (CH₄)", f"{latest['ch4']:.1f} ppb")
            m3.metric("Nitrogen (NO₂)", f"{latest['no2']:.1f} ppb")
            m4.metric("Temperature", f"{int(latest['temp'])}°C")

            # 2. แผนที่ 3D และกราฟแนวโน้ม
            c_l, c_r = st.columns([1.6, 1])
            with c_l:
                st.markdown("### 🗺️ แผนที่พยากรณ์โครงข่ายสถานี")
                all_df['lat'] = all_df['region'].map(lambda x: COORDS[x][0])
                all_df['lon'] = all_df['region'].map(lambda x: COORDS[x][1])
                st.pydeck_chart(pdk.Deck(
                    map_style="https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json",
                    initial_view_state=pdk.ViewState(latitude=13.0, longitude=101.0, zoom=4.5, pitch=40),
                    layers=[pdk.Layer("ScatterplotLayer", all_df, get_position="[lon, lat]", get_color="[45, 212, 191, 180]", get_radius=50000, pickable=True)],
                    tooltip={"text": "{region}: {temp}°C"}
                ))

            with c_r:
                clean_title = selected_thai_metric.split(" (")[0]
                st.markdown(f"### 📈 แนวโน้ม ทุก ๆ 1 ชั่วโมง")
                
                history_df['timestamp'] = pd.to_datetime(history_df['timestamp'])
                fig = px.line(history_df.sort_values('timestamp'), x='timestamp', y=selected_metric, height=180, color_discrete_sequence=['#2dd4bf'])
                fig.update_layout(margin=dict(l=0, r=0, t=5, b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="#94a3b8")
                st.plotly_chart(fig, use_container_width=True)

                st.markdown(f"### 🏆 อันดับ{clean_title}สูงสุด")
                df_rank = all_df.sort_values(by=selected_metric, ascending=False)
                inv_m = {v: k for k, v in REGION_MAP.items()}
                df_rank['ภูมิภาค'] = df_rank['region'].map(inv_m)
                st.dataframe(df_rank[['ภูมิภาค', selected_metric]], hide_index=True, use_container_width=True, height=140)
    except:
        st.info("🔄 กำลังดึงข้อมูลจากโครงข่าย...")
else:
    st.error("⚠️ ไม่พบไฟล์ฐานข้อมูลใน data/ghg_data.db")