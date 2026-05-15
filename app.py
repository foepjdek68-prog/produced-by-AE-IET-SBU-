import streamlit as st
import pandas as pd
import plotly.express as px
import pydeck as pdk
import sqlite3
import os
from datetime import datetime
import pytz

# 1. Config หน้าจอ
st.set_page_config(page_title="Dashboard Tracking GHGs Emission", layout="wide", initial_sidebar_state="collapsed")

# --- 🎨 2. CSS: ขยับตำแหน่งขึ้นและจัดสมดุล ---
st.markdown("""
    <style>
    /* ลด Padding ด้านบนเพื่อดันทุกอย่างขึ้น */
    .block-container { 
        padding-top: 1rem !important; 
        padding-bottom: 5rem !important; 
    }
    .stApp { background-color: #020617; }

    /* นาฬิกาไทยมุมบนขวา */
    .digital-clock {
        position: absolute; top: -55px; right: 0px;
        color: #22d3ee; font-family: monospace; font-size: 16px;
        font-weight: bold; background: rgba(30, 41, 59, 0.5);
        padding: 4px 12px; border-radius: 5px; border: 1px solid rgba(34, 211, 238, 0.3);
    }

    /* บล็อกการพิมพ์ในช่องเลือก */
    div[data-baseweb="select"] input { caret-color: transparent !important; pointer-events: none !important; }
    
    /* Metrics ขยับขึ้น */
    div[data-testid="stMetric"] { 
        background: rgba(30, 41, 59, 0.4); 
        padding: 8px 12px !important; 
        border-radius: 8px; 
    }

    /* เครดิตและโลโก้ (ขยับขึ้นหนีขอบล่าง) */
    .footer-container {
        position: fixed; bottom: 50px; right: 20px;
        display: flex; flex-direction: column; align-items: flex-end;
        z-index: 10000;
    }
    .footer-container img { width: 85px; height: auto; }
    .produced-by { font-size: 9px; color: #64748b; }

    /* ดันแผนที่และกราฟขึ้น */
    .content-wrapper { margin-top: -10px; }
    </style>
    """, unsafe_allow_html=True)

# --- 🕒 3. เวลาประเทศไทย ---
try:
    tz_th = pytz.timezone('Asia/Bangkok')
    now_th = datetime.now(tz_th).strftime("%H:%M:%S")
    st.markdown(f'<div class="digital-clock">🇹🇭 TH TIME: {now_th}</div>', unsafe_allow_html=True)
except:
    pass

st.markdown(f"""
    <div class="footer-container">
        <img src="https://www.southeast.ac.th/wp-content/uploads/2023/11/logo-main2.png">
        <div class="produced-by">produced by AE-IET [SBU]</div>
    </div>
    """, unsafe_allow_html=True)

# --- 🛠️ 4. DATABASE ---
def get_db_connection():
    db_path = os.path.join(os.path.dirname(__file__), 'data', 'ghg_data.db')
    return sqlite3.connect(db_path) if os.path.exists(db_path) else None

CO2_LBL = "CO₂"
REGION_MAP = {"ภาคเหนือ": "North", "ภาคกลาง": "Central", "ภาคใต้": "South", "ภาคอีสาน": "Northeast", "ภาคตะวันออก": "East", "ภาคตะวันตก": "West"}
METRIC_MAP = {f"{CO2_LBL} (ppm)": "co2", "CH₄ (ppb)": "ch4", "NO₂ (ppb)": "no2", "TEMP (°C)": "temp"}
COORDS = {"North": [18.78, 98.98], "Central": [13.75, 100.50], "South": [7.88, 98.39], "Northeast": [14.97, 102.10], "East": [12.92, 100.88], "West": [13.52, 99.81]}

# --- 🔝 5. HEADER (ยกขึ้น) ---
st.markdown("<h2 style='color:white; margin-bottom:10px; font-size:24px;'>Dashboard “Tracking GHGs Emission”</h2>", unsafe_allow_html=True)

