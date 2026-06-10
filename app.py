import streamlit as st
import plotly.express as px
from utils.database import load_data

st.set_page_config(
    page_title="Integrated Environmental Dashboard",
    layout="wide"
)

df = load_data()

if df.empty:
    st.error("No data found")
    st.stop()

latest = df.iloc[-1]

st.title("🌍 Integrated Environmental & GHG Dashboard")
st.caption("Thailand Environmental Monitoring Platform")

st.info(f"Last Update : {latest['Date']}")

# KPI
c1,c2,c3,c4,c5,c6 = st.columns(6)

c1.metric("CO₂", round(latest["CO2"],1))
c2.metric("CH₄", round(latest["CH4"],1))
c3.metric("NO₂", round(latest["NO2"],1))
c4.metric("PM2.5", round(latest["PM25"],1))
c5.metric("Temp", round(latest["Temp"],1))
c6.metric("Humidity", round(latest["Humidity"],1))

st.markdown("---")

# Graph
st.subheader("📈 Environmental Trend")

selected = st.selectbox(
    "Select Parameter",
    ["CO2","CH4","NO2","PM25","Temp","Humidity"]
)

fig = px.line(
    df.tail(168),
    x="Date",
    y=selected,
    template="plotly_dark"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

st.markdown("---")

# Sources + Status
left,right = st.columns(2)

with left:

    st.subheader("🔗 Data Sources")

    st.success("Air4Thai")
    st.success("TMD")

    st.warning("OpenAQ (Planned)")
    st.warning("Sentinel-5P (Planned)")

with right:

    st.subheader("⚙️ System Status")

    st.success("Database Online")
    st.success("Dashboard Active")
    st.success("Analytics Ready")

st.markdown("---")

# Objective
st.subheader("📌 Project Objective")

st.info("""
พัฒนา Web Dashboard เพื่อรวบรวมและเชื่อมโยงข้อมูลมลพิษ
จากหลายแหล่งมาไว้ในที่เดียว

ช่วยให้สามารถติดตามและเฝ้าระวังสถานการณ์
ด้านสิ่งแวดล้อมได้อย่างมีประสิทธิภาพ
""")

st.markdown("---")

# Team
st.caption("""
👨‍💻 Developed By

- Member 1
- Member 2
- Member 3

Engineering Project
""")
