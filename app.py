import streamlit as st
import pandas as pd
import plotly.express as px
import pydeck as pdk
import sqlite3
import os

# --- [1. CONFIG] ---
st.set_page_config(page_title="GHG Monitoring SBU", layout="wide", initial_sidebar_state="collapsed")

# --- [2. CSS] ปรับแต่ง UI ให้สวยแบบ Glassmorphism และแก้บัคโลโก้ ---
st.markdown("""
    <style>
    /* พื้นหลังแบบไล่เฉดเข้ม */
    .stApp { 
        background: linear-gradient(135deg, #020617 0%, #0f172a 100%);
        color: #f8fafc;
    }
    
    /* ตกแต่ง Metric Card (กล่องตัวเลข) */
    div[data-testid="stMetric"] { 
        background: rgba(30, 41, 59, 0.4); 
        padding: 20px; 
        border-radius: 15px; 
        border: 1px solid rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
    }
    [data-testid="stMetricValue"] { color: #22d3ee !important; font-size: 32px !important; }

    /* เครดิตลอยมุมขวาล่าง (แก้บัครูปแตก) */
    .footer-credit {
        position: fixed; bottom: 20px; right: 20px;
        background: rgba(15, 23, 42, 0.85);
        padding: 15px; border-radius: 15px;
        border: 1px solid rgba(34, 211, 238, 0.5);
        display: flex; align-items: center; gap: 15px; z-index: 9999;
        box-shadow: 0 0 20px rgba(34, 211, 238, 0.2);
    }
    .footer-credit img {
        width: 50px; height: 50px; object-fit: contain;
        background: white; border-radius: 50%; padding: 2px;
    }
    .footer-credit div { font-size: 11px; color: #94a3b8; }
    </style>

    <div class="footer-credit">
        <img src="https://raw.githubusercontent.com/AE-IET-SBU/assets/main/sbu_logo.png" 
             onerror="this.src='https://upload.wikimedia.org/wikipedia/th/thumb/a/a2/Southeast_Bangkok_University_Logo.png/200px-Southeast_Bangkok_University_Logo.png'">
        <div>
            <b style="color:#fff;">Dashboard produced by</b><br>
            AE-IET [SBU] Team<br>
            Environmental Monitoring
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- [3. DATA CONNECTION] ---
def get_db_connection():
    db_path = os.path.join(os.path.dirname(__file__), 'data', 'ghg_data.db')
    return sqlite3.connect(db_path) if os.path.exists(db_path) else None

REGION_MAP = {"ภาคเหนือ": "North", "ภาคกลาง": "Central", "ภาคใต้": "South", "ภาคอีสาน": "Northeast", "ภาคตะวันออก": "East", "ภาคตะวันตก": "West"}
METRIC_MAP = {"คาร์บอนไดออกไซด์ (CO₂)": "co2", "มีเทน (CH₄)": "ch4", "ไนโตรเจน (NO₂)": "no2", "อุณหภูมิ (Temp)": "temp"}
COORDS = {"North": [18.78, 98.98], "Central": [13.75, 100.50], "South": [7.88, 98.39], "Northeast": [14.97, 102.10], "East": [12.92, 100.88], "West": [13.52, 99.81]}

# --- [4. LAYOUT] ---
st.markdown("<h1 style='margin-bottom:0;'>TRACKING GHGs EMISSION</h1>", unsafe_allow_html=True)
st.markdown("<p style='color:#64748b; margin-bottom:30px;'>produced by AE-IET [SBU]</p>", unsafe_allow_html=True)

# แถวตัวเลือก (คุมโทนให้เรียบง่าย)
sel1, sel2 = st.columns(2)
with sel1: s_region_name = st.selectbox("📍 ภูมิภาค:", list(REGION_MAP.keys()), index=1)
with sel2: s_metric_name = st.selectbox("📊 ดัชนีตรวจวัด:", list(METRIC_MAP.keys()), index=0)

s_region = REGION_MAP[s_region_name]
s_metric = METRIC_MAP[s_metric_name]

# --- [5. DASHBOARD CONTENT] ---
conn = get_db_connection()
if conn:
    try:
        latest = pd.read_sql(f"SELECT * FROM ghg_logs WHERE region='{s_region}' ORDER BY timestamp DESC LIMIT 1", conn).iloc[0]
        history = pd.read_sql(f"SELECT * FROM ghg_logs WHERE region='{s_region}' ORDER BY timestamp DESC LIMIT 20", conn)
        all_data = pd.read_sql("SELECT region, MAX(co2) as co2, MAX(ch4) as ch4, MAX(no2) as no2, MAX(temp) as temp FROM ghg_logs GROUP BY region", conn)
        conn.close()

        # แถวบน: Metrics
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("CO₂ (ppm)", f"{int(latest['co2'])}")
        m2.metric("CH₄ (ppb)", f"{latest['ch4']:.1f}")
        m3.metric("NO₂ (ppb)", f"{latest['no2']:.1f}")
        m4.metric("TEMP (°C)", f"{int(latest['temp'])}")

        st.markdown("<br>", unsafe_allow_html=True)

        # แถวล่าง: แผนที่ (ซ้าย) และ ข้อมูล (ขวา)
        col_left, col_right = st.columns([1.5, 1])

        with col_left:
            st.markdown(f"##### 🗺️ โครงข่ายสถานี: {s_region_name}")
            all_data['lat'] = all_data['region'].map(lambda x: COORDS[x][0])
            all_data['lon'] = all_data['region'].map(lambda x: COORDS[x][1])
            
            # บังคับใช้ Map Style ที่ไม่ต้องพึ่ง Token เพื่อลดโอกาสพื้นหลังดำ
            st.pydeck_chart(pdk.Deck(
                map_style=None, # ใช้ Default ของ Deck.gl เพื่อความชัวร์
                initial_view_state=pdk.ViewState(latitude=13.5, longitude=101, zoom=5.3),
                layers=[
                    pdk.Layer(
                        "ScatterplotLayer", all_data,
                        get_position="[lon, lat]",
                        get_color="[34, 211, 238, 200]", # สีฟ้า Cyan
                        get_radius=55000,
                    )
                ],
            ))

        with col_right:
            # กราฟแนวโน้มแบบ Area (สวยกว่าเส้นตรง)
            st.markdown(f"##### 📈 แนวโน้มความเข้มข้น")
            history['timestamp'] = pd.to_datetime(history['timestamp'])
            fig = px.area(history.sort_values('timestamp'), x='timestamp', y=s_metric, height=260)
            fig.update_layout(
                margin=dict(l=0, r=0, t=10, b=0),
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color="#94a3b8", size=10),
                xaxis=dict(showgrid=False), yaxis=dict(gridcolor="rgba(255,255,255,0.05)")
            )
            fig.update_traces(line_color='#22d3ee', fillcolor='rgba(34, 211, 238, 0.1)')
            st.plotly_chart(fig, use_container_width=True)

            # อันดับสูงสุด
            st.markdown("##### 🏆 อันดับพื้นที่มลพิษสูงสุด")
            df_rank = all_data.sort_values(by=s_metric, ascending=False)
            df_rank['ภูมิภาค'] = df_rank['region'].map({v: k for k, v in REGION_MAP.items()})
            st.dataframe(df_rank[['ภูมิภาค', s_metric]], hide_index=True, use_container_width=True, height=180)

    except Exception as e:
        st.error(f"ระบบกำลังซิงค์ฐานข้อมูล... ({e})")
else:
    st.error("⚠️ ไม่พบไฟล์ data/ghg_data.db กรุณาตรวจสอบโฟลเดอร์ใน GitHub")
