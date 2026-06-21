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
thai_date = latest["Date"].strftime("%d/%m/%y")

# =====================================================
# HEADER & ALERTS
# =====================================================
st.markdown(f"""
    <div style="background:#111827; padding:20px; border-radius:15px; border:1px solid #374151; margin-bottom:10px;">
        <h1>🌍 Dashboard Tracking </h1>
        <h1> Greenhouse Gases Emission </h1>
        <p>อัปเดตล่าสุด : {thai_date}</p>
    </div>
""", unsafe_allow_html=True)

alerts = []
if latest.get("CO2", 0) > 500: alerts.append("🔴 ระดับ CO₂ สูงเกินเกณฑ์")
if latest.get("PM25", 0) > 35: alerts.append("⚠ แจ้งเตือนค่า PM2.5")
if latest.get("Temp", 0) > 38: alerts.append("🌡 อุณหภูมิสูงเกินเกณฑ์")

# =====================================================
# ฟังก์ชันคำนวณ KPI
# =====================================================
def kpi(col, symbol, name=None):
    now = pd.to_numeric(latest.get(col, 0), errors="coerce")
    old = pd.to_numeric(prev.get(col, 0), errors="coerce")
    now, old = (0.0 if pd.isna(now) else float(now)), (0.0 if pd.isna(old) else float(old))
    diff = now - old
    percent = ((diff / old) * 100 if old != 0 else 0)
    arrow = ("↑" if diff > 0 else "↓" if diff < 0 else "→")
    return now, f"{arrow} {percent:.1f}%", f"{symbol} ({name})" if name else symbol
    
# =====================================================
# KPI CARDS
# =====================================================
c1, c2, c3, c4, c5, c6 = st.columns(6)
metrics = [("CO2", "CO₂", "Carbon Dioxide"), ("CH4", "CH₄", "Methane"), 
           ("NO2", "NO₂", "Nitrogen Dioxide"), ("PM25", "PM2.5", None), 
           ("Temp", "อุณหภูมิ", None), ("Humidity", "ความชื้น", None)]

for i, (col, sym, name) in enumerate(metrics):
    val, diff, label = kpi(col, sym, name)
    [c1, c2, c3, c4, c5, c6][i].metric(label, f"{val:.2f}", diff)

if alerts:
    cols = st.columns(len(alerts))
    for i, alert in enumerate(alerts):
        cols[i].error(alert) if "🔴" in alert else cols[i].warning(alert)
else:
    st.success("🟢 สภาพแวดล้อมปกติ")

st.markdown("---")

# =====================================================
# GRAPH SECTION
# =====================================================
period = st.selectbox("เลือกช่วงเวลาการแสดงผล", ["รายวัน", "รายสัปดาห์", "รายเดือน", "รายปี"])
df_plot = df.tail(24) if period == "รายวัน" else df.tail(24*7) if period == "รายสัปดาห์" else df.tail(24*30) if period == "รายเดือน" else df

center, right = st.columns([4, 1.2])

with center:
    st.subheader("📈 กราฟแสดงข้อมูล")
    graph_mode = st.radio("โหมดการแสดงผลกราฟ", ["ค่าจริง (Actual)", "โหมดเปรียบเทียบ (Comparison)"], horizontal=True)
    options = {"CO₂ (Carbon Dioxide)": "CO2", "CH₄ (Methane)": "CH4", "NO₂ (Nitrogen Dioxide)": "NO2", 
               "PM 2.5 (Particulate Matter)": "PM25", "อุณหภูมิ (Temperature)": "Temp", "ความชื้น (Humidity)": "Humidity"}

    if graph_mode == "ค่าจริง (Actual)":
        sel_ui = st.selectbox("เลือกข้อมูลที่ต้องการแสดง", list(options.keys()))
        selected = [options[sel_ui]]
    else:
        sel_ui = st.multiselect("เลือกข้อมูลที่ต้องการเปรียบเทียบ", list(options.keys()), default=[list(options.keys())[0]])
        selected = [options[x] for x in sel_ui]
        if not selected: st.warning("กรุณาเลือกข้อมูลอย่างน้อย 1 รายการ"); st.stop()

    plot_df = df_plot.copy()
    for col in selected: plot_df[col] = pd.to_numeric(plot_df[col], errors="coerce").fillna(0)
    
    if graph_mode == "โหมดเปรียบเทียบ (Comparison)":
        scale = {"CO2": 1000, "CH4": 100, "NO2": 100, "PM25": 100, "Temp": 50, "Humidity": 100}
        for col in selected: plot_df[col] = (plot_df[col] / scale.get(col, 1)) * 100

    fig = px.line(plot_df, x="Date", y=selected, markers=True, template="plotly_dark")
    color_map = {"CO2": "#DC2626", "CH4": "#F97316", "NO2": "#7C3AED", "PM25": "#EAB308", "Temp": "#22C55E", "Humidity": "#2563EB"}
    
    for trace in fig.data:
        trace.line.color = color_map.get(trace.name, "#FFFFFF")
        trace.line.width = 3
        # แปลงชื่อคีย์เป็นชื่อภาษาไทยที่แสดงบน Legend
        rev_map = {v: k for k, v in options.items()}
        trace.name = rev_map.get(trace.name, trace.name)

    fig.update_layout(height=550, hovermode="x unified", legend_title_text="")
    st.plotly_chart(fig, use_container_width=True)

# =====================================================
# STATUS PANEL
# =====================================================
with right:
    st.subheader("📊 สถานะระบบ")
    st.success("🟢 ระบบออนไลน์ (Normal)")
    st.metric("จำนวนรายการ", len(df))
    st.metric("อัปเดตล่าสุดเมื่อ", latest["Date"].strftime("%H:%M"))
    st.metric("สถานะข้อมูล", "ปกติ")
