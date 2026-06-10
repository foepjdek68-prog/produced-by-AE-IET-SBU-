import streamlit as st
import plotly.express as px

from utils.database import load_data
from utils.calculator import emission_score

df = load_data()

st.title("📊 Dashboard")

if df.empty:

    st.warning("ไม่มีข้อมูล")

else:

    latest = df.iloc[-1]

    c1,c2,c3,c4 = st.columns(4)

    c1.metric("CO₂", round(latest["CO2"],1))
    c2.metric("CH₄", round(latest["CH4"],1))
    c3.metric("NO₂", round(latest["NO2"],1))
    c4.metric("PM2.5", round(latest["PM25"],1))

    st.metric(
        "GHG Score",
        emission_score(df)
    )

    selected = st.selectbox(
        "เลือกตัวแปร",
        ["CO2","CH4","NO2","PM25"]
    )

    fig = px.line(
        df,
        x="Date",
        y=selected,
        template="plotly_dark"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )
