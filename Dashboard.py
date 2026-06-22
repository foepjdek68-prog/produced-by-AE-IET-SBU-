import streamlit as st
import plotly.express as px
import pandas as pd

from streamlit_autorefresh import st_autorefresh
from Services.database import load_data, save_data
from Services.api_loader import fetch_data

# =====================================================
# การตั้งค่าหน้าจอ
# =====================================================
st.set_page_config(
    page_title="Dashboard Tracking GHGs Emission",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

st_autorefresh(interval=60000, key="refresh")

# =====================================================
# LOAD & PREPARE DATA
# =====================================================
@st.cache_data(ttl=30)
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
# SIDEBAR & CSS
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

st.markdown(
    f"""
    <div style="
        background:linear-gradient(135deg,#0f172a,#1e293b);
        padding:20px;
        border-radius:12px;
        border:1px solid #334155;
        margin-bottom:20px;
    ">
        <h1 style="margin:0;color:white;">
            🌍 Dashboard Tracking Greenhouse Gases Emission
        </h1>
        <p style="margin-top:8px;color:#cbd5e1;">
            🕒 อัปเดตล่าสุด : {latest_str}
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown("""
<style>

/* =====================================================
   MAIN BACKGROUND
===================================================== */

.stApp {
    background: #030712;
}

.block-container {
    padding-top: 1rem;
}

/* =====================================================
   SIDEBAR
===================================================== */

section[data-testid="stSidebar"] {
    background: #0f172a !important;
    border-right: 1px solid #334155;
}

section[data-testid="stSidebar"] * {
    color: #ffffff !important;
}

/* =====================================================
   KPI CARDS
===================================================== */

[data-testid="stMetric"] {
    background: #0f172a !important;
    border: 1px solid #60a5fa !important;
    border-radius: 12px !important;
    padding: 15px !important;
    text-align: center;
}

[data-testid="stMetricLabel"] {
    color: #cbd5e1 !important;
    font-weight: 600 !important;
}

[data-testid="stMetricValue"] {
    color: #ffffff !important;
    font-weight: 700 !important;
}

[data-testid="stMetricDelta"] {
    color: #22c55e !important;
}

/* =====================================================
   INPUT COMPONENTS
===================================================== */

.stSelectbox > div > div {
    background: #111827 !important;
    color: #ffffff !important;
}

.stMultiSelect > div > div {
    background: #111827 !important;
    color: #ffffff !important;
}

.
