import streamlit as st
import pandas as pd
import plotly.express as px
import pydeck as pdk
import sqlite3
import os

# 1. ตั้งค่าหน้าจอ (ต้องอยู่บนสุด)
st.set_page_config(page_title="GHGs Monitoring Dashboard", layout="wide", initial_sidebar_state="collapsed")

# --- 🎨 2. CSS: ปรับดีไซน์ใหม่และแก้บัคภาพไม่โหลด ---
st.markdown("""
    <style>
    /* พื้นหลัง Midnight Blue */
    .stApp { background-color: #020617; color: #f8fafc; }
    .block-container { padding: 1rem 2rem !important; }

    /* ตกแต่ง Metric Cards */
    div[data-testid="stMetric"] { 
        background: rgba(15, 23, 42, 0.7); 
        padding: 20px; 
        border-radius: 15px; 
        border: 1px solid rgba(34, 211, 238, 0.2);
        backdrop-filter: blur(10px);
    }
    [data-testid="stMetricValue"] { font-size: 26px !important; color: #22d3ee !important; font-weight: 700; }
    
    /* กล่องเครดิตมุมขวาล่าง (แก้บัคการแสดงผลภาพ) */
    .fixed-credit {
        position: fixed;
        bottom: 20px;
        right: 20px;
        background: rgba(15, 23, 42, 0.9);
        padding: 15px;
        border-radius: 15px;
        border: 1px solid rgba(34, 211, 238, 0.4);
        display: flex;
        align-items: center;
        gap: 12px;
        z-index: 9999;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }
    .fixed-credit img {
        width: 50px;
        height: 50px;
        object-fit: contain;
    }
    .fixed-credit div {
        font-size: 11px;
        color: #94a3b8;
        line-height: 1.3;
    }
    </style>

    <div class="fixed-credit">
        <img src="https://upload.wikimedia.org/wikipedia/th/thumb/a/a2/Southeast_Bangkok_University_Logo.png/200px-Southeast_Bangkok_University_Logo.png" alt="SBU Logo">
        <div>
            <b style="color:#fff;">Dashboard Produced by</b><br>
            AE-IET [SBU] Team<br>
            Monitoring Solutions
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- 🛠️ 3. Data Connection ---
def get_db_connection():
    db_path = os.path.join(os.path.dirname(__file__), 'data', 'ghg_data.db')
    return sqlite3.connect(db_path) if os.path.exists(db_path) else None

REGION_MAP = {"ภาคเหนือ": "North", "ภาคกลาง": "Central", "ภาคใต้": "South", "ภาคอีสาน": "Northeast", "ภาคตะวันออก": "East", "ภาคตะวันตก": "West"}
METRIC_MAP = {"คาร์บอนไดออกไซด์ (CO₂)": "co2", "มีเทน (CH₄)": "ch4", "ไนโตรเจน (NO₂)": "no2", "อุณหภูมิ (Temp)": "temp"}
COORDS = {"North": [18.78, 98.98], "Central": [13.75, 100.50], "South": [7.88, 98.39], "Northeast": [14.97, 102.10], "East": [12.92, 100.88], "West": [13.52, 99.81]}

# --- 🔝 4. Layout: Header & Metrics ---
st.markdown("<h2 style='margin-bottom:0;'>TRACKING GHGs EMISSION</h2>", unsafe_allow_html=True)
st.markdown("<p style='color:#64748b; margin-bottom:20px;'>produced by AE-IET [SBU]</p>", unsafe_allow_html=True)

# แถวตัวเลือก
f1, f2 = st.columns(2)
with f1: s_region_name = st.selectbox("📍 พื้นที่พยากรณ์:", list(REGION_MAP.keys()), index=1)
with f2: s_metric_name = st.selectbox("📊 ดัชนีตรวจวัด:", list(METRIC_MAP.keys()), index=0)

s_region = REGION_MAP[s_region_name]
s_metric = METRIC_MAP[s_metric_name]

# --- 📊 5. Dashboard Logic ---
conn = get_db_connection()
if conn:
    try:
        # Load Data
        latest = pd.read_sql(f"SELECT * FROM ghg_logs WHERE region='{s_region}' ORDER BY timestamp DESC LIMIT 1", conn).iloc[0]
        history = pd.read_sql(f"SELECT * FROM ghg_logs WHERE region='{s_region}' ORDER BY timestamp DESC LIMIT 15", conn)
        all_data = pd.read_sql("SELECT region, MAX(co2) as co2, MAX(ch4) as ch4, MAX(no2) as no2, MAX(temp) as temp FROM ghg_logs GROUP BY region", conn)
        conn.close()

        # แถว Metric Cards (4 ช่อง)
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("CO₂ (ppm)", f"{int(latest['co2'])}")
        m2.metric("CH₄ (ppb)", f"{latest['ch4']:.1f}")
        m3.metric("NO₂ (ppb)", f"{latest['no2']:.1f}")
        m4.metric("Temp (°C)", f"{int(latest['temp'])}")

        st.markdown("<br>", unsafe_allow_html=True)

        # จัดเลย์เอาต์หลัก [ซ้าย 60% : ขวา 40%]
        col_left, col_right = st.columns([1.4, 1])

        with col_left:
            st.markdown(f"##### 🗺️ แผนที่พยากรณ์โครงข่ายสถานี: {s_region_name}")
            all_data['lat'] = all_data['region'].map(lambda x: COORDS[x][0])
            all_data['lon'] = all_data['region'].map(lambda x: COORDS[x][1])
            
            st.pydeck_chart(pdk.Deck(
                map_style="mapbox://styles/mapbox/dark-v11",
                initial_view_state=pdk.ViewState(latitude=13.5, longitude=101, zoom=5.2),
                layers=[
                    pdk.Layer(
                        "ScatterplotLayer",
                        all_data,
                        get_position="[lon, lat]",
                        get_color="[34, 211, 238, 200]",
                        get_radius=50000,
                    )
                ],
            ))

        with col_right:
            # กราฟแนวโน้ม
            st.markdown(f"##### 📈 แนวโน้ม {s_metric_name.split(' (')[0]}")
            history['timestamp'] = pd.to_datetime(history['timestamp'])
            fig = px.area(history.sort_values('timestamp'), x='timestamp', y=s_metric, height=250)
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

            # ตารางจัดอันดับ
            st.markdown("##### 🏆 ตารางสรุปอันดับภูมิภาค")
            df_rank = all_data.sort_values(by=s_metric, ascending=False)
            df_rank['ภูมิภาค'] = df_rank['region'].map({v: k for k, v in REGION_MAP.items()})
            st.dataframe(df_rank[['ภูมิภาค', s_metric]], hide_index=True, use_container_width=True, height=180)

    except Exception as e:
        st.error(f"ระบบกำลังซิงค์ข้อมูล... (Error: {e})")
else:
    st.error("⚠️ ไม่พบฐานข้อมูลที่โฟลเดอร์ data/ghg_data.db")
