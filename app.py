import streamlit as st
import pandas as pd
import plotly.express as px
import pydeck as pdk
import sqlite3
import os

# 1. บีบทุกอย่างให้อยู่ในหน้าเดียว (Desktop Mode)
st.set_page_config(page_title="SBU MONITORING", layout="wide", initial_sidebar_state="collapsed")

# --- 🎨 2. CSS: จัดการ Layout ให้สมส่วนและบล็อกการพิมพ์ ---
st.markdown("""
    <style>
    /* บีบหน้าจอให้พอดี 100% ไม่ต้องเลื่อน */
    .block-container { padding: 0.8rem 1.2rem !important; max-height: 100vh; overflow: hidden; }
    .stApp { background-color: #020617; }

    /* บล็อกการพิมพ์ในช่องเลือก */
    div[data-baseweb="select"] input { caret-color: transparent !important; pointer-events: none !important; }
    
    /* ตกแต่ง Metric Cards ให้ดูทางการและประหยัดที่ */
    div[data-testid="stMetric"] { 
        background: rgba(30, 41, 59, 0.4); 
        padding: 10px !important; 
        border-radius: 8px; 
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    div[data-testid="stMetricValue"] { font-size: 20px !important; color: #22d3ee !important; }

    /* โลโก้ SBU มุมขวาล่าง */
    .footer-credit {
        position: fixed; bottom: 15px; right: 15px;
        background: rgba(15, 23, 42, 0.9);
        padding: 8px 12px; border-radius: 12px;
        border: 1px solid rgba(34, 211, 238, 0.4);
        z-index: 10000;
    }
    .footer-credit img { width: 110px; height: auto; }
    
    /* ปรับตารางให้แคบและดูสะอาด */
    .stDataFrame { border: none !important; }
    </style>

    <div class="footer-credit">
        <a href="https://www.southeast.ac.th/about-us/" target="_blank">
            <img src="https://www.southeast.ac.th/wp-content/uploads/2023/11/logo-main2.png" 
                 onerror="this.src='https://upload.wikimedia.org/wikipedia/th/thumb/a/a2/Southeast_Bangkok_University_Logo.png/200px-Southeast_Bangkok_University_Logo.png'">
        </a>
    </div>
    """, unsafe_allow_html=True)

# --- 🛠️ 3. DATABASE ---
def get_db_connection():
    db_path = os.path.join(os.path.dirname(__file__), 'data', 'ghg_data.db')
    return sqlite3.connect(db_path) if os.path.exists(db_path) else None

REGION_MAP = {"ภาคเหนือ": "North", "ภาคกลาง": "Central", "ภาคใต้": "South", "ภาคอีสาน": "Northeast", "ภาคตะวันออก": "East", "ภาคตะวันตก": "West"}
METRIC_MAP = {"CO₂": "co2", "CH₄": "ch4", "NO₂": "no2", "Temp": "temp"}
COORDS = {"North": [18.78, 98.98], "Central": [13.75, 100.50], "South": [7.88, 98.39], "Northeast": [14.97, 102.10], "East": [12.92, 100.88], "West": [13.52, 99.81]}

# --- 🔝 4. HEADER & FILTERS (กลับมาแสดงด้านบนแบบสมส่วน) ---
# จัดเรียง: ชื่อระบบ (60%) | เลือกภูมิภาค (20%) | เลือกดัชนี (20%)
col_h1, col_h2, col_h3 = st.columns([3, 1, 1])
with col_h1: 
    st.markdown("<h2 style='color:white; margin:0; font-size:24px;'>GHGs MONITORING SYSTEM</h2>", unsafe_allow_html=True)
with col_h2: 
    s_region_name = st.selectbox("Region", list(REGION_MAP.keys()), index=1, label_visibility="collapsed")
with col_h3: 
    s_metric_name = st.selectbox("Metric", list(METRIC_MAP.keys()), index=0, label_visibility="collapsed")

s_region = REGION_MAP[s_region_name]
s_metric = METRIC_MAP[s_metric_name]

# --- 📊 5. MAIN CONTENT ---
conn = get_db_connection()
if conn:
    try:
        latest = pd.read_sql(f"SELECT * FROM ghg_logs WHERE region='{s_region}' ORDER BY timestamp DESC LIMIT 1", conn).iloc[0]
        history = pd.read_sql(f"SELECT * FROM ghg_logs WHERE region='{s_region}' ORDER BY timestamp DESC LIMIT 20", conn)
        all_data = pd.read_sql("SELECT region, MAX(co2) as co2, MAX(ch4) as ch4, MAX(no2) as no2, MAX(temp) as temp FROM ghg_logs GROUP BY region", conn)
        conn.close()

        # Metrics Row (แสดงค่าปัจจุบัน 4 ตัว)
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("CO₂ (ppm)", f"{int(latest['co2'])}")
        m2.metric("CH₄ (ppb)", f"{latest['ch4']:.1f}")
        m3.metric("NO₂ (ppb)", f"{latest['no2']:.1f}")
        m4.metric("TEMP (°C)", f"{int(latest['temp'])}")

        st.markdown("<div style='margin: 10px 0;'></div>", unsafe_allow_html=True)

        # Main Layout: [แผนที่ (65%) | กราฟและตาราง (35%)]
        col_left, col_right = st.columns([2, 1])

        with col_left:
            # แผนที่: ปรับขนาดให้สมส่วนกับหน้าจอเดสก์ท็อป
            all_data['lat'] = all_data['region'].map(lambda x: COORDS[x][0])
            all_data['lon'] = all_data['region'].map(lambda x: COORDS[x][1])
            st.pydeck_chart(pdk.Deck(
                map_style=None,
                initial_view_state=pdk.ViewState(latitude=13.5, longitude=100.8, zoom=5.2),
                layers=[
                    pdk.Layer(
                        "ScatterplotLayer", all_data,
                        get_position="[lon, lat]",
                        get_color="[34, 211, 238, 200]",
                        get_radius=45000,
                    )
                ],
            ), use_container_width=True)

        with col_right:
            # กราฟแนวโน้ม (Compact Area Chart)
            history['timestamp'] = pd.to_datetime(history['timestamp'])
            fig = px.area(history.sort_values('timestamp'), x='timestamp', y=s_metric, height=200)
            fig.update_layout(
                margin=dict(l=0, r=0, t=10, b=0),
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color="#94a3b8", size=9),
                xaxis=dict(showgrid=False), yaxis=dict(gridcolor="rgba(255,255,255,0.05)")
            )
            fig.update_traces(line_color='#22d3ee', fillcolor='rgba(34, 211, 238, 0.1)')
            st.plotly_chart(fig, use_container_width=True)

            st.markdown("<p style='font-size:12px; color:#22d3ee; font-weight:bold; margin-bottom:5px;'>TOP REGIONS RANKING</p>", unsafe_allow_html=True)
            
            # ตารางอันดับ: บีบให้แคบและพอดีกับคอลัมน์ขวา
            df_rank = all_data.sort_values(by=s_metric, ascending=False)
            df_rank['Region'] = df_rank['region'].map({v: k for k, v in REGION_MAP.items()})
            st.dataframe(df_rank[['Region', s_metric]], hide_index=True, use_container_width=True, height=160)

    except Exception as e:
        st.error("Waiting for data...")
else:
    st.error("Database connection failed.")
