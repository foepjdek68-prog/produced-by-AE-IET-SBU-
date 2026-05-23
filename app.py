import streamlit as st
import pandas as pd
import plotly.express as px
import pydeck as pdk
import requests

# =====================================================================
# 1. PAGE CONFIGURATION & THEME
# =====================================================================
st.set_page_config(page_title="GHG Analytics Dashboard", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    .block-container { padding-top: 0.5rem; padding-bottom: 1rem; }
    .stApp { background-color: #020617; }
    div[data-baseweb="select"] { background-color: #1e293b !important; border: 1px solid #334155 !important; }
    div[data-testid="stMetric"] { background: #1e293b; padding: 10px; border-radius: 6px; border: 1px solid #334155; }
    .compact-table { width: 100%; border-collapse: collapse; font-size: 12px; color: #e2e8f0; }
    .compact-table th { background-color: #0f172a; padding: 8px; border-bottom: 1px solid #334155; }
    .compact-table td { padding: 8px; border-bottom: 1px solid #1e293b; }
    footer, header { visibility: hidden; display: none !important; }
    </style>
    """, unsafe_allow_html=True)

# =====================================================================
# 2. DATA PROCESSING
# =====================================================================
@st.cache_data(ttl=300)
def fetch_data():
    # สร้างข้อมูลจำลองที่ถูกต้อง 100%
    regions = ["North", "Central", "South", "Northeast", "East", "West"]
    th_names = {"North":"ภาคเหนือ", "Central":"ภาคกลาง", "South":"ภาคใต้", "Northeast":"ภาคอีสาน", "East":"ภาคตะวันออก", "West":"ภาคตะวันตก"}
    coords = {"North": [18.78, 98.98], "Central": [13.75, 100.50], "South": [7.88, 98.39], "Northeast": [14.97, 102.10], "East": [12.92, 100.88], "West": [13.52, 99.81]}
    
    latest_list = []
    for r in regions:
        latest_list.append({
            "region": r, "th_name": th_names[r], "lat": coords[r][0], "lon": coords[r][1],
            "co2": 433 if r == "Central" else 412, "ch4": 1865 if r == "Central" else 1810,
            "no2": 42.1 if r == "Central" else 12.4, "temp": 33.2 if r == "Central" else 29.0,
            "pm25": 22.4 if r == "Central" else 35.0, "humidity": 64.0
        })
    
    history_list = []
    for r in regions:
        for idx in range(12):
            history_list.append({"month": ["ม.ค.","ก.พ.","มี.ค.","เม.ย.","พ.ค.","มิ.ย.","ก.ค.","ส.ค.","ก.ย.","ต.ค.","พ.ย.","ธ.ค."][idx], "region": r, "co2": 410 + idx, "ch4": 1800 + idx, "no2": 20 + idx, "temp": 28 + idx, "pm25": 20 + idx, "humidity": 70})
    return pd.DataFrame(latest_list), pd.DataFrame(history_list)

df_latest, df_history = fetch_data()

REGION_MAP = {"ภาคกลาง": "Central", "ภาคเหนือ": "North", "ภาคใต้": "South", "ภาคอีสาน": "Northeast", "ภาคตะวันออก": "East", "ภาคตะวันตก": "West"}
METRIC_MAP = {"CO₂": "co2", "CH₄": "ch4", "NO₂": "no2", "Temp": "temp", "PM 2.5": "pm25", "Humidity": "humidity"}

# =====================================================================
# 3. UI LAYOUT
# =====================================================================
col1, col2, col3, col4 = st.columns([0.5, 2, 1, 1])
with col1: st.image("https://comci.southeast.ac.th/wp-content/uploads/2023/11/logo_comsci_re-1.png", width=60)
with col2: st.markdown("### ระบบวิเคราะห์ข้อมูลสภาพภูมิอากาศ")
with col3: selected_metric_th = st.selectbox("ตัวชี้วัด", list(METRIC_MAP.keys()), label_visibility="collapsed")
with col4: selected_region_th = st.selectbox("ภูมิภาค", list(REGION_MAP.keys()), label_visibility="collapsed")

metric_key = METRIC_MAP[selected_metric_th]
region_key = REGION_MAP[selected_region_th]

# Metrics Row
m1, m2, m3, m4, m5, m6 = st.columns(6)
for i, m in enumerate([m1, m2, m3, m4, m5, m6]):
    m.metric(label=list(METRIC_MAP.keys())[i], value=f"{df_latest[list(METRIC_MAP.values())[i]].iloc[0]:.1f}")

# Map & Table Row (50/50 Split)
col_left, col_right = st.columns(2)

with col_left:
    st.markdown(f"**แผนที่แสดงจุดตรวจวัด ({selected_metric_th})**")
    st.pydeck_chart(pdk.Deck(map_style="mapbox://styles/mapbox/dark-v10", initial_view_state=pdk.ViewState(latitude=13, longitude=101, zoom=5), layers=[pdk.Layer("ScatterplotLayer", df_latest, get_position="[lon, lat]", get_radius=50000, get_color=[255, 0, 0, 160])]), use_container_width=True)

with col_right:
    st.markdown(f"**ตารางเปรียบเทียบข้อมูล ({selected_metric_th})**")
    table_data = df_latest[['th_name', metric_key]].sort_values(by=metric_key, ascending=False)
    html = "<table class='compact-table'><tr><th>ภูมิภาค</th><th>ค่าตรวจวัด</th></tr>"
    for _, row in table_data.iterrows():
        style = "style='color: #22d3ee; font-weight: bold;'" if row['th_name'] == selected_region_th else ""
        html += f"<tr {style}><td>{row['th_name']}</td><td>{row[metric_key]:.1f}</td></tr>"
    html += "</table>"
    st.markdown(html, unsafe_allow_html=True)

# Trend Graph
st.markdown(f"**แนวโน้มรายเดือนของ {selected_region_th}**")
st.plotly_chart(px.area(df_history[df_history['region'] == region_key], x='month', y=metric_key), use_container_width=True)
