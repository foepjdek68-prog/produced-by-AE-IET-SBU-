import streamlit as st
import pandas as pd
import plotly.express as px
import pydeck as pdk
import sqlite3
import os

# 1. Config: บีบพื้นที่ให้แน่นที่สุด
st.set_page_config(page_title="SBU MONITORING", layout="wide", initial_sidebar_state="collapsed")

# --- 🎨 2. CSS: บีบกรอบ UI + ปรับตำแหน่งโลโก้ใหม่ ---
st.markdown("""
    <style>
    /* บีบ Padding และซ่อน Scrollbar สำหรับ Desktop */
    .block-container { padding: 0.5rem 1rem !important; max-height: 100vh; overflow: hidden; }
    .stApp { background-color: #020617; }

    /* บล็อกการพิมพ์ใน Selectbox */
    div[data-baseweb="select"] input { caret-color: transparent !important; pointer-events: none !important; }
    
    /* บีบ Metrics ให้เล็กและเตี้ย */
    div[data-testid="stMetric"] { 
        background: rgba(30, 41, 59, 0.4); 
        padding: 8px !important; 
        border-radius: 8px; 
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    div[data-testid="stMetricValue"] { font-size: 20px !important; }
    
    /* ปรับตารางให้ตัวหนังสือเล็กลงและประหยัดที่ */
    .stDataFrame div { font-size: 11px !important; }

    /* เครดิตมุมขวาล่าง (ปรับให้อยู่บนสุดของ Layer และหลบมุม) */
    .footer-credit {
        position: fixed; bottom: 10px; right: 10px;
        background: rgba(15, 23, 42, 0.95);
        padding: 5px 10px; border-radius: 10px;
        border: 1px solid rgba(34, 211, 238, 0.4);
        z-index: 10000; /* ดันขึ้นมาให้อยู่เหนือตาราง */
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

# --- 🛠️ 3. DATABASE ---
def get_db_connection():
    db_path = os.path.join(os.path.dirname(__file__), 'data', 'ghg_data.db')
    return sqlite3.connect(db_path) if os.path.exists(db_path) else None

REGION_MAP = {"ภาคเหนือ": "North", "ภาคกลาง": "Central", "ภาคใต้": "South", "ภาคอีสาน": "Northeast", "ภาคตะวันออก": "East", "ภาคตะวันตก": "West"}
METRIC_MAP = {"CO₂": "co2", "CH₄": "ch4", "NO₂": "no2", "Temp": "temp"}
COORDS = {"North": [18.78, 98.98], "Central": [13.75, 100.50], "South": [7.88, 98.39], "Northeast": [14.97, 102.10], "East": [12.92, 100.88], "West": [13.52, 99.81]}

# --- 🔝 4. HEADER (Compact) ---
h1, h2, h3 = st.columns([2.5, 1, 1])
with h1: st.markdown("<h3 style='color:white; margin:0;'>GHGs MONITORING SYSTEM</h3>", unsafe_allow_html=True)
with h2: s_region_name = st.selectbox("R", list(REGION_MAP.keys()), index=1, label_visibility="collapsed")
with h3: s_metric_name = st.selectbox("M", list(METRIC_MAP.keys()), index=0, label_visibility="collapsed")

s_region = REGION_MAP[s_region_name]
s_metric = METRIC_MAP[s_metric_name]

# --- 📊 5. MAIN ---
conn = get_db_connection()
if conn:
    try:
        latest = pd.read_sql(f"SELECT * FROM ghg_logs WHERE region='{s_region}' ORDER BY timestamp DESC LIMIT 1", conn).iloc[0]
        history = pd.read_sql(f"SELECT * FROM ghg_logs WHERE region='{s_region}' ORDER BY timestamp DESC LIMIT 15", conn)
        all_data = pd.read_sql("SELECT region, MAX(co2) as co2, MAX(ch4) as ch4, MAX(no2) as no2, MAX(temp) as temp FROM ghg_logs GROUP BY region", conn)
        conn.close()

        # Metrics Row
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("CO₂ (ppm)", f"{int(latest['co2'])}")
        m2.metric("CH₄ (ppb)", f"{latest['ch4']:.1f}")
        m3.metric("NO₂ (ppb)", f"{latest['no2']:.1f}")
        m4.metric("TEMP (°C)", f"{int(latest['temp'])}")

        st.markdown("<div style='margin: 5px 0;'></div>", unsafe_allow_html=True)

        # Main Layout (ปรับสัดส่วนใหม่เพื่อบีบฝั่งขวา)
        col_left, col_right = st.columns([2, 0.8]) # บีบ col_right ให้แคบลง

        with col_left:
            # แผนที่ (สเกลมาตรฐาน)
            all_data['lat'] = all_data['region'].map(lambda x: COORDS[x][0])
            all_data['lon'] = all_data['region'].map(lambda x: COORDS[x][1])
            st.pydeck_chart(pdk.Deck(
                map_style=None,
                initial_view_state=pdk.ViewState(latitude=13.2, longitude=101.0, zoom=5.1),
                layers=[pdk.Layer("ScatterplotLayer", all_data, get_position="[lon, lat]", get_color="[34, 211, 238, 200]", get_radius=45000)],
            ), use_container_width=True)

        with col_right:
            # กราฟ (ลดความสูงลงอีก)
            history['timestamp'] = pd.to_datetime(history['timestamp'])
            fig = px.area(history.sort_values('timestamp'), x='timestamp', y=s_metric, height=180)
            fig.update_layout(margin=dict(l=0, r=0, t=10, b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color="#94a3b8", size=8), xaxis=dict(showgrid=False), yaxis=dict(showgrid=False))
            fig.update_traces(line_color='#22d3ee', fillcolor='rgba(34, 211, 238, 0.05)')
            st.plotly_chart(fig, use_container_width=True)

            # ตาราง (บีบแคบและสั้นลงเพื่อเปิดที่ให้โลโก้)
            st.markdown("<p style='font-size:12px; font-weight:bold; color:#22d3ee; margin:5px 0;'>RANKING</p>", unsafe_allow_html=True)
            df_rank = all_data.sort_values(by=s_metric, ascending=False)
            df_rank['Area'] = df_rank['region'].map({v: k[4:] for k, v in REGION_MAP.items()}) # ตัดคำว่า "ภาค" ออกเพื่อประหยัดที่
            st.dataframe(df_rank[['Area', s_metric]], hide_index=True, use_container_width=True, height=130)

    except Exception as e:
        st.error("Data Syncing...")
else:
    st.error("Database Error")
