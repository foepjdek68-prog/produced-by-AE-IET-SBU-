import streamlit as st
import plotly.express as px
import pandas as pd
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


df = load_data()

if df.empty:
    df = fetch_data()
    save_data(df)

df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
df = df.dropna(subset=["Date"])

latest = df.iloc[-1]

thai_date = latest["Date"].strftime("%d/%m/%y")


st.info("""
### 🌍 Dashboard Tracking

## Greenhouse Gases Emission
""")

st.caption(f"ข้อมูลล่าสุด : {thai_date}")


prev = df.iloc[-2] if len(df) > 1 else latest


def kpi(col, symbol, name):

    now = float(latest[col])
    old = float(prev[col])

    diff = now - old
    arrow = "↑" if diff > 0 else "↓"

    return now, f"{arrow} {diff:.1f}", f"{symbol} ({name})"


c1, c2, c3, c4, c5, c6 = st.columns(6)

v, d, label = kpi("CO2", "CO₂", "Carbon Dioxide")
c1.metric(label, f"{v:.1f}", d)

v, d, label = kpi("CH4", "CH₄", "Methane")
c2.metric(label, f"{v:.1f}", d)

v, d, label = kpi("NO2", "NO₂", "Nitrogen Dioxide")
c3.metric(label, f"{v:.1f}", d)

v, d, label = kpi("PM25", "PM2.5", "Particulate Matter")
c4.metric(label, f"{v:.1f}", d)

v, d, label = kpi("Temp", "Temp", "Temperature")
c5.metric(label, f"{v:.1f}", d)

v, d, label = kpi("Humidity", "Hum", "Relative Humidity")
c6.metric(label, f"{v:.1f}", d)

c1.metric("CO2", round(float(latest["CO2"]), 1))
c2.metric("CH4", round(float(latest["CH4"]), 1))
c3.metric("NO2", round(float(latest["NO2"]), 1))
c4.metric("PM25", round(float(latest["PM25"]), 1))
c5.metric("Temp", round(float(latest["Temp"]), 1))
c6.metric("Humidity", round(float(latest["Humidity"]), 1))


st.markdown("---")


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


left, center, right = st.columns([1.2, 3, 1])

with left:

    st.subheader("📊 Summary")

    selected_cols = ["CO2", "CH4", "NO2", "PM25", "Temp", "Humidity"]

    name_thai = {
        "CO2": "คาร์บอนไดออกไซด์",
        "CH4": "มีเทน",
        "NO2": "ไนโตรเจนไดออกไซด์",
        "PM25": "ฝุ่น PM2.5",
        "Temp": "อุณหภูมิ",
        "Humidity": "ความชื้น"
    }

    for col in selected_cols:

        avg = df[col].mean()
        mx = df[col].max()
        trend = df[col].iloc[-1] - df[col].iloc[-5]

        st.metric(
            col,
            round(avg, 2),
            f"max {round(mx,2)}"
        )

        st.caption(f"→ {name_thai[col]} | trend: {'↑' if trend > 0 else '↓'}")


with center:

    st.subheader("📈 Graph")

    graph_mode = st.radio(
        "Mode",
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

    selected = st.multiselect(
        "Select data",
        list(options.keys()),
        default=["CO2"]
    )

    plot_df = df_plot.copy()

    if graph_mode == "Compare":

        scale = {
            "CO2": 1000,
            "CH4": 100,
            "NO2": 100,
            "PM25": 100,
            "Temp": 50,
            "Humidity": 100
        }

        for col in selected:
            plot_df[col] = (plot_df[col] / scale[col]) * 100


    fig = px.line(
        plot_df,
        x="Date",
        y=selected,
        markers=True,
        template="plotly_dark"
    )

    label_map = {
        "CO2": "CH4 (มีเทน)",
        "CH4": "CH4 (มีเทน)",
        "NO2": "NO2 (ไนโตรเจนไดออกไซด์)",
        "PM25": "PM2.5",
        "Temp": "Temp",
        "Humidity": "Humidity"
    }

    color_map = {
        "CO2": "#DC2626",
        "CH4": "#F97316",
        "NO2": "#7C3AED",
        "PM25": "#EAB308",
        "Temp": "#22C55E",
        "Humidity": "#2563EB"
    }

    for t in fig.data:

        k = t.name

        t.line.color = color_map.get(k, "#ffffff")
        t.line.width = 3

        t.name = k + f" ({name_thai.get(k,'')})"

    fig.update_layout(
        hovermode="x unified",
        legend=dict(orientation="h")
    )

    st.plotly_chart(fig, use_container_width=True)


with right:

    st.subheader("📌 Status")

    avg_co2 = df["CO2"].mean()

    if avg_co2 < 450:
        st.success("Normal")
    elif avg_co2 < 500:
        st.warning("Warning")
    else:
        st.error("Critical")
