from PIL import Image
import streamlit as st
import plotly.express as px
import pandas as pd

from Services.database import load_data, save_data
from Services.api_loader import fetch_data


# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(
    page_title="Dashboard Tracking Greenhouse Gases Emission",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

with st.sidebar:

    st.markdown(
        """
        <div style="
            text-align:center;
            padding:25px;
            border-radius:15px;
            border:2px dashed #4B5563;
            background:#111827;
        ">
            <h2>🌍 GHG MONITOR</h2>
            <p>Greenhouse Gas Dashboard</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("---")

    st.caption("Monitoring System")

    st.write("📡 Real-time Tracking")
    st.write("🌡 Environmental Data")
    st.write("📊 Emission Analysis")

    st.markdown("---")

    st.caption("Version 1.0")

st.markdown(
    """
    <style>
    [data-testid="stMetric"]{
        background:#111827;
        border:1px solid #374151;
        padding:15px;
        border-radius:12px;
    }

    .block-container{
        padding-top:1rem;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# =====================================================
# LOAD DATA
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

alerts = []

if latest["CO2"] > 500:
    alerts.append("🔴 High CO₂ Level")

if latest["PM25"] > 35:
    alerts.append("⚠ PM2.5 Warning")

if latest["Temp"] > 38:
    alerts.append("🌡 High Temperature")

# =====================================================
# HEADER
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
        <h1>🌍 Greenhouse Gas Monitoring Dashboard</h1>
        <p>Last Update : {thai_date}</p>
    </div>
    """,
    unsafe_allow_html=True
)

# =====================================================
# KPI FUNCTION
# =====================================================

def kpi(col, symbol, name=None):
    now = pd.to_numeric(latest.get(col, 0), errors="coerce")
    old = pd.to_numeric(prev.get(col, 0), errors="coerce")

    now = 0 if pd.isna(now) else float(now)
    old = 0 if pd.isna(old) else float(old)

    diff = now - old

    arrow = (
        "↑" if diff > 0
        else "↓" if diff < 0
        else "→"
    )

    label = f"{symbol} ({name})" if name else symbol

    return now, f"{arrow} {diff:.2f}", label


# =====================================================
# KPI CARDS
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

v, d, label = kpi("Temp", "Temperature")
c5.metric(label, f"{v:.2f}", d)

v, d, label = kpi("Humidity", "Humidity")
c6.metric(label, f"{v:.2f}", d)

if alerts:

    cols = st.columns(len(alerts))

    for i, alert in enumerate(alerts):

        if "🔴" in alert:
            cols[i].error(alert)
        else:
            cols[i].warning(alert)

else:
    st.success("🟢 Environmental Condition Normal")

st.markdown("---")


# =====================================================
# PERIOD FILTER
# =====================================================

period = st.selectbox(
    "ช่วงการแสดงผล",
    ["Daily", "Weekly", "Monthly", "Annual"]
)

if period == "Daily":
    df_plot = df.tail(24)

elif period == "Weekly":
    df_plot = df.tail(24 * 7)

elif period == "Monthly":
    df_plot = df.tail(24 * 30)

else:
    df_plot = df


# =====================================================
# MAIN LAYOUT
# =====================================================

center, right = st.columns([4, 1.2])


# =====================================================
# GRAPH SECTION
# =====================================================

with center:

    st.subheader("📈 กราฟแสดงข้อมูล")

    graph_mode = st.radio(
        "โหมดการแสดงผล",
        ["Actual Values", "Comparison Mode"],
        horizontal=True
    )

    options = {
        "CO₂ (Carbon Dioxide)": "CO2",
        "CH₄ (Methane)": "CH4",
        "NO₂ (Nitrogen Dioxide)": "NO2",
        "PM 2.5 (Particulate Matter)": "PM25",
        "Temp (Temperature)": "Temp",
        "Humidity (Relative Humidity)": "Humidity"
    }

    short_name = {
        "CO2": "CO2",
        "CH4": "CH4",
        "NO2": "NO2",
        "PM25": "PM25",
        "Temp": "Temp",
        "Humidity": "Humidity"
    }

    full_name = {
        "CO2": "Carbon Dioxide",
        "CH4": "Methane",
        "NO2": "Nitrogen Dioxide",
        "PM25": "PM2.5",
        "Temp": "Temperature",
        "Humidity": "Relative Humidity"
    }

    if graph_mode == "Actual Values":

        selected_ui = st.selectbox(
            "เลือกข้อมูล",
            list(options.keys())
        )

        selected = [options[selected_ui]]
        legend_map = full_name

    else:

        selected_ui = st.multiselect(
            "เลือกข้อมูล",
            list(options.keys()),
            default=[list(options.keys())[0]]
        )

        selected = [options[x] for x in selected_ui]

        if not selected:
            st.warning("กรุณาเลือกอย่างน้อย 1 ตัวแปร")
            st.stop()

        legend_map = short_name

    plot_df = df_plot.copy()

    if graph_mode == "Comparison Mode":

        scale = {
            "CO2": 1000,
            "CH4": 100,
            "NO2": 100,
            "PM25": 100,
            "Temp": 50,
            "Humidity": 100
        }

        for col in selected:
            plot_df[col] = (
                pd.to_numeric(plot_df[col], errors="coerce")
                .fillna(0)
            )

            plot_df[col] = (
                plot_df[col] / scale[col]
            ) * 100

    fig = px.line(
        plot_df,
        x="Date",
        y=selected,
        markers=True,
        template="plotly_dark"
    )

    color_map = {
        "CO2": "#DC2626",
        "CH4": "#F97316",
        "NO2": "#7C3AED",
        "PM25": "#EAB308",
        "Temp": "#22C55E",
        "Humidity": "#2563EB"
    }

    for trace in fig.data:
        key = trace.name
        trace.line.color = color_map.get(key, "#FFFFFF")
        trace.line.width = 3
        trace.name = legend_map.get(key, key)

    fig.update_layout(
    height=550,
    hovermode="x unified",
    legend_title_text=""
)

    st.plotly_chart(fig, use_container_width=True)


# =====================================================
# STATUS PANEL
# =====================================================

with right:

    st.subheader("📊 สถานะระบบ")

    required_cols = [
        "CO2",
        "CH4",
        "NO2",
        "PM25",
        "Temp",
        "Humidity"
    ]

    missing = [
        c for c in required_cols
        if c not in df.columns or df[c].isna().all()
    ]

    if df.empty:
        st.error("🔴 ระบบผิดปกติ: ไม่มีข้อมูล")

    elif len(df) < 2:
        st.error("🔴 ระบบผิดปกติ: ข้อมูลไม่เพียงพอ")

    elif missing:
        st.error(
            f"🔴 ข้อมูลขาดหาย: {', '.join(missing)}"
        )

    else:

    st.success("🟢 SYSTEM ONLINE")

    st.metric(
        "Records",
        len(df)
    )

    st.metric(
        "Last Update",
        latest["Date"].strftime("%H:%M")
    )

    st.metric(
        "Data Status",
        "Healthy"
    )
