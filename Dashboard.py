import streamlit as st
import plotly.express as px
import pandas as pd

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


st.title("🌍 GHG Dashboard")


# =========================
# KPI SECTION (ORIGINAL STYLE)
# =========================
st.markdown("## 📊 Summary")

c1, c2, c3, c4, c5, c6 = st.columns(6)

c1.metric("CO2", round(float(latest["CO2"]), 2))
c2.metric("CH4", round(float(latest["CH4"]), 2))
c3.metric("NO2", round(float(latest["NO2"]), 2))
c4.metric("PM25", round(float(latest["PM25"]), 2))
c5.metric("Temp", round(float(latest["Temp"]), 2))
c6.metric("Humidity", round(float(latest["Humidity"]), 2))

st.markdown("---")


# =========================
# FILTER
# =========================
period = st.selectbox(
    "ช่วงเวลา",
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
# GRAPH (ORIGINAL STRUCTURE)
# =========================
st.markdown("## 📈 Graph")

graph_mode = st.radio(
    "Mode",
    ["Actual Values", "Comparison Mode"],
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
        plot_df[col] = (plot_df[col] / scale[col]) * 100


fig = px.line(
    plot_df,
    x="Date",
    y=selected,
    template="plotly_dark",
    markers=True
)

colors = {
    "CO2": "#DC2626",
    "CH4": "#F97316",
    "NO2": "#7C3AED",
    "PM25": "#EAB308",
    "Temp": "#22C55E",
    "Humidity": "#2563EB"
}

for t in fig.data:
    t.line.color = colors.get(t.name, "#fff")
    t.line.width = 3

fig.update_layout(
    hovermode="x unified",
    legend=dict(orientation="h"),
)

st.plotly_chart(fig, use_container_width=True)


# =========================
# STATUS (ORIGINAL POSITION)
# =========================
avg_co2 = df["CO2"].mean()

st.markdown("---")
st.subheader("📌 Status")

if avg_co2 < 450:
    st.success("Normal")
elif avg_co2 < 500:
    st.warning("Warning")
else:
    st.error("Critical")
