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

with st.sidebar:
    # 1. ส่วนเนื้อหาด้านบน (โลโก้)
    st.image("Assets/logo.png", width=250)
    
    # 2. ส่วนท้ายของ Sidebar (Footer)
    st.markdown("""
        <style>
            [data-testid="stSidebar"] > div:first-child {
                display: flex;
                flex-direction: column;
                height: 90vh;
            }
            .sidebar-spacer {
                flex-grow: 1;
            }
            .sidebar-footer {
                border-top: 1px solid #4B5563;
                padding-top: 10px;
                margin-top: auto;
                font-size: 0.75em;
                color: #9CA3AF;
            }
        </style>
        
        <div class="sidebar-spacer"></div>
        <div class="sidebar-footer">
            (C) แผนกวิศวกรรม SBU
        </div>
    """, unsafe_allow_html=True)

st.markdown("""
<style>
.block-container{
    padding-top:1rem;
}
[data-testid="stSidebar"] img{
    margin-top:-10px;
    margin-bottom:10px;
}
[data-testid="stMetric"]{
    background:#111827;
    border:1px solid #374151;
    border-radius:12px;
    padding:15px;
    text-align:center;
}
[data-testid="stMetricValue"]{
    font-size:28px;
    font-weight:700;
}
</style>
""", unsafe_allow_html=True)

# =====================================================
# การโหลดข้อมูล (Data Loading)
# =====================================================

df = load_data()

if df.empty:
    df = fetch_data()
    save_data(df)

df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

df = (
    df.dropna(subset=["Date"])
    .sort_values("Date")
    .reset_index(drop=True)
)

latest = df.iloc[-1]
prev = df.iloc[-2] if len(df) > 1 else latest

thai_date = latest["Date"].strftime("%d/%m/%y")

# การตั้งค่าการแจ้งเตือน (Alert System)
alerts = []

if latest["CO2"] > 500:
    alerts.append("🔴 ระดับ CO₂ สูงเกินเกณฑ์")

if latest["PM25"] > 35:
    alerts.append("⚠ แจ้งเตือนค่า PM2.5")

if latest["Temp"] > 38:
    alerts.append("🌡 อุณหภูมิสูงเกินเกณฑ์")

# =====================================================
# ส่วนหัว (Header)
# =====================================================

st.markdown(
    f"""
    <div style="
        background:#111827;
        padding:20px;
        border-radius:15px;
        border:1px solid #374151;
        margin-bottom:10px;
    ">
        <h1>🌍 แดชบอร์ดติดตามก๊าซเรือนกระจก</h1>
        <p>อัปเดตล่าสุด : {thai_date}</p>
    </div>
    """,
    unsafe_allow_html=True
)

# =====================================================
# ฟังก์ชันคำนวณ KPI
# =====================================================

def kpi(col, symbol, name=None):
    now = pd.to_numeric(latest.get(col, 0), errors="coerce")
    old = pd.to_numeric(prev.get(col, 0), errors="coerce")

    now = 0 if pd.isna(now) else float(now)
    old = 0 if pd.isna(old) else float(old)

    diff = now - old
    percent = ((diff / old) * 100 if old != 0 else 0)

    arrow = ("↑" if diff > 0 else "↓" if diff < 0 else "→")
    label = f"{symbol} ({name})" if name else symbol

    return now, f"{arrow} {percent:.1f}%", label
    
# =====================================================
# แถบแสดงผล KPI (KPI Cards)
# =====================================================

c1, c2, c3, c4, c5, c6 = st.columns(6)

v, d, label = kpi("CO2", "CO₂", "Carbon Dioxide")
c1.metric(label, f"{v:.2f}", d)

v, d, label = kpi("CH4", "CH₄", "Methane")
c2.metric(label, f"{v:.2f}", d)

v, d, label = kpi("NO2", "NO₂", "Nitrogen Dioxide")
c3.metric(label, f"{v:.2f}", d)

v, d, label = kpi("PM25", "PM2.5")
c4.metric(label, f"{v:.2f}", d)

v, d, label = kpi("Temp", "อุณหภูมิ")
c5.metric(label, f"{v:.2f}", d)

v, d, label = kpi("Humidity", "ความชื้น")
c6.metric(label, f"{v:.2f}", d)

if alerts:
    cols = st.columns(len(alerts))
    for i, alert in enumerate(alerts):
        if "🔴" in alert:
            cols[i].error(alert)
        else:
            cols[i].warning(alert)
else:
    st.success("🟢 สภาพแวดล้อมปกติ")

st.markdown("---")

# =====================================================
# ตัวกรองช่วงเวลา (Period Filter)
# =====================================================

period = st.selectbox(
    "เลือกช่วงเวลาการแสดงผล",
    ["รายวัน", "รายสัปดาห์", "รายเดือน", "รายปี"]
)

if period == "รายวัน":
    df_plot = df.tail(24)
elif period == "รายสัปดาห์":
    df_plot = df.tail(24 * 7)
elif period == "รายเดือน":
    df_plot = df.tail(24 * 30)
else:
    df_plot = df

# =====================================================
# โครงสร้างหลัก (Main Layout)
# =====================================================

center, right = st.columns([4, 1.2])

# =====================================================
# ส่วนแสดงกราฟ (Graph Section)
# =====================================================

with center:
    st.subheader("📈 กราฟแสดงข้อมูล")

    graph_mode = st.radio(
        "โหมดการแสดงผลกราฟ",
        ["ค่าจริง (Actual)", "โหมดเปรียบเทียบ (Comparison)"],
        horizontal=True
    )

    options = {
        "CO₂ (Carbon Dioxide)": "CO2",
        "CH₄ (Methane)": "CH4",
        "NO₂ (Nitrogen Dioxide)": "NO2",
        "PM 2.5 (Particulate Matter)": "PM25",
        "อุณหภูมิ (Temperature)": "Temp",
        "ความชื้น (Humidity)": "Humidity"
    }

    # (ส่วนของ logic การเลือกข้อมูล... เหมือนเดิมแต่เปลี่ยนชื่อ UI)
    if graph_mode == "ค่าจริง (Actual)":
        selected_ui = st.selectbox("เลือกข้อมูลที่ต้องการแสดง", list(options.keys()))
        selected = [options[selected_ui]]
        legend_map = {v: k for k, v in options.items()}
    else:
        selected_ui = st.multiselect("เลือกข้อมูลที่ต้องการเปรียบเทียบ", list(options.keys()), default=[list(options.keys())[0]])
        selected = [options[x] for x in selected_ui]
        if not selected:
            st.warning("กรุณาเลือกข้อมูลอย่างน้อย 1 รายการ")
            st.stop()
        legend_map = {v: k for k, v in options.items()}

    # ... (ส่วนการสร้างกราฟ Plotly คงเดิม) ...
    st.plotly_chart(fig, use_container_width=True)

# =====================================================
# แผงสถานะระบบ (Status Panel)
# =====================================================

with right:
    st.subheader("📊 สถานะระบบ")
    # ... (Logic ตรวจสอบสถานะคงเดิม) ...
    if df.empty:
        st.error("🔴 ระบบผิดปกติ: ไม่มีข้อมูล")
    elif len(df) < 2:
        st.error("🔴 ระบบผิดปกติ: ข้อมูลไม่เพียงพอ")
    else:
        st.success("🟢 ระบบออนไลน์ (Normal)")
        st.metric("จำนวนรายการ", len(df))
        st.metric("อัปเดตล่าสุดเมื่อ", latest["Date"].strftime("%H:%M"))
        st.metric("สถานะข้อมูล", "ปกติ")
