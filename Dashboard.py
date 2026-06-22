import streamlit as st
import plotly.express as px
import pandas as pd
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
# DATA HANDLING
# =====================================================
@st.cache_data(ttl=3600)
def get_data():
    df = load_data()
    if df.empty:
        df = fetch_data()
        save_data(df)
    if not df.empty:
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        df = df.dropna(subset=["Date"]).sort_values("Date").reset_index(drop=True)
    return df

# ตรวจสอบการกดปุ่ม Refresh
if st.button("🔄 Refresh Data Now"):
    st.cache_data.clear()

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
    st.markdown('<div style="background:rgba(255,255,255,0.05); padding:15px; border-radius:10px; margin-bottom:20px; text-align:center;">', unsafe_allow_html=True)
    st.image("Assets/logo.png", width=250)
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("""
        <style>
        [data-testid="stSidebar"] > div:first-child { display:flex; flex-direction:column; height:90vh; }
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
# CSS STYLING
# =====================================================
st.markdown("""
<style>
.stApp { background:#030712; }
[data-testid="stMetric"] { background:#0f172a !important; border:1px solid #60a5fa !important; border-radius:12px !important; padding:15px !important; text-align:center; }
[data-testid="stMetricLabel"] { color:#cbd5e1 !important; font-weight:600 !important; }
[data-testid="stMetricValue"] { color:white !important; font-weight:700 !important; }
</style>
""", unsafe_allow_html=True)

# =====================================================
# KPI SECTION
# =====================================================
alerts = []
if latest.get("CO2", 0) > 500: alerts.append("🔴 ระดับ CO₂ สูงเกินเกณฑ์")
if latest.get("PM25", 0) > 35: alerts.append("⚠ แจ้งเตือนค่า PM2.5")
if latest.get("Temp", 0) > 38: alerts.append("🌡 อุณหภูมิสูงเกินเกณฑ์")

def kpi(col, symbol, name=None):
    now, old = float(latest.get(col, 0)), float(prev.get(col, 0))
    diff = now - old
    percent = (diff / old * 100) if old != 0 else 0
    arrow = "↑" if diff > 0 else "↓" if diff < 0 else "→"
    return now, f"{arrow} {percent:.1f}%", f"{symbol} ({name})" if name else symbol

cols = st.columns(6)
metrics = [("CO2","CO₂","Carbon Dioxide"),("CH4","CH₄","Methane"),("NO2","NO₂","Nitrogen Dioxide"),("PM25","PM2.5",None),("Temp","อุณหภูมิ",None),("Humidity","ความชื้น",None)]
for i, (col, sym, name) in enumerate(metrics):
    val, delta, label = kpi(col, sym, name)
    cols[i].metric(label, f"{val:.2f}", delta)

if alerts:
    a_cols = st.columns(len(alerts))
    for