col_h1, col_h2 = st.columns(2)
with col_h1: s_region_name = st.selectbox("Region", list(REGION_MAP.keys()), index=1)
with col_h2: s_metric_name = st.selectbox("Metric", list(METRIC_MAP.keys()), index=0)

s_region = REGION_MAP[s_region_name]
s_metric = METRIC_MAP[s_metric_name]

# --- 📊 6. CONTENT ---
conn = get_db_connection()
if conn:
    try:
        latest = pd.read_sql(f"SELECT * FROM ghg_logs WHERE region='{s_region}' ORDER BY timestamp DESC LIMIT 1", conn).iloc[0]
        history = pd.read_sql(f"SELECT * FROM ghg_logs WHERE region='{s_region}' ORDER BY timestamp DESC LIMIT 24", conn)
        all_data = pd.read_sql("SELECT region, MAX(co2) as co2, MAX(ch4) as ch4, MAX(no2) as no2, MAX(temp) as temp FROM ghg_logs GROUP BY region", conn)
        conn.close()

        # Metrics
        m1, m2, m3, m4 = st.columns(4)
        m1.metric(f"{CO2_LBL}", f"{int(latest['co2'])} ppm")
        m2.metric("CH₄", f"{latest['ch4']:.1f} ppb")
        m3.metric("NO₂", f"{latest['no2']:.1f} ppb")
        m4.metric("TEMP", f"{int(latest['temp'])} °C")

        st.markdown("<div class='content-wrapper'>", unsafe_allow_html=True)
        col_map, col_rank, col_trend = st.columns([0.8, 1.0, 1.2])

        with col_map:
            st.markdown("<p style='font-size:11px; color:#22d3ee; margin-bottom:5px;'>STATION NETWORK</p>", unsafe_allow_html=True)
            all_data['lat'] = all_data['region'].map(lambda x: COORDS[x][0])
            all_data['lon'] = all_data['region'].map(lambda x: COORDS[x][1])
            st.pydeck_chart(pdk.Deck(
                map_style=None,
                initial_view_state=pdk.ViewState(latitude=13.5, longitude=100.8, zoom=4.5),
                layers=[pdk.Layer("ScatterplotLayer", all_data, get_position="[lon, lat]", get_color="[34, 211, 238, 200]", get_radius=60000)],
            ), use_container_width=True)

        with col_rank:
            m_name = s_metric_name.split(' (')[0]
            if m_name == "CO₂": m_name = "คาร์บอนไดออกไซด์ (CO₂)"
            st.markdown(f"<p style='font-size:11px; color:#22d3ee; margin-bottom:5px;'>อันดับ{m_name}</p>", unsafe_allow_html=True)
            df_rank = all_data.sort_values(by=s_metric, ascending=False).head(6).copy()
            df_rank['Region'] = df_rank['region'].map({v: k for k, v in REGION_MAP.items()})
            st.dataframe(df_rank[['Region', s_metric]].rename(columns={s_metric: 'Value'}), hide_index=True, use_container_width=True, height=225)

        with col_trend:
            st.markdown("<p style='font-size:11px; color:#22d3ee; margin-bottom:5px;'>TREND ANALYSIS (Every 1 Hour)</p>", unsafe_allow_html=True)
            history['timestamp'] = pd.to_datetime(history['timestamp'])
            # แก้ไขบัคเวลาตรงนี้: ปรับ tickformat เป็น %H:%M
            fig = px.area(history.sort_values('timestamp'), x='timestamp', y=s_metric, height=220)
            fig.update_layout(
                margin=dict(l=0, r=0, t=5, b=0),
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', 
                font=dict(color="#94a3b8", size=8),
                xaxis=dict(showgrid=False, nticks=6, tickformat="%H:%M", title=None), # แก้ไขบัคเวลา
                yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.05)", title=None)
            )
            fig.update_traces(line_color='#22d3ee', fillcolor='rgba(34, 211, 238, 0.1)')
            st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Waiting for data... ({e})")
else:
    st.error("DB connection error")
