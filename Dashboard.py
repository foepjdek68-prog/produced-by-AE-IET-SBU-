import streamlit as st
import plotly.express as px
import pandas as pd
from streamlit_autorefresh import st_autorefresh

from Services.database import load_data, save_data
from Services.api_loader import fetch_data

# =====================================================
# CONFIG
# =====================================================
st.set_page_config(
    page_title="Dashboard Tracking GHGs Emission",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# refresh ทุก 15 วินาที (เหมาะกับ Streamlit Cloud)
st_autorefresh(interval=15000, key="refresh")

# =====================================================
# DATA LOADER (REAL-TIME FIX)
# =====================================================
@st.cache_data(ttl=10)
def get_data():

    # 1. ดึงข้อมูลสดก่อน
    try:
        fresh_df = fetch_data()
    except Exception:
        fresh_df = pd.DataFrame()

    # 2. fallback ถ้า API ล่ม
    if fresh_df.empty:
        df = load_data()
    else:
        df = fresh_df
        save_data(df)

    # 3. clean data
    if not df.empty and "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        df = df.dropna(subset=["Date"])
        df = df.sort_values("Date").reset_index(drop=True)

    return df


df = get_data()

# กัน crash
if df is None or df.empty:
    st.error("❌ ไม่มีข้อมูล (API / DB ไม่ตอบสนอง)")
    st.stop()

latest = df.iloc[-1]
prev = df.iloc[-2] if len(df) > 1 else latest

latest_str = latest["Date"].strftime("%d/%m/%Y %H:%M:%S")

# =====================================================
# HEADER
# =====================================================
col1, col2 = st.columns([8, 1])

with col1:
    st.markdown(f"""
    <div style="
        background:linear-gradient(135deg,#0f172a,#1e293b);
        padding:18px;
        border-radius:12px;
        border:1px solid #334155;
    ">
        <h2 style="color:white;margin:0;">
            🌍 GHG Dashboard
        </h2>
        <p style="color:#cbd5e1;margin:5px 0 0 0;">
            🕒 Last update: {latest_str}
        </p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    if st.button("🔄 Refresh"):
        st.cache_data.clear()
        st.rerun()

st.markdown("---")

# =====================================================
# ALERT SYSTEM
# =====================================================
alerts = []

if latest.get("CO2", 0) > 500:
    alerts.append("🔴 CO₂ สูง")
if latest.get("PM25", 0) > 35:
    alerts.append("⚠ PM2.5 สูง")
if latest.get("Temp", 0) > 38:
    alerts.append("🌡 อุณหภูมิสูง")

if alerts:
    cols = st.columns(len(alerts))
    for i, a in enumerate(alerts):
        cols[i].warning(a)
else:
    st.success("🟢 ปกติทั้งหมด")

# =====================================================
# KPI
# =====================================================
def kpi(col, symbol):
    now = float(latest.get(col, 0))
    old = float(prev.get(col, 0))
    diff = now - old
    percent = (diff / old * 100) if old != 0 else 0
    arrow = "↑" if diff > 0 else "↓" if diff < 0 else "→"
    return now, f"{arrow} {percent:.1f}%", symbol


c1, c2, c3, c4, c5, c6 = st.columns(6)

metrics = [
    ("CO2", "CO₂"),
    ("CH4", "CH₄"),
    ("NO2", "NO₂"),
    ("PM25", "PM2.5"),
    ("Temp", "Temp"),
    ("Humidity", "Humidity")
]

for i, (col, sym) in enumerate(metrics):
    val, diff, label = kpi(col, sym)
    [c1, c2, c3, c4, c5, c6][i].metric(label, f"{val:.2f}", diff)

st.markdown("---")

# =====================================================
# GRAPH
# =====================================================
period = st.selectbox(
    "ช่วงเวลา",
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

# กัน lag (สำคัญมากบน Streamlit Cloud)
MAX_POINTS = 800
if len(df_plot) > MAX_POINTS:
    df_plot = df_plot.tail(MAX_POINTS)

center, right = st.columns([4, 1.2])

with center:

    st.subheader("📈 Graph")

    graph_mode = st.radio(
        "โหมด",
        ["Actual", "Compare"],
        horizontal=True
    )

    options = {
        "CO2": "CO2",
        "CH4": "CH4",
        "NO2": "NO2",
        "PM25": "PM25",
        "Temp": "Temp",
        "Humidity": "Humidity"
    }

    if graph_mode == "Actual":
        sel = st.selectbox("เลือก", list(options.keys()))
        selected = [sel]
    else:
        selected = st.multiselect(
            "เลือก",
            list(options.keys()),
            default=["CO2", "CH4"]
        )
        if not selected:
            st.warning("เลือกอย่างน้อย 1 ค่า")
            st.stop()

    plot_df = df_plot.copy()

    fig = px.line(
        plot_df,
        x="Date",
        y=selected,
        markers=False,   # ลด lag
        template="plotly_white"
    )

    color_map = {
        "CO2": "#ef4444",
        "CH4": "#f97316",
        "NO2": "#8b5cf6",
        "PM25": "#eab308",
        "Temp": "#22c55e",
        "Humidity": "#3b82f6"
    }

    for t in fig.data:
        t.line.width = 3
        t.line.color = color_map.get(t.name, "#111827")

    fig.update_layout(
        height=520,
        hovermode="x unified",
        paper_bgcolor="white",
        plot_bgcolor="white"
    )

    st.plotly_chart(fig, use_container_width=True)

# =====================================================
# STATUS PANEL
# =====================================================
with right:
    st.subheader("📊 Status")

    delay = (pd.Timestamp.now() - latest["Date"]).total_seconds()

    if delay < 60:
        status = "🟢 Live"
    elif delay < 300:
        status = "🟡 Delayed"
    else:
        status = "🔴 Offline"

    st.metric("Status", status)
    st.metric("Rows", len(df))
    st.metric("Last update", latest["Date"].strftime("%H:%M:%S"))
