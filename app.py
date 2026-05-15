import streamlit as st
import pandas as pd
import plotly.express as px
import pydeck as pdk
import sqlite3
import os

# 1. ตั้งค่าหน้าจอ
st.set_page_config(page_title="GHGs Monitoring SBU", layout="wide")

# --- 🎨 CSS: คลุมโทนสีและจัดการโลโก้ (แบบเดิมที่รูปไม่แตก) ---
st.markdown("""
    <style>
    .stApp { background-color: #020617; color: white; }
    
    /* กล่องสรุปตัวเลข */
    div[data-testid="stMetric"] { 
        background: #1f2937; 
        padding: 15px; 
        border-radius: 10px; 
        border-left: 5px solid #22d3ee;
    }

    /* เครดิตโลโก้มุมขวาล่าง */
    .footer-credit {
        position: fixed; bottom: 20px; right: 20px;
        background: rgba(15, 23, 42, 0.9);
        padding: 15px; border-radius: 15px;
        border: 1px solid #22d3ee;
        display: flex; align-items: center; gap: 15px; z-index: 9999;
    }
    .footer-credit img { width: 130px; height: auto; }
    </style>

    <div class="footer-credit">
        <a href="https://www.southeast.ac.th/about-us/" target="_blank">
            <img src="https://www.southeast.ac.th/wp-content/uploads/2023/11/logo-main2.png" 
                 onerror="this.src='https://upload.wikimedia.org/wikipedia/th/thumb/a/a2/Southeast_Bangkok_University_Logo.png/200px-Southeast_Bangkok_University_Logo.png'">
        </a>
    </div>
    """, unsafe_allow_html=True)

# --- 🛠️ ส่วนจัดการข้อมูล ---
def get_db_connection():
    db_path = os.path.join(os.path.dirname(__file__), 'data', 'ghg_data.db')
    return sqlite3.connect(db_path) if os.path.exists(db_path) else None

REGION_MAP = {"ภาคเหนือ": "North", "ภาคกลาง": "Central", "ภาคใต้": "South", "ภาคอีสาน": "Northeast", "ภาคตะวันออก": "East", "ภาคตะวันตก": "West"}
METRIC_MAP = {"คาร์บอนไดออกไซด์ (CO₂)": "co2", "มีเทน (CH₄)": "ch4", "ไนโตรเจน (NO₂)": "no2", "อุณหภูมิ (Temp)": "temp"}
COORDS = {"North": [18.78, 98.98], "Central": [13.75, 100.50], "South": [7.88, 98.39], "Northeast": [14.97, 102.10], "East": [12.92, 100.88], "West": [13.52, 99.81]}

# --- 🔝 หัวข้อและการเลือก ---
st.header("TRACKING GHGs EMISSION")
st.write("Environmental Real-time Data by SBU")

col_sel1, col_sel2 = st.columns(2)
with col_sel1:
    region_thai = st.selectbox("เลือกภูมิภาค:", list(REGION_MAP.keys()), index=1)
    s_region = REGION_MAP[region_thai]
with col_sel2:
    metric_thai = st.selectbox("เลือกดัชนี:", list(METRIC_MAP.keys()), index=0)
    s_metric = METRIC_MAP[metric_thai]

# --- 📊 แสดงผลหลัก ---
conn = get_db_connection()
if conn:
    try:
        latest = pd.read_sql(f"SELECT * FROM ghg_logs WHERE region='{s_region}' ORDER BY timestamp DESC LIMIT 1", conn).iloc[0]
        history = pd.read_sql(f"SELECT * FROM ghg_logs WHERE region='{s_region}' ORDER BY timestamp DESC LIMIT 15", conn)
        all_data = pd.read_sql("SELECT region, MAX(co2) as co2, MAX(ch4) as ch4, MAX(no2) as no2, MAX(temp) as temp FROM ghg_logs GROUP BY region", conn)
        conn.close()

        # 1. Metrics
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("CO₂", f"{int(latest['co2'])} ppm")
        m2.metric("CH₄", f"{latest['ch4']:.1f}")
        m3.metric("NO₂", f"{latest['no2']:.1f}")
        m4.metric("Temp", f"{int(latest['temp'])}°C")

        # 2. จัดระเบียบหน้าจอ (ซ้าย: แผนที่, ขวา: กราฟ)
        c_map, c_graph = st.columns([1.5, 1])

        with c_map:
            st.subheader("🗺️ 2D Station Network")
            all_data['lat'] = all_data['region'].map(lambda x: COORDS[x][0])
            all_data['lon'] = all_data['region'].map(lambda x: COORDS[x][1])
            
            # --- แก้ไขส่วนแผนที่ให้ Basic ที่สุดเพื่อกันบัค ---
            st.pydeck_chart(pdk.Deck(
                map_style=None, # ใช้พื้นฐาน ไม่พึ่งพา Style ภายนอก
                initial_view_state=pdk.ViewState(latitude=13.5, longitude=101.0, zoom=5),
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

        with c_graph:
            st.subheader("📈 Trend")
            history['timestamp'] = pd.to_datetime(history['timestamp'])
            fig = px.area(history.sort_values('timestamp'), x='timestamp', y=s_metric, height=300)
            fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white")
            fig.update_traces(line_color='#22d3ee')
            st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"Error: {e}")
else:
    st.error("⚠️ หาไฟล์ data/ghg_data.db ไม่เจอ")
