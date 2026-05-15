import streamlit as st
import pandas as pd
import plotly.express as px
import pydeck as pdk
import sqlite3
import os

# 1. SETUP: ขยายหน้าจอเต็มพิกัด
st.set_page_config(page_title="GHGs Emission Monitoring", layout="wide", initial_sidebar_state="collapsed")

# --- 🎨 CSS: บังคับสีพื้นหลังหน้าเว็บกับ Widget ให้คนละโทนเพื่อให้ดูมีมิติ ---
st.markdown("""
    <style>
    /* 1. พื้นหลังหลักของหน้าเว็บ (สีกรมท่าเข้มมาก) */
    .stApp { background-color: #0f172a; }
    .block-container { padding: 1rem 2rem !important; }

    /* 2. การ์ดสรุปตัวเลข (สีเทา Slate) */
    div[data-testid="stMetric"] { 
        background: #1e293b; 
        padding: 12px; 
        border-radius: 10px; 
        border: 1px solid #334155;
    }
    [data-testid="stMetricValue"] { font-size: 22px !important; color: #22d3ee !important; }
    [data-testid="stMetricLabel"] { font-size: 13px !important; color: #94a3b8 !important; }

    /* 3. ส่วนหัว (Title) */
    .main-title { font-size: 24px; font-weight: bold; color: white; margin: 0; }
    .sub-title { font-size: 13px; color: #64748b; margin-top: -5px; }

    /* 4. ปรับแต่งตารางให้ดูสะอาด */
    .stDataFrame { background: #1e293b; border-radius: 8px; }

    /* Credit */
    .credit { position: fixed; bottom: 8px; right: 20px; color: #475569; font-size: 10px; z-index: 1000; }
    hr { border-top: 1px solid #1e293b; margin: 0.8rem 0 !important; }
    </style>
    <div class="credit">produced by AE-IET [SBU]</div>
    """, unsafe_allow_html=True)

# --- 🛠️ DATABASE CONNECTION ---
def get_db_connection():
    db_path = os.path.join(os.path.dirname(__file__), 'data', 'ghg_data.db')
    return sqlite3.connect(db_path) if os.path.exists(db_path) else None

METRIC_MAP = {"คาร์บอนไดออกไซด์ (CO₂)": "co2", "มีเทน (CH₄)": "ch4", "ไนโตรเจน (NO₂)": "no2", "อุณหภูมิ (Temp)": "temp"}
REGION_MAP = {"ภาคเหนือ": "North", "ภาคกลาง": "Central", "ภาคใต้": "South", "ภาคอีสาน": "Northeast", "ภาคตะวันออก": "East", "ภาคตะวันตก": "West"}
COORDS = {"North": [18.78, 98.98], "Central": [13.75, 100.50], "South": [7.88, 98.39], "Northeast": [14.97, 102.10], "East": [12.92, 100.88], "West": [13.52, 99.81]}

# --- 🔝 HEADER: โลโก้และชื่ออยู่ฝั่งซ้าย / ตัวเลือกอยู่ฝั่งขวา ---
col_h1, col_h2 = st.columns([2, 1])
with col_h1:
    l_c, t_c = st.columns([0.4, 4])
    with l_c: st.image("https://upload.wikimedia.org/wikipedia/th/thumb/a/a2/Southeast_Bangkok_University_Logo.png/200px-Southeast_Bangkok_University_Logo.png", width=60)
    with t_c:
        st.markdown('<p class="main-title">Dashboard “Tracking GHGs Emission”</p>', unsafe_allow_html=True)
        st.markdown('<p class="sub-title">ระบบติดตามมลพิษรายชั่วโมงโดย AE-IET [SBU]</p>', unsafe_allow_html=True)

with col_h2:
    s1, s2 = st.columns(2)
    with s1: s_region = REGION_MAP[st.selectbox("📍 ภูมิภาค:", list(REGION_MAP.keys()), index=1)]
    with s2: 
        s_thai_metric = st.selectbox("📊 ดัชนี:", list(METRIC_MAP.keys()), index=0)
        s_metric = METRIC_MAP[s_thai_metric]

st.markdown("---")

# --- 📊 DATA LOGIC ---
conn = get_db_connection()
if conn:
    try:
        latest = pd.read_sql(f"SELECT * FROM ghg_logs WHERE region='{s_region}' ORDER BY timestamp DESC LIMIT 1", conn).iloc[0]
        history = pd.read_sql(f"SELECT * FROM ghg_logs WHERE region='{s_region}' ORDER BY timestamp DESC LIMIT 15", conn)
        all_data = pd.read_sql("SELECT region, MAX(co2) as co2, MAX(ch4) as ch4, MAX(no2) as no2, MAX(temp) as temp FROM ghg_logs GROUP BY region", conn)
        conn.close()

        # 1. Metric Cards (ย้ายขึ้นมาให้เห็นชัดทันที)
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("CO₂ Level", f"{int(latest['co2'])} ppm")
        m2.metric("Methane (CH₄)", f"{latest['ch4']:.1f} ppb")
        m3.metric("Nitrogen (NO₂)", f"{latest['no2']:.1f} ppb")
        m4.metric("Temperature", f"{int(latest['temp'])}°C")

        st.write("") 

        # 2. MAIN LAYOUT: [ซ้าย: แผนที่] [ขวา: กราฟ + อันดับ]
        col_map, col_data = st.columns([1.1, 1])
        
        with col_map:
            st.markdown("##### 🗺️ แผนที่พยากรณ์โครงข่าย (2D View)")
            all_data['lat'] = all_data['region'].map(lambda x: COORDS[x][0]); all_data['lon'] = all_data['region'].map(lambda x: COORDS[x][1])
            # ใช้ map_style เป็น "dark" เพื่อแยกสีจากพื้นหลังแอป
            st.pydeck_chart(pdk.Deck(
                map_style="mapbox://styles/mapbox/dark-v10", 
                initial_view_state=pdk.ViewState(latitude=13.8, longitude=101.0, zoom=5.1, pitch=0),
                layers=[pdk.Layer("ScatterplotLayer", all_data, get_position="[lon, lat]", get_color="[34, 211, 238, 180]", get_radius=45000)],
                height=450
            ))

        with col_data:
            # กราฟแนวโน้ม (ลดขนาดลงเพื่อให้เห็นตารางด้านล่างครบ)
            st.markdown(f"##### 📈 แนวโน้ม {s_thai_metric.split(' (')[0]}")
            history['timestamp'] = pd.to_datetime(history['timestamp'])
            fig = px.line(history.sort_values('timestamp'), x='timestamp', y=s_metric, height=220, color_discrete_sequence=['#22d3ee'])
            fig.update_layout(margin=dict(l=0, r=0, t=10, b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_size=10)
            st.plotly_chart(fig, use_container_width=True)
            
            # ตารางอันดับสูงสุด
            st.markdown(f"##### 🏆 อันดับค่ามลพิษสูงสุด")
            df_rank = all_data.sort_values(by=s_metric, ascending=False)
            inv_m = {v: k for k, v in REGION_MAP.items()}
            df_rank['ภูมิภาค'] = df_rank['region'].map(inv_m)
            st.dataframe(df_rank[['ภูมิภาค', s_metric]], hide_index=True, use_container_width=True, height=160)
            
    except: st.info("🔄 กำลังอัปเดตข้อมูล...")
else: st.error("⚠️ ไม่พบฐานข้อมูลระบบ")
