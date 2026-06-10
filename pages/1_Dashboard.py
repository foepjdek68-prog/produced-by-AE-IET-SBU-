import streamlit as st
import plotly.express as px
from utils.database import load_data

df = load_data()

latest = df.iloc[-1]

c1,c2,c3,c4,c5,c6 = st.columns(6)

c1.metric("CO2", round(latest["CO2"],1))
c2.metric("CH4", round(latest["CH4"],1))
c3.metric("NO2", round(latest["NO2"],1))
c4.metric("PM2.5", round(latest["PM25"],1))
c5.metric("Temp", round(latest["Temp"],1))
c6.metric("Humidity", round(latest["Humidity"],1))

selected = st.selectbox("เลือกตัวแปร", ["CO2","CH4","NO2","PM25"])

fig = px.line(df.tail(168), x="Date", y=selected)
st.plotly_chart(fig, use_container_width=True)

def emission_score(df):
    latest = df.iloc[-1]
    return round(
        latest["CO2"]*0.5 +
        latest["CH4"]*0.3 +
        latest["NO2"]*0.2,
        2
    )

st.metric("Emission Score", emission_score(df))

st.subheader("Data Sources")

st.success("Air4Thai")
st.success("TMD")
st.warning("OpenAQ (Planned)")
st.warning("Sentinel-5P (Planned)")

###########
st.markdown("### Project Objective")

st.info("""
รวมข้อมูลมลพิษจากหลายแหล่งมาไว้ใน Dashboard เดียว
เพื่อช่วยการติดตามและวิเคราะห์สิ่งแวดล้อม
""")

st.caption("""
Developed by:
- Member 1
- Member 2
- Member 3
""")
