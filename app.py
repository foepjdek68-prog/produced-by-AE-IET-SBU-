import streamlit as st
import pandas as pd
import plotly.express as px
import pydeck as pdk
import sqlite3
import os

# 1. ตั้งค่าหน้าจอ (ขยายเต็มจอและปิด Sidebar)
st.set_page_config(page_title="Tracking GHGs Emission", layout="wide", initial_sidebar_state="collapsed")

# --- 🎨 CSS: บังคับให้ทุกอย่างกะทัดรัด (Compact) เพื่อให้เห็นครบในหน้าจอเดียว ---
st.markdown("""
    <style>
    .block-container { padding-top: 1rem !important; padding-bottom: 0rem !important; }
    
    /* ส่วนหัว */
    .main-title { font-size: 22px; font-weight: bold; color: white; margin: 0; }
    .sub-title { font-size: 12px; color: #94a3b8; margin-bottom: 5px; }

    /* ตกแต่ง Metric Card ให้เล็กลง */
    div[data-testid="stMetric"] { background: #1e293b; padding: 5px 10px; border-radius: 6px; border: 1px solid #334155; }
    [data-testid="stMetricValue"] { font-size: 18px !important; color: #2dd4bf !important; }
    [data-testid="stMetricLabel"] { font-size: 11px !important; }
    
    /* Credit มุมล่างขวา */
    .credit { position: fixed; bottom: 5px; right: 15px; color: #475569; font-size: 9px; z-index: 1000; }
    
    hr { margin: 0.5rem 0 !important; }
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

# --- 🔝 Header: Logo & Title ---
h1, h2 = st.columns([0.5, 6])
with h1: st.image("https://upload.wikimedia.org/wikipedia/th/thumb/a/a2/Southeast_Bangkok_University_Logo.png/200px-Southeast_Bangkok_University_Logo.png", width=60)
with h2:
    st.markdown('<p class="main-title">Dashboard “Tracking GHGs Emission”</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">produced by AE-IET [SBU]</p>', unsafe_allow_html=True)

# แถวตัวเลือกและ Metrics
c_s1, c_s2, c_m1, c_m2, c_m3, c_m4 = st.columns([1, 1, 1, 1, 1, 1])

conn = get_db_connection()
if conn:
    try:
        s_region_thai = c_s1.selectbox("📍 พื้นที่:", list(REGION_MAP.keys()), index=1)
        s_region = REGION_MAP[s_region_thai]
        s_thai_metric = c_s2.selectbox("📊 ดัชนี:", list(METRIC_MAP.keys()), index=0)
        s_metric = METRIC_MAP[s_thai_metric]

        latest = pd.read_sql(f"SELECT * FROM ghg_logs WHERE region='{s_region}' ORDER BY timestamp DESC LIMIT 1", conn).iloc[0]
        history = pd.read_sql(f"SELECT * FROM ghg_logs WHERE region='{s_region}' ORDER BY timestamp DESC LIMIT 15", conn)
        all_data = pd.read_sql("SELECT region, MAX(co2) as co2, MAX(ch4) as ch4, MAX(no2) as no2, MAX(temp) as temp FROM ghg_logs GROUP BY region", conn)
        conn.close()

        c_m1.metric("CO₂", f"{int(latest['co2'])} ppm")
        c_m2.metric("CH₄", f"{latest['ch4']:.1f} ppb")
        c_m3.metric("NO₂", f"{latest['no2']:.1f} ppb")
        c_m4.metric("Temp", f"{int(latest['temp'])}°C")

        st.markdown("---")

        # --- 🏗️ NEW LAYOUT: [ซ้าย: แผนที่] [ขวา: กราฟ + อันดับ] ---
        col_left, col_right = st.columns([1.2, 1])
        
        with col_left:
            st.markdown("##### 🗺️ แผนที่พยากรณ์สถานี (2D)")
            all_data['lat'] = all_data['region'].map(lambda x: COORDS[x][0]); all_data['lon'] = all_data['region'].map(lambda x: COORDS[x][1])
            st.pydeck_chart(pdk.Deck(
                map_style="mapbox://styles/mapbox/dark-v10",
                initial_view_state=pdk.ViewState(latitude=13.8, longitude=100.6, zoom=5.2, pitch=0),
                layers=[pdk.Layer("ScatterplotLayer", all_data, get_position="[lon, lat]", get_color="[45, 212, 191, 180]", get_radius=40000)],
                height=480 # เพิ่มความสูงแผนที่ให้สมดุลกับฝั่งขวา
            ))

        with col_right:
            # 1. กราฟแนวโน้ม (ลดขนาดลง)
            st.markdown(f"##### 📈 แนวโน้ม {s_thai_metric.split(' (')[0]}")
            history['timestamp'] = pd.to_datetime(history['timestamp'])
            fig = px.line(history.sort_values('timestamp'), x='timestamp', y=s_metric, height=220, color_discrete_sequence=['#2dd4bf'])
            fig.update_layout(margin=dict(l=0, r=0, t=5, b=5), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_size=9)
            st.plotly_chart(fig, use_container_width=True)
            
            # 2. ตารางอันดับ (วางต่อท้ายกราฟ)
            st.markdown(f"##### 🏆 อันดับสูงสุด")
            df_rank = all_data.sort_values(by=s_metric, ascending=False)
            inv_m = {v: k for k, v in REGION_MAP.items()}
            df_rank['ภูมิภาค'] = df_rank['region'].map(inv_m)
            st.dataframe(df_rank[['ภูมิภาค', s_metric]], hide_index=True, use_container_width=True, height=180)
            
    except Exception as e: st.info("🔄 กำลังเตรียมข้อมูล...")
else: st.error("⚠️ ไม่พบฐานข้อมูล")
