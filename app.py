import streamlit as st
import pandas as pd
import plotly.express as px
import pydeck as pdk
import sqlite3
import os

# 1. ตั้งค่าหน้าจอแบบ Wide และซ่อน Sidebar
st.set_page_config(page_title="SBU GHGs Tracking", layout="wide", initial_sidebar_state="collapsed")

# --- 🎨 CSS: ปรับโฉมใหม่ธีม Charcoal & Electric Blue ---
st.markdown("""
    <style>
    /* พื้นหลังหลักของแอป */
    .stApp { background-color: #111827; }
    .block-container { padding: 1rem 2.5rem !important; }

    /* ตกแต่ง Metric Cards ให้ดูหรูหรา */
    div[data-testid="stMetric"] { 
        background: #1f2937; 
        padding: 15px; 
        border-radius: 12px; 
        border-left: 5px solid #38bdf8;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
    }
    [data-testid="stMetricValue"] { font-size: 24px !important; color: #38bdf8 !important; font-weight: bold; }
    [data-testid="stMetricLabel"] { font-size: 13px !important; color: #9ca3af !important; }

    /* ส่วนหัวโปรเจกต์ */
    .main-title { font-size: 26px; font-weight: 800; color: #f9fafb; margin: 0; letter-spacing: 1px; }
    .sub-title { font-size: 13px; color: #6b7280; margin-top: -5px; font-weight: 500; }
    
    /* เส้นคั่น */
    hr { border-top: 1px solid #374151; margin: 1rem 0 !important; }

    /* Credit Footer */
    .credit { position: fixed; bottom: 10px; right: 25px; color: #4b5563; font-size: 10px; z-index: 1000; font-weight: 600; }
    </style>
    <div class="credit">produced by AE-IET [SBU]</div>
    """, unsafe_allow_html=True)

# --- 🛠️ ฟังก์ชันฐานข้อมูล ---
def get_db_connection():
    db_path = os.path.join(os.path.dirname(__file__), 'data', 'ghg_data.db')
    return sqlite3.connect(db_path) if os.path.exists(db_path) else None

METRIC_MAP = {"คาร์บอนไดออกไซด์ (CO₂)": "co2", "มีเทน (CH₄)": "ch4", "ไนโตรเจน (NO₂)": "no2", "อุณหภูมิ (Temp)": "temp"}
REGION_MAP = {"ภาคเหนือ": "North", "ภาคกลาง": "Central", "ภาคใต้": "South", "ภาคอีสาน": "Northeast", "ภาคตะวันออก": "East", "ภาคตะวันตก": "West"}
COORDS = {"North": [18.78, 98.98], "Central": [13.75, 100.50], "South": [7.88, 98.39], "Northeast": [14.97, 102.10], "East": [12.92, 100.88], "West": [13.52, 99.81]}

# --- 🔝 HEADER: จัดระเบียบใหม่ให้โลโก้เด่น ---
h_col1, h_col2 = st.columns([2.2, 1.2])

with h_col1:
    l_c, t_c = st.columns([0.4, 4])
    with l_c: 
        st.image("https://upload.wikimedia.org/wikipedia/th/thumb/a/a2/Southeast_Bangkok_University_Logo.png/200px-Southeast_Bangkok_University_Logo.png", width=65)
    with t_c:
        st.markdown('<p class="main-title">TRACKING GHGs EMISSION SYSTEM</p>', unsafe_allow_html=True)
        st.markdown('<p class="sub-title">Real-time Environmental Monitoring by AE-IET [SBU]</p>', unsafe_allow_html=True)

with h_col2:
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

        # 1. แถบ Metrics (เน้นความชัดเจน)
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("CO₂ CONCENTRATION", f"{int(latest['co2'])} ppm")
        m2.metric("METHANE (CH₄)", f"{latest['ch4']:.1f} ppb")
        m3.metric("NITROUS OXIDE (NO₂)", f"{latest['no2']:.1f} ppb")
        m4.metric("TEMPERATURE", f"{int(latest['temp'])}°C")

        st.write("") 

        # 2. MAIN VISUAL: [ซ้าย: แผนที่สีกรมท่า] [ขวา: กราฟ + อันดับ]
        col_map, col_right = st.columns([1.2, 1])
        
        with col_map:
            st.markdown("##### 🗺️ แผนที่พยากรณ์โครงข่าย (Spatial 2D View)")
            all_data['lat'] = all_data['region'].map(lambda x: COORDS[x][0]); all_data['lon'] = all_data['region'].map(lambda x: COORDS[x][1])
            
            # บังคับใช้สีพื้นหลังแผนที่เข้มพิเศษเพื่อแก้บัค Mapbox
            st.pydeck_chart(pdk.Deck(
                map_style="mapbox://styles/mapbox/dark-v10", 
                initial_view_state=pdk.ViewState(latitude=13.5, longitude=101.0, zoom=5.1, pitch=0),
                layers=[
                    pdk.Layer(
                        "ScatterplotLayer", 
                        all_data, 
                        get_position="[lon, lat]", 
                        get_color="[56, 189, 248, 200]", 
                        get_radius=50000,
                        pickable=True
                    )
                ],
                height=520
            ))

        with col_right:
            # กราฟแนวโน้ม (ปรับเส้นให้หนาและชัดขึ้น)
            st.markdown(f"##### 📈 แนวโน้ม {s_thai_metric.split(' (')[0]}")
            history['timestamp'] = pd.to_datetime(history['timestamp'])
            fig = px.line(history.sort_values('timestamp'), x='timestamp', y=s_metric, height=250, color_discrete_sequence=['#38bdf8'])
            fig.update_layout(
                margin=dict(l=0, r=0, t=10, b=0),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color="#9ca3af", size=10),
                xaxis=dict(showgrid=False),
                yaxis=dict(gridcolor="#374151")
            )
            fig.update_traces(line=dict(width=3))
            st.plotly_chart(fig, use_container_width=True)
            
            # ตารางอันดับสูงสุด
            st.markdown(f"##### 🏆 อันดับภูมิภาคค่ามลพิษสูงสุด")
            df_rank = all_data.sort_values(by=s_metric, ascending=False)
            inv_m = {v: k for k, v in REGION_MAP.items()}
            df_rank['ภูมิภาค'] = df_rank['region'].map(inv_m)
            st.dataframe(
                df_rank[['ภูมิภาค', s_metric]].rename(columns={s_metric: 'ค่าที่วัดได้'}),
                hide_index=True, 
                use_container_width=True, 
                height=200
            )
            
    except Exception as e: 
        st.info("🔄 กำลังซิงค์ข้อมูลโครงข่ายสถานี...")
else: 
    st.error("⚠️ ไม่สามารถเชื่อมต่อฐานข้อมูล ghg_data.db ได้")
