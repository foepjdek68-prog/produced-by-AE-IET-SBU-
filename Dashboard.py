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
    padding:12px;
    border-radius:12px;
}

.block-container{
    padding-top:0.8rem;
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


# =========================
# TOP SUMMARY (MOVING FROM LEFT)
# =========================
st.subheader("📊 Summary Overview")

cols = st.columns(6)

metrics = {
    "CO2": ("CO₂", "คาร์บอนไดออกไซด์"),
    "CH4": ("CH₄", "มีเทน"),
    "NO2": ("NO₂", "ไนโตรเจนไดออกไซด์"),
    "PM25": ("PM2.5", "ฝุ่นละเอียด"),
    "Temp": ("Temp", "อุณหภูมิ"),
    "Humidity": ("Hum", "ความชื้น")
}

for i, key in enumerate(metrics.keys()):

    label, _ = metrics[key]

    prev = df[key].iloc[-6] if len(df) > 6 else df[key].iloc[0]
    now = df[key].iloc[-1]

    trend = now - prev
    arrow = "↑" if trend > 0 else "↓"

    cols[i].metric(
        label,
        round(now, 2),
        f"{arrow} {round(trend, 2)}"
    )


st.markdown("---")


# =========================
# PERIOD
# =========================
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


# =========================
# LAYOUT (GRAPH BIG)
# =========================
left, right = st.columns([5, 1])

with left:

    st.subheader("📈 Graph")

    graph_mode = st.radio(
        "Mode",
        ["Actual Values", "Comparison"],
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
        "เลือกข้อมูล",
        list(options.keys()),
        default=["CO2"]
    )

    plot_df = df_plot.copy()

    if graph_mode == "Comparison":

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
        template="plotly_dark",
        markers=True
    )

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

    fig.update_layout(
        hovermode="x unified",
        legend=dict(orientation="h"),
        height=550
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
