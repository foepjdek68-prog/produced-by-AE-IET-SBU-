import streamlit as st
import plotly.express as px
import pandas as pd
import time
from streamlit_autorefresh import st_autorefresh
from Services.database import load_data, save_data
from Services.api_loader import fetch_data

# =====================================================
# PAGE CONFIG
# =====================================================
st.set_page_config(
    page_title="Dashboard Tracking GHGs Emission",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =====================================================
# REFRESH CONTROL
# =====================================================
st_autorefresh(interval=60000, key="datarefresh")

# =====================================================
# LOAD DATA
# =====================================================
@st.cache_data(ttl=60)
def get_data():
    df = load_data()
    if df.empty:
        df = fetch_data()
        save_data(df)
    
    if not df.empty:
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        df = df.dropna(subset=["Date"]).sort_values("Date").reset_index(drop=True)
    return df

df = get_data()

if df.empty:
    st.error("ไม่พบข้อมูลในระบบ กรุณาตรวจสอบการเชื่อมต่อฐานข้อมูล")
    st.stop()

latest = df.iloc[-1]
prev = df.iloc[-2] if len(df) > 1 else latest
latest_str = latest["Date"].strftime("%d/%m/%Y %H:%M:%S")

# =====================================================
# SIDEBAR
# =====================================================
with st.sidebar:
    st.markdown('<div style="text-align:center;">', unsafe_allow_html=True)
    st.image("Assets/logo.png", width=250)
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown("""
        <style>
        .sidebar-footer { border-top:1px solid #4B5563; padding-top:10px; margin-top:auto; font-size:0.75em; color:#9CA3AF; }
        </style>
        <div class="sidebar-footer">(C) Dept. Engineering SBU</div>
    """, unsafe_allow_html=True)

# =====================================================
# HEADER
# =====================================================
st.markdown(f"""
<div style="background:linear-gradient(135deg,#0f172a,#1e293b); padding:20px; border-radius:12px; border:1px solid #334155; margin-bottom:20px;">
    <h1 style="margin:0; color:white;">🌍 Dashboard Tracking Greenhouse Gases Emission</h1>
    <p style="margin-top:8px; color:#cbd5e1;">🕒 อัปเดตล่าสุด : {latest_str}</p>
</div>
""", unsafe_allow_html=True)

# =====================================================
# KPI SECTION
# =====================================================
metrics = [
    ("CO2", "CO₂", "Carbon Dioxide"),
    ("CH4", "CH₄", "Methane"),
    ("NO2", "NO₂", "Nitrogen Dioxide"),
    ("PM25", "PM2.5", None),
    ("Temp", "อุณหภูมิ", None),
    ("Humidity", "ความชื้น", None)
]

cols = st.columns(6)
for i, (col, sym, name) in enumerate(metrics):
    val = float(latest.get(col, 0))
    old = float(prev.get(col, 0))
    diff = val - old
    percent = (diff / old * 100) if old != 0 else 0
    delta = f"{'↑' if diff > 0 else '↓' if diff < 0 else '→'} {percent:.1f}%"
    cols[i].metric(f"{sym} ({name})" if name else sym, f"{val:.2f}", delta)

# =====================================================
# GRAPH SECTION
# =====================================================
period = st.selectbox("เลือกช่วงเวลาการแสดงผล", ["รายวัน", "รายสัปดาห์", "รายเดือน", "รายปี"])

if period == "รายวัน": df_plot = df.tail(24)
elif period == "รายสัปดาห์": df_plot = df.tail(24*7)
elif period == "รายเดือน": df_plot = df.tail(24*30)
else:
