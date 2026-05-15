import streamlit as st
import pandas as pd
import plotly.express as px
import pydeck as pdk
import sqlite3
import os

# 1. Config: บีบระยะขอบให้เหลือน้อยที่สุดเพื่อให้อยู่ในหน้าเดียว
st.set_page_config(page_title="SBU MONITORING", layout="wide", initial_sidebar_state="collapsed")

# --- 🎨 2. CSS: บล็อกการพิมพ์ + บีบสัดส่วน UI ---
st.markdown("""
    <style>
    /* บีบ Padding หลักของแอป */
    .block-container { padding: 0.5rem 1rem !important; max-height: 100vh; overflow: hidden; }
    .stApp { background-color: #020617; }

    /* บล็อกการพิมพ์ใน Selectbox ชัวร์ๆ */
    div[data-baseweb="select"] input { caret-color: transparent !important; pointer-events: none !important; }
    
    /* ปรับแต่งความสูงของกล่องและระยะห่าง (Compact Mode) */
    div[data-testid="stMetric"] { 
        background: rgba(30, 41, 59, 0.4); 
        padding: 10px !important; 
        border-radius: 8px; 
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    div[data-testid="stMetricValue"] { font-size: 22px !important; }
    
    /* ซ่อน Footer Streamlit */
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* เครดิตมุมขวาล่าง */
    .footer-credit {
        position: fixed; bottom: 10px; right: 10px;
        background: rgba(15, 23, 42, 0.9);
        padding: 8px 12px; border-radius: 10px;
        border: 1px solid rgba(34, 211, 238, 0.3);
        display: flex; align-items: center; gap: 10px; z-index: 9999;
    }
    .footer-credit img { width: 100px; height: auto; }
    </style>

    <div class="footer-credit">
        <a href="https://www.southeast.ac.th/about-us/" target="_blank">
            <img src="https://www.southeast.ac.th/wp-content/uploads/2023/11/logo-main2.png" 
                 onerror="this.src='https://upload.wikimedia.org/wikipedia/th/thumb/a/a2/Southeast_Bangkok_University_Logo.png/200px-Southeast_Bangkok_University_Logo.png'">
        </a>
    </div>
    """, unsafe_allow_html=True)

# --- 🛠️ 3. DATABASE LOGIC ---
def get_db_connection():
    db_path = os.path.join(os.path.dirname(__file__), 'data', 'ghg_data.db')
    return sqlite3.connect(db_path) if os.path.exists(db_path) else None

REGION_MAP = {"ภาคเหนือ": "North", "ภาคกลาง": "Central", "ภาคใต้": "South", "ภาคอีสาน": "Northeast", "ภาคตะวันออก": "East", "ภาคตะวันตก": "West"}
METRIC_MAP = {"CO₂": "co2", "CH₄": "ch4", "NO₂": "no2", "Temp": "temp"}
COORDS = {"North": [18.78, 98.98], "Central": [13.75, 100.50], "South": [7.88, 98.39], "Northeast": [14.97, 102.10], "East": [12.92, 100.88], "West": [13.52, 99.81]}

# --- 🔝 4. HEADER & FILTERS (บรรทัดเดียวจบ) ---
f1, f2, f3 = st.columns([2, 1, 1])
with f1: st.markdown("<h2 style='color:white; margin:0; font-size:24px;'>GHGs REAL-TIME MONITORING</h2>", unsafe_allow_html=True)
with f2: s_region_name = st.selectbox("Region", list(REGION_MAP.keys()), label_visibility="collapsed")
with f3: s_metric_name = st.selectbox("Metric", list(METRIC_MAP.keys()), label_visibility="collapsed")

s_region = REGION_MAP[s_region_name]
s_metric = METRIC_MAP[s_metric_name]

# --- 📊 5. CONTENT AREA ---
conn = get_db_connection()
if conn:
    try:
        latest = pd.read_sql(f"SELECT * FROM ghg_logs WHERE region='{s_region}' ORDER BY timestamp DESC LIMIT 1", conn).iloc[0]
        history = pd.read_sql(f"SELECT * FROM ghg_logs WHERE region='{s_region}' ORDER BY timestamp DESC LIMIT 20", conn)
        all_data = pd.read_sql("SELECT region, MAX(co2) as co2, MAX(ch4) as ch4, MAX(no2) as no2, MAX(temp) as temp FROM ghg_logs GROUP BY region", conn)
        conn.close()

        # Metrics Row
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("CO₂ (ppm)", f"{int(latest['co2'])}")
        m2.metric("CH₄ (ppb)", f"{latest['ch4']:.1f}")
        m3.metric("NO₂ (ppb)", f"{latest['no2']:.1f}")
        m4.metric("TEMP (°C)", f"{int(latest['temp'])}")

        st.markdown("<div style='margin: 10px 0;'></div>", unsafe_allow_html=True)

        # Main Visualization (1 หน้าจอเดสก์ท็อป)
        col_left, col_right = st.columns([1.6, 1])

        with col_left:
            # แก้บัคแผนที่: ใช้การตั้งค่าที่เบาและเสถียรที่สุด
            all_data['lat'] = all_data['region'].map(lambda x: COORDS[x][0])
            all_data['lon'] = all_data['region'].map(lambda x: COORDS[x][1])
            
            st.pydeck_chart(pdk.Deck(
                map_style=None, # เลิกพึ่งพา Style ภายนอกเพื่อกันจอดำ
                initial_view_state=pdk.ViewState(latitude=13.5, longitude=101.0, zoom=5.2, pitch=0),
                layers=[
                    pdk.Layer(
                        "ScatterplotLayer", all_data,
                        get_position="[lon, lat]",
                        get_color="[34, 211, 238, 200]",
                        get_radius=50000,
                    )
                ],
            ), use_container_width=True)

        with col_right:
            # กราฟแนวโน้ม (บีบความสูงให้พอดีหน้าเดียว)
            history['timestamp'] = pd.to_datetime(history['timestamp'])
            fig = px.area(history.sort_values('timestamp'), x='timestamp', y=s_metric, height=220)
            fig.update_layout(
                margin=dict(l=0, r=0, t=10, b=0),
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color="#94a3b8", size=9),
                xaxis=dict(showgrid=False), yaxis=dict(gridcolor="rgba(255,255,255,0.05)")
            )
            fig.update_traces(line_color='#22d3ee', fillcolor='rgba(34, 211, 238, 0.1)')
            st.plotly_chart(fig, use_container_width=True)

            # ตารางจัดอันดับ (Compact Table)
            df_rank = all_data.sort_values(by=s_metric, ascending=False)
            df_rank['ภูมิภาค'] = df_rank['region'].map({v: k for k, v in REGION_MAP.items()})
            st.dataframe(df_rank[['ภูมิภาค', s_metric]], hide_index=True, use_container_width=True, height=160)

    except Exception as e:
        st.error(f"Syncing Error...")
else:
    st.error("Database connection failed")
