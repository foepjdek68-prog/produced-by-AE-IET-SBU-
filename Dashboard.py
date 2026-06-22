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

# รีเฟรชหน้าจออัตโนมัติทุก 60 วินาที
st_autorefresh(interval=60000, key="refresh")

# =====================================================
# ฟังก์ชันโหลดข้อมูล (ใส่ Cache เพื่อความลื่นไหล แต่กำหนดให้เคลียร์ได้)
# =====================================================
@st.cache_data(ttl=30) # ข้อมูลจะถูกรีเฟรชใหม่ทุก 30 วินาที
def get_data_freshly():
    df = load_data()
    if df.empty:
        df = fetch_data()
        if not df.empty:
            save_data(df)
    
    if not df.empty:
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        df = df.dropna(subset=["Date"]).sort_values("Date").reset_index(drop=True)
    return df

# =====================================================
# LOAD DATA
# =====================================================
df = get_data_freshly()

if df.empty:
    st.error("ไม่พบข้อมูลในระบบ กรุณาตรวจสอบการเชื่อมต่อฐานข้อมูล")
    st.stop()

# ข้อมูลล่าสุด
latest = df.iloc[-1]
prev = df.iloc[-2] if len(df) > 1 else latest
# เปลี่ยน format เป็นวินาทีเพื่อให้เห็นว่าระบบขยับตลอดเวลา
latest_str = latest["Date"].strftime("%d/%m/%Y %H:%M:%S")

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

# =====================================================
# HEADER
# =====================================================
st.markdown(
    f"""
    <div style="background:linear-gradient(135deg,#111827,#1F2937); padding: 20px 25px; border-radius: 12px; border: 1px solid #374151; margin-bottom: 20px;">
        <h1 style="margin:0; color:white; font-size: 2.2rem; font-weight: 800;">🌍 Dashboard Tracking Greenhouse Gases Emission</h1>
        <div style="margin-top: 12px; padding-top: 8px; border-top: 1px solid #374151;">
            <p style="color:#9CA3AF; margin:0; font-size: 1.05rem;">🕒 อัปเดตล่าสุด : {latest_str}</p>
        </div>
    </div>
    """, unsafe_allow_html=True
)

# =====================================================
# KPI SECTION
# =====================================================
def kpi(col, symbol, name=None):
    now = float(latest.get(col, 0))
    old = float(prev.get(col, 0))
    diff = now - old
    percent = ((diff / old) * 100 if old != 0 else 0)
    arrow = ("↑" if diff > 0 else "↓" if diff < 0 else "→")
    return now, f"{arrow} {percent:.1f}%", f"{symbol} ({name})" if name else symbol

c1, c2, c3, c4, c5, c6 = st.columns(6)
metrics = [("CO2", "CO₂", "Carbon Dioxide"), ("CH4", "CH₄", "Methane"), 
           ("NO2", "NO₂", "Nitrogen Dioxide"), ("PM25", "PM2.5", None), 
           ("Temp", "อุณหภูมิ", None), ("Humidity", "ความชื้น", None)]

for i, (col, sym, name) in enumerate(metrics):
    val, diff, label = kpi(col, sym, name)
    [c1, c2, c3, c4, c5, c6][i].metric(label, f"{val:.2f}", diff)

# =====================================================
# GRAPH SECTION
# =====================================================
period = st.selectbox("เลือกช่วงเวลาการแสดงผล", ["รายวัน", "รายสัปดาห์", "รายเดือน", "รายปี"])
# กรองข้อมูลตาม period
df_plot = df.tail(24) if period == "รายวัน" else df.tail(24*7) if period == "รายสัปดาห์" else df.tail(24*30) if period == "รายเดือน" else df

center, right = st.columns([4, 1.2])

with center:
    st.subheader("📈 กราฟแสดงข้อมูล")
    graph_mode = st.radio("โหมดการแสดงผล", ["ค่าจริง (Actual)", "โหมดเปรียบเทียบ (Comparison)"], horizontal=True)
    options = {"CO₂": "CO2", "CH₄": "CH4", "NO₂": "NO2", "PM 2.5": "PM25", "อุณหภูมิ": "Temp", "ความชื้น": "Humidity"}
    
    sel_ui = st.multiselect("เลือกข้อมูล", list(options.keys()), default=["CO₂"])
    selected = [options[x] for x in sel_ui]

    if selected:
        plot_df = df_plot.copy()
        fig = px.line(plot_df, x="Date", y=selected, markers=True, template="plotly_dark")
        fig.update_layout(height=450, hovermode="x unified")
        st.plotly_chart(fig, use_container_width=True)

# =====================================================
# STATUS PANEL (อัปเดตเวลาจริง)
# =====================================================
with right:
    st.subheader("📊 สถานะระบบ")
    st.success("🟢 ระบบออนไลน์ (Normal)")
    st.metric("จำนวนรายการ", len(df))
    # ใช้เวลาจากตัวแปร latest ที่รันใหม่ทุกครั้ง
    st.metric("อัปเดตล่าสุดเมื่อ", latest["Date"].strftime("%H:%M:%S"))
    st.metric("สถานะข้อมูล", "ปกติ")
