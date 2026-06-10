import streamlit as st
import plotly.express as px

from utils.database import load_data, save_data
from utils.api_loader import fetch_data

st.set_page_config(
    page_title="Dashboard Tracking Greenhouse Gases Emission",
    page_icon="🌍",
    layout="wide"
)

# -------------------
# Load Data
# -------------------

df = load_data()

if df.empty:
    df = fetch_data()
    save_data(df)

latest = df.iloc[-1]

# -------------------
# Header
# -------------------

st.title("🌍 Dashboard Tracking Greenhouse Gases Emission")

st.caption(
    "ระบบรายงานและติดตามก๊าซเรือนกระจกอัจฉริยะ"
)

st.markdown("---")

# -------------------
# KPI
# -------------------

c1,c2,c3,c4,c5,c6 = st.columns(6)

c1.metric("CO₂", round(latest["CO2"],1))
c2.metric("CH₄", round(latest["CH4"],1))
c3.metric("NO₂", round(latest["NO2"],1))
c4.metric("PM2.5", round(latest["PM25"],1))
c5.metric("Temp", round(latest["Temp"],1))
c6.metric("Humidity", round(latest["Humidity"],1))

st.markdown("---")

# -------------------
# Graph + Summary
# -------------------

left,right = st.columns([4,1])

with left:

    st.subheader("📈 Emission Trend")

    selected = st.selectbox(
        "เลือกข้อมูล",
        ["CO2","CH4","NO2","PM25","Temp","Humidity"]
    )

    fig = px.line(
        df.tail(168),
        x="Date",
        y=selected,
        template="plotly_dark"
    )

    fig.update_layout(
        height=520,
        margin=dict(
            l=10,
            r=10,
            t=20,
            b=10
        )
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

with right:

    st.subheader("📊 Overview")

    st.metric(
        "Last Update",
        str(df.iloc[-1]["Date"])[:16]
    )

    st.metric(
        "Records",
        len(df)
    )

    st.metric(
        "Average",
        round(df[selected].mean(),2)
    )

    st.metric(
        "Maximum",
        round(df[selected].max(),2)
    )
