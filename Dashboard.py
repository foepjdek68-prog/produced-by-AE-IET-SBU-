import streamlit as st
import plotly.express as px
import pandas as pd

from streamlit_autorefresh import st_autorefresh
from Services.database import load_data, save_data
from Services.api_loader import fetch_data

# =====================================================
# การตั้งค่าหน้าจอ (Page Configuration)
# =====================================================
st.set_page_config(
    page_title="Dashboard Tracking Greenhouse Gases Emission",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ตั้งค่ารีเฟรชหน้าจออัตโนมัติทุก 60 วินาที
st_autorefresh(interval=60000, key="refresh")

# =====================================================
# SIDEBAR
# =====================================================
with st.sidebar:
    st.image("Assets/logo.png", width=250)
    st.markdown("""
        <style>
            [data-testid="stSidebar"] > div:first-child { display: flex; flex-direction: column; height: 90vh; }
            .sidebar-spacer { flex-grow: 1; }
            .sidebar-footer { border-top: 1px solid #4B5563; padding-top: 10px; margin-top: auto; font-size: 0.75em; color: #9CA3AF; }
        </style>
        <div class="sidebar-spacer"></div>
        <div class="sidebar-footer">(C) Dept. Engineering SBU </div>
    """, unsafe_allow_html=True)

# CSS ปรับแต่งหน้าจอ
st.markdown("""
<style>
.block-container { padding-top: 1rem; }
[data-testid="stMetric"] { background: #111827; border: 1px solid #374151; border-radius: 12px; padding: 15px; text-align: center; }
[data-testid="stMetricValue"] { font-size: 28px; font-weight: 700; }
</style>
""", unsafe_allow_html=True)

# =====================================================
# LOAD & PREPARE DATA
# =====================================================
df = load_data()
if df.empty:
    df = fetch_data()
    save_data(df)

if df.empty:
    st.error("ไม่พบข้อมูลในระบบ กรุณาตรวจสอบการเชื่อมต่อฐานข้อมูล")
    st.stop()

df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
df = df.dropna(subset=["Date"]).sort_values("Date").reset_index(drop=True)

latest = df.iloc[-1]
prev = df.iloc[-2] if len(df) > 1 else latest
latest_str = latest["Date"].strftime("%d/%m/%Y %H:%M")

# =====================================================
# HEADER
# =====================================================
st.markdown(
    f"""
    <div style="
        background:linear-gradient(135deg,#111827,#1F2937); 
        padding: 40px 30px; 
        border-radius: 20px; 
        border: 1px solid #374151; 
        margin-bottom: 25px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    ">
        <h1 style="margin:0; color:white; font-size: 3rem; line-height: 1.1; font-weight: 800;">
            Dashboard Tracking
        </h1>
        <h1 style="margin:5px 0 0 0; color:white; font-size: 3rem; line-height: 1.1; font-weight: 800;">
            Greenhouse Gases Emission
        </h1>
        <div style="margin-top: 20px; padding-top: 15px; border-top: 1px solid #4B5563; display: inline-block;">
            <p style="color:#9CA3AF; margin:0; font-size: 1.2rem; font-weight: 400;">
                🌍 อัปเดตล่าสุด : {latest_str}
            </p>
        </div>
    </div>
    """, 
    unsafe_allow_html=True
)

# =====================================================
# ALERTS
# =====================================================
alerts = []
if latest.get("CO2", 0) > 500: alerts.append("🔴 ระดับ CO₂ สูงเกินเกณฑ์")
if latest.get("PM25", 0) > 35: alerts.append("⚠ แจ้งเตือนค่า PM2.5")
if latest.get("Temp", 0) > 38: alerts.append("🌡 อุณหภูมิสูงเกินเกณฑ์")

# =====================================================
# ฟังก์ชันคำนวณ KPI
# =====================================================
