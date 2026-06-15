import streamlit as st
import plotly.express as px
import pandas as pd
import pytz
from datetime import datetime

from Services.database import load_data, save_data
from Services.api_loader import fetch_data

st.set_page_config(
    page_title="Dashboard Tracking Greenhouse Gases Emission",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
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
""", unsafe_allow_html=True)

# ---------------- DATA ----------------
df = load_data()

if df.empty:
    df = fetch_data()
    save_data(df)

latest = df.iloc[-1]

date_obj = pd.to_datetime(latest["Date"], utc=True)
date_obj = date_obj.tz_convert("Asia/Bangkok")

thai_date = (
    f"{date_obj.day:02d}/"
    f"{date_obj.month:02d}/"
    f"{(date_obj.year+543)%100:02d}"
)

st.info("""
### 🌍 Dashboard Tracking

## Greenhouse Gases Emission

ระบบรายงานและติดตามก๊าซเรือนกระจกอัจฉริยะ
""")

st.caption(f"ข้อมูลล่าสุด : {thai_date}")

# ---------------- KPI ----------------
c1, c2, c3, c4, c5, c6 = st.columns(6)

c1.metric("CO₂ (Carbon Dioxide)", round(float(latest["CO2"]), 1))
c2.metric("CH₄ (Methane)", round(float(latest["CH4"]), 1))
c3.metric("NO₂ (Nitrogen Dioxide)", round(float(latest["NO2"]), 1))
c4.metric("PM 2.5 (Particulate Matter)", round(float(latest["PM25"]), 1))
c5.metric("Temp (Temperature)", round(float(latest["Temp"]), 1))
c6.metric("Humidity (Relative Humidity)", round(float(latest["Humidity"]), 1))

st.markdown("---")

# ---------------- PERIOD ----------------
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

# ---------------- LAYOUT ----------------
left, right = st.columns([4, 1])

# =========================================================
# 🔥 GRAPH (NEW SYSTEM INSERTED INTO OLD CODE)
# =========================================================
with left:

    st.subheader("📈 กราฟแสดงข้อมูล")

    graph_mode = st.radio(
        "โหมดการแสดงผล",
        ["Actual Values", "Comparison Mode"],
        horizontal=True
    )

    # ใช้แบบ “โค้ดใหม่” แต่รองรับระบบเก่า
    options = {
        "CO2": "CO2",
        "CH4": "CH4",
        "NO2": "NO2",
        "PM25": "PM25",
        "Temp": "Temp",
        "Humidity": "Humidity"
    }

    display_names = {
        "CO2": "CO₂ (Carbon Dioxide)",
        "CH4": "CH₄ (Methane)",
        "NO2": "NO₂ (Nitrogen Dioxide)",
        "PM25": "PM 2.5",
        "Temp": "Temperature",
        "Humidity": "Relative Humidity"
    }

    color_map = {
        "CO2": "#DC2626",
        "CH4": "#F97316",
        "NO2": "#7C3AED",
        "PM25": "#EAB308",
        "Temp": "#22C55E",
        "Humidity": "#2563EB"
    }

    plot_df = df_plot.copy()

    # ---------------- MULTI SELECT (FIXED) ----------------
    selected = st.multiselect(
        "เลือกข้อมูล",
        list(options.keys()),
        default=["CO2"]
    )

    if not selected:
        st.warning("Please select at least one parameter.")
        st.stop()

    # ---------------- SCALE MODE ----------------
    if graph_mode == "Comparison Mode":

        reference_scale = {
            "CO2": 1000,
            "CH4": 100,
            "NO2": 100,
            "PM25": 100,
            "Temp": 50,
            "Humidity": 100
        }

        for col in selected:
            plot_df[col] = pd.to_numeric(plot_df[col], errors="coerce").fillna(0)
            plot_df[col] = (plot_df[col] / reference_scale[col]) * 100

    # ---------------- TIME CLEAN ----------------
    plot_df["Date"] = pd.to_datetime(plot_df["Date"], errors="coerce")
    plot_df = plot_df.sort_values("Date")

    # ---------------- PLOT ----------------
    fig = px.line(
        plot_df,
        x="Date",
        y=selected,
        template="plotly_dark",
        markers=True
    )

    for trace in fig.data:

        col_key = trace.name

        trace.line.color = color_map.get(col_key, "#ffffff")
        trace.line.width = 3

        trace.name = display_names.get(col_key, col_key)

        trace.hovertemplate = "%{y:.2f}<br>%{x|%d/%m/%Y %H:%M}<extra></extra>"

    fig.update_layout(
        legend=dict(orientation="h"),
        hovermode="x unified",
        xaxis=dict(type="date")
    )

    if graph_mode == "Actual Values":
        fig.update_yaxes(title_text="Actual Value")
    else:
        fig.update_yaxes(title_text="Relative Scale (%)", range=[0, 100])

    st.plotly_chart(fig, use_container_width=True)

# ---------------- RIGHT PANEL (OLD 그대로) ----------------
with right:

    st.subheader("📊 สรุปข้อมูล")

    name_map = {
        "CO2": "CO₂",
        "CH4": "CH₄",
        "NO2": "NO₂",
        "PM25": "PM 2.5",
        "Temp": "Temperature",
        "Humidity": "Humidity"
    }

    for col in ["CO2", "CH4", "NO2", "PM25", "Temp", "Humidity"]:

        st.metric(
            f"AVG {name_map[col]}",
            round(df[col].mean(), 2)
        )

        st.metric(
            f"MAX {name_map[col]}",
            round(df[col].max(), 2)
        )

    avg_co2 = df["CO2"].mean()

    if avg_co2 < 450:
        st.success("🟢 Normal")
    elif avg_co2 < 500:
        st.warning("🟡 Warning")
    else:
        st.error("🔴 Critical")
