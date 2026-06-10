import streamlit as st
import plotly.express as px

from utils.database import load_data, save_data
from utils.api_loader import fetch_data

st.set_page_config(
    page_title="Smart Environmental Monitoring Dashboard",
    page_icon="🌍",
    layout="wide"
)

# --------------------------
# Load Data
# --------------------------

df = load_data()

if df.empty:
    df = fetch_data()
    save_data(df)

latest = df.iloc[-1]

# --------------------------
# Header
# --------------------------

st.title("🌍 Smart Environmental Monitoring Dashboard")
st.caption("Integrated Environmental Monitoring Platform")

# --------------------------
# KPI
# --------------------------

k1,k2,k3,k4,k5,k6 = st.columns(6)

k1.metric("CO₂", round(latest["CO2"],1))
k2.metric("CH₄", round(latest["CH4"],1))
k3.metric("NO₂", round(latest["NO2"],1))
k4.metric("PM2.5", round(latest["PM25"],1))
k5.metric("Temp (°C)", round(latest["Temp"],1))
k6.metric("Humidity (%)", round(latest["Humidity"],1))

st.markdown("---")

# --------------------------
# Graph + Summary
# --------------------------

left,right = st.columns([4,1])

with left:

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

    fig.update_layout(
        height=500,
        margin=dict(l=10,r=10,t=30,b=10)
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

with right:

    st.subheader("📊 Summary")

    st.metric(
        "Average",
        round(df[selected].mean(),2)
    )

    st.metric(
        "Maximum",
        round(df[selected].max(),2)
    )

    st.metric(
        "Minimum",
        round(df[selected].min(),2)
    )

    st.metric(
        "Records",
        len(df)
    )

st.markdown("---")

# --------------------------
# Latest Data
# --------------------------

st.subheader("📄 Latest Records")

st.dataframe(
    df.tail(10),
    use_container_width=True
)
