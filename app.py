import streamlit as st
import pandas as pd
import plotly.express as px
import pydeck as pdk
import sqlite3
import os

# 1. ตั้งค่าหน้าจอ (บีบระยะห่างให้เหลือน้อยที่สุด)
st.set_page_config(page_title="GHGs Monitoring SBU", layout="wide", initial_sidebar_state="collapsed")

# --- 🎨 2. CSS: ลดสเกล UI และบล็อกการพิมพ์ใน Selectbox ---
st.markdown("""
    <style>
    /* บีบพื้นที่หน้าจอให้แน่น */
    .block-container { padding: 0.5rem 1rem !important; }
    .stApp { background-color: #020617; color: #f8fafc; }

    /* ลดสเกลตัวอักษรและหัวข้อ */
    h1 { font-size: 18px !important; font-weight: 800; margin-bottom: -5px !important; }
    p { font-size: 10px !important; color: #64748b; margin-bottom: 5px !important; }
    h5 { font-size: 12px !important; margin-bottom: 5px !important; color: #22d3ee; }

    /* ปรับแต่ง Metric Cards ให้เล็กและเตี้ยลง */
    div[data-testid="stMetric"] { 
        background: rgba(30, 41, 59, 0.4); 
        padding: 5px 10px !important; 
        border-radius: 8px; 
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    div[data-testid="stMetricValue"] { font-size: 18px !important; }
    div[data-testid="stMetricLabel"] { font-size: 10px !important; }

    /* บล็อกการพิมพ์ใน Selectbox (ทำให้เป็น Read-only) */
    div[data-baseweb="select"] input {
        pointer-events: none; /* ห้ามคลิกเพื่อพิมพ์ */
        caret-color: transparent; /* ซ่อนตัวกะพริบ */
    }
    .stSelectbox label { font-size: 11px !important; margin-bottom: 0px !important; }

    /* เครดิตลอยมุมขวาล่าง (จิ๋วแต่แจ๋ว) */
    .footer-credit {
        position: fixed; bottom: 10px; right: 10px;
        background: rgba(15, 23, 42, 0.95);
        padding: 5px 10px; border-radius: 10px;
        border: 1px solid rgba(34, 211, 238, 0.3);
        display: flex; align-items: center; gap: 8px; z-index: 9999;
    }
    .footer-credit img { width: 80px; height: auto; }
    .credit-text { border-left: 1px solid rgba(255,255,255,0.1); padding-left: 8px; font-size: 8px; color: #94a3b8; }
    </style>

    <div class="footer-credit">
        <a href="https://www.southeast.ac.th/about-us/" target="_blank" style="text-decoration: none; display: flex; align-items: center; gap: 8px;">
            <img src="https://www.southeast.ac.th/wp-content/uploads/2023/11/logo-main2.png" 
                 onerror="this.src='https://upload.wikimedia.org/wikipedia/th/thumb/a/a2/Southeast_Bangkok_University_Logo.png/200px-Southeast_Bangkok_University_Logo.png'">
            <div class="credit-text">
                <b style="color:#fff;">AE-IET</b><br>
                <span>SBU Monitoring</span>
            </div>
        </a>
    </div>
    """, unsafe_allow_html=True)

# --- 🛠️ 3. DATABASE CONNECTION ---
def get_db_connection():
    db_path = os.path.join(os.path.dirname(__file__), 'data', 'ghg_data.db')
    return sqlite3.connect(db_path) if os.path.exists(db_path) else None

REGION_MAP = {"ภาคเหนือ": "North", "ภาคกลาง": "Central", "ภาคใต้": "South", "ภาคอีสาน": "Northeast", "ภาคตะวันออก": "East", "ภาคตะวันตก": "West"}
METRIC_MAP = {"คาร์บอนไดออกไซด์ (CO₂)": "co2", "มีเทน (CH₄)": "ch4", "ไนโตรเจน (NO₂)": "no2", "อุณหภูมิ (Temp)": "temp"}
COORDS = {"North": [18.78, 98.98], "Central": [13.75, 100.50], "South": [7.88, 98.39], "Northeast": [14.97, 102.10], "East": [12.92, 100.88], "West": [13.52, 99.81]}

# --- 🔝 4. HEADER ---
st.markdown("<h1>TRACKING GHGs EMISSION</h1>", unsafe_allow_html=True)
st.markdown("<p>Real-time Monitoring System [SBU]</p>", unsafe_allow_html=True)

# ส่วน Filter (บีบลง 0.8x)
c_sel1, c_sel2 = st.columns(2)
with c_sel1: s_region_name = st.selectbox("📍 ภูมิภาค:", list(REGION_MAP.keys()), index=1)
with c_sel2: s_metric_name = st.selectbox("📊 ดัชนี:", list(METRIC_MAP.keys()), index=0)

s_region = REGION_MAP[s_region_name]
s_metric = METRIC_MAP[s_metric_name]

# --- 📊 5. CONTENT ---
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

        # ส่วนแสดงผลหลัก
        col_map, col_right = st.columns([1.7, 1])

        with col_map:
            st.markdown("##### 🗺️ 2D STATION NETWORK")
            all_data['lat'] = all_data['region'].map(lambda x: COORDS[x][0])
            all_data['lon'] = all_data['region'].map(lambda x: COORDS[x][1])
            
            st.pydeck_chart(pdk.Deck(
                map_style="mapbox://styles/mapbox/dark-v10", 
                initial_view_state=pdk.ViewState(latitude=13.5, longitude=100.8, zoom=5.1),
                layers=[
                    pdk.Layer(
                        "ScatterplotLayer", all_data,
                        get_position="[lon, lat]",
                        get_color="[34, 211, 238, 200]",
                        get_radius=42000,
                    )
                ],
            ))

        with col_right:
            # กราฟ (เน้นประหยัดพื้นที่)
            st.markdown(f"##### 📈 TREND: {s_metric_name.split(' (')[0]}")
            history['timestamp'] = pd.to_datetime(history['timestamp'])
            fig = px.area(history.sort_values('timestamp'), x='timestamp', y=s_metric, height=180)
            fig.update_layout(
                margin=dict(l=0, r=0, t=5, b=0),
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color="#94a3b8", size=8),
                xaxis=dict(showgrid=False), yaxis=dict(gridcolor="rgba(255,255,255,0.05)")
            )
            fig.update_traces(line_color='#22d3ee', fillcolor='rgba(34, 211, 238, 0.05)')
            st.plotly_chart(fig, use_container_width=True)

            # ตาราง
            st.markdown("##### 🏆 RANKING")
            df_rank = all_data.sort_values(by=s_metric, ascending=False)
            df_rank['ภูมิภาค'] = df_rank['region'].map({v: k for k, v in REGION_MAP.items()})
            st.dataframe(df_rank[['ภูมิภาค', s_metric]], hide_index=True, use_container_width=True, height=130)

    except Exception as e:
        st.error(f"Error: {e}")
else:
    st.error("Database connection failed")
