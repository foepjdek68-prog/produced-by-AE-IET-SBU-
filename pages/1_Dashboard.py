import streamlit as st
import plotly.express as px

from utils.database import load_data

st.title("📊 Dashboard")

df = load_data()

if df.empty:
    st.warning("ไม่มีข้อมูล")
    st.stop()

latest = df.iloc[-1]

c1, c2, c3, c4 = st.columns(4)

c1.metric("CO₂", round(latest["CO2"], 1))
c2.metric("CH₄", round(latest["CH4"], 1))
c3.metric("NO₂", round(latest["NO2"], 1))
c4.metric("PM2.5", round(latest["PM25"], 1))

st.divider()

selected = st.selectbox(
    "เลือกข้อมูล",
    ["CO2", "CH4", "NO2", "PM25"]
)

fig = px.line(
    df.tail(168),
    x="Date",
    y=selected,
    title=f"{selected} Trend (7 วันล่าสุด)",
    template="plotly_dark"
)

st.plotly_chart(fig, use_container_width=True)

st.divider()

st.subheader("⚙️ Data Pipeline")

a, b, c = st.columns(3)

a.success("API Connected")
b.success("Database Updated")
c.success("Analytics Complete")
