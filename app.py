import streamlit as st
import pandas as pd
import plotly.express as px
import pydeck as pdk
import sqlite3
import os

# --- 1. ตั้งค่าหน้าจอ (ต้องอยู่บนสุดเสมอ) ---
st.set_page_config(page_title="SBU GHGs Tracking", layout="wide", initial_sidebar_state="collapsed")

# --- 2. CSS: ตกแต่งธีมและการจัดวางเครดิตมุมขวาล่าง ---
st.markdown("""
    <style>
    /* พื้นหลังหลักของแอป: สีเทาดำ Charcoal */
    .stApp { background-color: #111827; } 
    
    /* การ์ดสรุปตัวเลข: สีกรมท่าเข้ม */
    div[data-testid="stMetric"] { 
        background: #1f2937; 
        padding: 15px; 
        border-radius: 12px; 
        border-left: 5px solid #22d3ee;
    }
    [data-testid="stMetricValue"] { color: #22d3ee !important; font-weight: bold; }

    /* โลโก้เครดิตมุมขวาล่างแบบลอย (Fixed Position) */
    .credit-box {
        position: fixed;
        bottom: 15px;
        right: 15px;
        z-index: 1000;
        background: rgba(31, 41, 55, 0.9);
        padding: 10px;
        border-radius: 15px;
        border: 1px solid rgba(34, 211, 238, 0.3);
        text-align: center;
        width: 100px;
    }
    .credit-box img { width: 60px; margin-bottom: 5px; }
    .credit-box div { color: #9ca3af; font-size: 10px; font-weight: 600; }
    </style>
    
    <div class="credit-box">
        <img src="https://upload.wikimedia.org/wikipedia/th/thumb/a/a2/Southeast_Bangkok_University_Logo.png/200px-Southeast_Bangkok_University_Logo.png">
        <div>Produced by AE-IET [SBU]</div>
    </div>
    """, unsafe_allow_html=True)

# --- 3. ฟังก์ชันเชื่อมต่อฐานข้อมูล ---
def get_db_connection():
    db_path = os.path.join(os.path.dirname(__file__), 'data', 'ghg_data.db')
    if not os.path.exists(db_path):
        return None
    return sqlite3.connect(db_path)

# --- 4. การตั้งค่าข้อมูลพื้นฐาน ---
METRIC_MAP = {"คาร์บอนไดออกไซด์ (CO₂)": "co2", "มีเทน (CH₄)": "ch4", "ไนโตรเจน (NO₂)": "no2", "อุณหภูมิ (Temp)": "temp"}
REGION_MAP = {"ภาคเหนือ": "North", "ภาคกลาง": "Central", "ภาคใต้": "South", "ภาคอีสาน": "Northeast", "ภาคตะวันออก": "East", "ภาคตะวันตก": "West"}
COORDS = {"North": [18.78, 98.98], "Central": [13.75, 100.50], "South": [7.88, 98.39], "Northeast": [14.97, 102.10], "East": [12.92, 100.88], "West": [13.52, 99.81]}

# --- 5. HEADER & SELECTION ---
col_head1, col_head2 = st.columns([2, 1])
with col_head1:
    st.markdown('<h1 style="color:white; margin:0;">TRACKING GHGs EMISSION</h1>', unsafe_allow_html=True)
    st.markdown('<p style="color:#9ca3af; font-size:14px;">Environmental Monitoring System by SBU</p>', unsafe_allow_html=True)

with col_head2:
    sel1, sel2 = st.columns(2)
    s_region_name = sel1.selectbox("เลือกพื้นที่", list(REGION_MAP.keys()), index=1)
    s_metric_name = sel2.selectbox("เลือกดัชนี", list(METRIC_MAP.keys()), index=0)
    
    s_region = REGION_MAP[s_region_name]
    s_metric = METRIC_MAP[s_metric_name]

st.markdown("<hr style='border:1px solid #374151;'>", unsafe_allow_html=True)

# --- 6. แสดงผล DASHBOARD ---
conn = get_db_connection()
if conn:
    try:
        # ดึงข้อมูล
        latest = pd.read_sql(f"SELECT * FROM ghg_logs WHERE region='{s_region}' ORDER BY timestamp DESC LIMIT 1", conn).iloc[0]
        history = pd.read_sql(f"SELECT * FROM ghg_logs WHERE region='{s_region}' ORDER BY timestamp DESC LIMIT 15", conn)
        all_data = pd.read_sql("SELECT region, MAX(co2) as co2, MAX(ch4) as ch4, MAX(no2) as no2, MAX(temp) as temp FROM ghg_logs GROUP BY region", conn)
        conn.close()

        # ส่วนที่ 1: Metric Cards
        m_col1, m_col2, m_col3, m_col4 = st.columns(4)
        m_col1.metric("CO₂ (ppm)", f"{int(latest['co2'])}")
        m_col2.metric("CH₄ (ppb)", f"{latest['ch4']:.1f}")
        m_col3.metric("NO₂ (ppb)", f"{latest['no2']:.1f}")
        m_col4.metric("Temp (°C)", f"{int(latest['temp'])}")

        st.write("")

        # ส่วนที่ 2: จัดระเบียบ Layout (ใช้ชื่อตัวแปรที่เข้าใจง่ายและป้องกัน NameError)
        content_col_left, content_col_right = st.columns([1.3, 1])

        # --- ฝั่งซ้าย: แผนที่ ---
        all_data['lat'] = all_data['region'].map(lambda x: COORDS[x][0])
        all_data['lon'] = all_data['region'].map(lambda x: COORDS[x][1])
        
        content_col_left.markdown("##### 🗺️ แผนที่โครงข่ายสถานี (2D Spatial)")
        content_col_left.pydeck_chart(pdk.Deck(
            map_style="mapbox://styles/mapbox/dark-v11",
            initial_view_state=pdk.ViewState(latitude=13.5, longitude=101, zoom=5),
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

        # --- ฝั่งขวา: กราฟและอันดับ ---
        # กราฟ
        content_col_right.markdown(f"##### 📈 แนวโน้ม {s_metric_name.split(' (')[0]}")
        history['timestamp'] = pd.to_datetime(history['timestamp'])
        fig = px.line(history.sort_values('timestamp'), x='timestamp', y=s_metric, height=240, color_discrete_sequence=['#22d3ee'])
        fig.update_layout(margin=dict(l=0, r=0, t=10, b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="#9ca3af")
        content_col_right.plotly_chart(fig, use_container_width=True)
        
        # ตาราง
        content_col_right.markdown("##### 🏆 ตารางจัดอันดับภูมิภาค")
        df_rank = all_data.sort_values(by=s_metric, ascending=False)
        inv_map = {v: k for k, v in REGION_MAP.items()}
        df_rank['ภูมิภาค'] = df_rank['region'].map(inv_map)
        content_col_right.dataframe(df_rank[['ภูมิภาค', s_metric]], hide_index=True, use_container_width=True, height=180)

    except Exception as e:
        st.error(f"Error logic: {e}")
else:
    st.error("⚠️ ไม่พบฐานข้อมูลที่โฟลเดอร์ data/ghg_data.db")
