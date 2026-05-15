import streamlit as st
import pandas as pd
import plotly.express as px
import pydeck as pdk
import sqlite3
import os

# 1. ตั้งค่าหน้าจอ (ต้องอยู่บรรทัดแรก)
st.set_page_config(page_title="GHGs Monitoring Dashboard", layout="wide", initial_sidebar_state="collapsed")

# --- 🎨 2. CSS: ปรับ UI ตามแบบ 100% (Midnight Glass Theme) ---
st.markdown("""
    <style>
    /* พื้นหลังหลักของแอป */
    .stApp { background-color: #020617; color: #f8fafc; }
    .block-container { padding: 1rem 2rem !important; }

    /* ส่วนหัว (Title Section) */
    .header-container { display: flex; align-items: center; gap: 15px; margin-bottom: 20px; }
    .main-title { font-size: 26px; font-weight: 800; color: #ffffff; margin: 0; letter-spacing: 1px; }

    /* ตกแต่ง Metric Card แบบ Glass */
    div[data-testid="stMetric"] { 
        background: rgba(15, 23, 42, 0.6); 
        padding: 20px; 
        border-radius: 15px; 
        border: 1px solid rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
    }
    [data-testid="stMetricValue"] { font-size: 28px !important; color: #22d3ee !important; font-weight: 700; }
    [data-testid="stMetricLabel"] { font-size: 14px !important; color: #94a3b8 !important; text-transform: uppercase; }

    /* การ์ดล้อมรอบแผนที่และกราฟ */
    .content-card {
        background: rgba(15, 23, 42, 0.4);
        padding: 20px;
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.05);
    }

    /* เครดิตมุมขวาล่าง */
    .footer-credit {
        position: fixed;
        bottom: 20px;
        right: 20px;
        background: rgba(15, 23, 42, 0.8);
        padding: 15px;
        border-radius: 15px;
        border: 1px solid rgba(34, 211, 238, 0.3);
        display: flex;
        align-items: center;
        gap: 12px;
        z-index: 1000;
    }
    .footer-credit img { width: 50px; border-radius: 50%; }
    .footer-credit div { font-size: 11px; color: #94a3b8; line-height: 1.2; }
    </style>
    
    <div class="footer-credit">
        <img src="https://upload.wikimedia.org/wikipedia/th/thumb/a/a2/Southeast_Bangkok_University_Logo.png/200px-Southeast_Bangkok_University_Logo.png">
        <div><b>AE-IET [SBU] Team</b><br>Contact us for environmental solutions.</div>
    </div>
    """, unsafe_allow_html=True)

# --- 🛠️ 3. ฟังก์ชันและข้อมูล ---
def get_db_connection():
    db_path = os.path.join(os.path.dirname(__file__), 'data', 'ghg_data.db')
    return sqlite3.connect(db_path) if os.path.exists(db_path) else None

REGION_MAP = {"ภาคเหนือ": "North", "ภาคกลาง": "Central", "ภาคใต้": "South", "ภาคอีสาน": "Northeast", "ภาคตะวันออก": "East", "ภาคตะวันตก": "West"}
METRIC_MAP = {"คาร์บอนไดออกไซด์ (CO₂)": "co2", "มีเทน (CH₄)": "ch4", "ไนโตรเจน (NO₂)": "no2", "อุณหภูมิ (Temp)": "temp"}
COORDS = {"North": [18.78, 98.98], "Central": [13.75, 100.50], "South": [7.88, 98.39], "Northeast": [14.97, 102.10], "East": [12.92, 100.88], "West": [13.52, 99.81]}

# --- 🔝 4. Header & Filter ---
st.markdown('<div class="header-container"><p class="main-title">TRACKING GHGs EMISSION</p></div>', unsafe_allow_html=True)

f1, f2 = st.columns([1, 1])
with f1: s_region_name = st.selectbox("📍 Select Region", list(REGION_MAP.keys()), index=1)
with f2: s_metric_name = st.selectbox("📊 Select Metric", list(METRIC_MAP.keys()), index=0)

s_region = REGION_MAP[s_region_name]
s_metric = METRIC_MAP[s_metric_name]

# --- 📊 5. Main Content Logic ---
conn = get_db_connection()
if conn:
    try:
        # Load Data
        latest = pd.read_sql(f"SELECT * FROM ghg_logs WHERE region='{s_region}' ORDER BY timestamp DESC LIMIT 1", conn).iloc[0]
        history = pd.read_sql(f"SELECT * FROM ghg_logs WHERE region='{s_region}' ORDER BY timestamp DESC LIMIT 15", conn)
        all_data = pd.read_sql("SELECT region, MAX(co2) as co2, MAX(ch4) as ch4, MAX(no2) as no2, MAX(temp) as temp FROM ghg_logs GROUP BY region", conn)
        conn.close()

        # [Top Row] Metrics
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("CO₂ Concentration", f"{int(latest['co2'])} ppm")
        m2.metric("Methane (CH₄)", f"{latest['ch4']:.1f} ppb")
        m3.metric("Nitrous Oxide (N₂O)", f"{latest['no2']:.1f} ppb")
        m4.metric("Temperature", f"{int(latest['temp'])}°C")

        st.markdown("<br>", unsafe_allow_html=True)

        # [Main Grid] Map (Left) & Data (Right)
        col_map, col_data = st.columns([1.4, 1])

        with col_map:
            st.markdown(f"##### 🟢 2D STATION NETWORK [{s_region_name}]")
            all_data['lat'] = all_data['region'].map(lambda x: COORDS[x][0])
            all_data['lon'] = all_data['region'].map(lambda x: COORDS[x][1])
            
            st.pydeck_chart(pdk.Deck(
                map_style="mapbox://styles/mapbox/dark-v11",
                initial_view_state=pdk.ViewState(latitude=13.5, longitude=101, zoom=5.2, pitch=0),
                layers=[
                    pdk.Layer(
                        "ScatterplotLayer",
                        all_data,
                        get_position="[lon, lat]",
                        get_color="[34, 211, 238, 200]", # Cyan color
                        get_radius=50000,
                        pickable=True
                    )
                ],
            ))

        with col_data:
            # Trend Chart
            st.markdown(f"##### 📈 GHGs TREND [{s_region_name}]")
            history['timestamp'] = pd.to_datetime(history['timestamp'])
            fig = px.area(history.sort_values('timestamp'), x='timestamp', y=s_metric, height=240)
            fig.update_layout(
                margin=dict(l=0, r=0, t=10, b=0),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color="#94a3b8", size=10),
                xaxis=dict(showgrid=False),
                yaxis=dict(gridcolor="rgba(255,255,255,0.1)")
            )
            fig.update_traces(line_color='#22d3ee', fillcolor='rgba(34, 211, 238, 0.1)')
            st.plotly_chart(fig, use_container_width=True)

            # Ranking Table
            st.markdown("##### 🏆 TOP REGIONS RANKING")
            df_rank = all_data.sort_values(by=s_metric, ascending=False)
            df_rank['ภูมิภาค'] = df_rank['region'].map({v: k for k, v in REGION_MAP.items()})
            st.dataframe(
                df_rank[['ภูมิภาค', s_metric]].rename(columns={s_metric: 'Value'}),
                hide_index=True, 
                use_container_width=True, 
                height=180
            )

    except Exception as e:
        st.error(f"ระบบกำลังรวบรวมข้อมูล: {e}")
else:
    st.error("⚠️ ไม่พบฐานข้อมูลที่โฟลเดอร์ data/ghg_data.db")
