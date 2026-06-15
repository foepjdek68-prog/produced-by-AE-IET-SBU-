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


# ---------------- DATA LOAD ----------------
df = load_data()

if df.empty:
    df = fetch_data()
    save_data(df)

df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
df = df.dropna(subset=["Date"]).sort_values("Date").reset_index(drop=True)

latest = df.iloc[-1]
prev = df.iloc[-2] if len(df) > 1 else latest

thai_date = latest["Date"].strftime("%d/%m/%y")


# ---------------- HEADER ----------------
st.info("""
### 🌍 Dashboard Tracking

## Greenhouse Gases Emission
""")

st.caption(f"ข้อมูลล่าสุด : {thai_date}")


# ---------------- KPI FUNCTION ----------------
def kpi(col, symbol, name):
    now = float(latest[col])
    old = float(prev[col])

    diff = now - old

    if diff > 0:
        arrow = "↑"
    elif diff < 0:
        arrow = "↓"
    else:
        arrow = "→"

    return now, f"{arrow} {diff:.2f}", f"{symbol} ({name})"


# ---------------- KPI UI ----------------
c1, c2, c3, c4, c5, c6 = st.columns(6)

v, d, label = kpi("CO2", "CO₂", "Carbon Dioxide")
c1.metric(label, f"{v:.2f}", d)

v, d, label = kpi("CH4", "CH₄", "Methane")
c2.metric(label, f"{v:.2f}", d)

v, d, label = kpi("NO2", "NO₂", "Nitrogen Dioxide")
c3.metric(label, f"{v:.2f}", d)

v, d, label = kpi("PM25", "PM2.5", "Particulate Matter")
c4.metric(label, f"{v:.2f}", d)

v, d, label = kpi("Temp", "Temp", "Temperature")
c5.metric(label, f"{v:.2f}", d)

v, d, label = kpi("Humidity", "ฑ็", "Humidity")
c6.metric(label, f"{v:.2f}", d)

st.markdown("---")


# ---------------- PERIOD SELECT ----------------
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
left, center, right = st.columns([1.2, 3, 1])

# ---------------- SUMMARY ----------------
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

        if len(df[col]) > 5:
            trend = df[col].iloc[-1] - df[col].iloc[-5]
        else:
            trend = df[col].iloc[-1] - df[col].iloc[0]

        st.metric(
            label=col,
            value=round(avg, 2),
            delta=f"max {round(mx,2)}"
        )

        st.caption(
            f"→ {name_thai[col]} | trend: {'↑' if trend > 0 else '↓'}"
        )


# ---------------- GRAPH ----------------
with center:
    st.subheader("📈 Graph")

    graph_mode = st.radio(
        "Mode",
        ["Actual", "Compare"],
        horizontal=True
    )

    selected = st.multiselect(
        "Select data",
        ["CO2", "CH4", "NO2", "PM25", "Temp", "Humidity"],
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

    name_thai = {
        "CO2": "CO₂",
        "CH4": "CH₄",
        "NO2": "NO₂",
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
        t.name = f"{k} ({name_thai.get(k,'')})"

    fig.update_layout(
        hovermode="x unified",
        legend=dict(orientation="h")
    )

    st.plotly_chart(fig, use_container_width=True)


# ---------------- STATUS ----------------
with right:
    st.subheader("📌 Status")

    avg_co2 = df["CO2"].mean()

    if avg_co2 < 450:
        st.success("Normal")
    elif avg_co2 < 500:
        st.warning("Warning")
    else:
        st.error("Critical")
