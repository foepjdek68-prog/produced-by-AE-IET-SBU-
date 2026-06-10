import streamlit as st
import plotly.express as px
import pandas as pd
from datetime import datetime

from utils.database import load_data

# ======================
# PAGE CONFIG
# ======================

st.set_page_config(
    page_title="Dashboard Tracking",
    page_icon="🌍",
    layout="wide"
)

# ======================
# CSS
# ======================

st.markdown("""
<style>

[data-testid="stMetric"]{
    background:#0f172a;
    border:1px solid #334155;
    padding:15px;
    border-radius:12px;
}

.main .block-container{
    padding-top:1rem;
}

</style>
""", unsafe_allow_html=True)

# ======================
# SIDEBAR
# ======================

with st.sidebar:

    st.markdown("## 📋 เมนู")

    st.markdown("""
    ### 📊 Dashboard

    ใช้สำหรับติดตามและวิเคราะห์ข้อมูล
    ก๊าซเรือนกระจก
    """)

# ======================
# LOAD DATA
# ======================

df = load_data()

if df.empty:

    st.error("ไม่พบข้อมูลในฐานข้อมูล")

    st.stop()

# ======================
# DATE
# ======================

latest = df.iloc[-1]

try:

    date_obj = pd.to_datetime(latest["Date"])

    thai_date = (
        f"{date_obj.day:02d}/"
        f"{date_obj.month:02d}/"
        f"{(date_obj.year + 543)%100:02d}"
    )

except:

    thai_date = "-"

# ======================
# HEADER
# ======================

st.title("Dashboard Tracking")

st.subheader("Greenhouse Gases Emission")

st.caption(
    "ระบบรายงานและติดตามก๊าซเรือนกระจกอัจฉริยะ"
)

st.caption(
    f"ข้อมูลล่าสุด : {thai_date}"
)

st.markdown("---")

# ======================
# KPI
# ======================

c1,c2,c3,c4,c5,c6 = st.columns(6)

c1.metric("CO₂", round(float(latest["CO2"]),1))
c2.metric("CH₄", round(float(latest["CH4"]),1))
c3.metric("NO₂", round(float(latest["NO2"]),1))
c4.metric("PM2.5", round(float(latest["PM25"]),1))
c5.metric("Temp", round(float(latest["Temp"]),1))
c6.metric("Humidity", round(float(latest["Humidity"]),1))

st.markdown("---")

# ======================
# FILTER
# ======================

period = st.selectbox(
    "ช่วงการแสดงผล",
    [
        "Daily",
        "Weekly",
        "Monthly",
        "Annual"
    ]
)

if period == "Daily":

    df_plot = df.tail(24)

elif period == "Weekly":

    df_plot = df.tail(24 * 7)

elif period == "Monthly":

    df_plot = df.tail(24 * 30)

else:

    df_plot = df

# ======================
# GRAPH
# ======================

left,right = st.columns([4,1])

with left:

    st.subheader("📈 กราฟแสดงข้อมูล")

    options = {
        "Carbon Dioxide":"CO2",
        "Methane":"CH4",
        "Nitrogen Dioxide":"NO2",
        "PM2.5":"PM25",
        "Temperature":"Temp",
        "Humidity":"Humidity"
    }

    selected_label = st.selectbox(
        "เลือกข้อมูล",
        list(options.keys())
    )

    selected = options[selected_label]

    fig = px.line(
        df_plot,
        x="Date",
        y=selected,
        template="plotly_dark"
    )

    fig.update_layout(
        height=500,
        margin=dict(
            l=10,
            r=10,
            t=20,
            b=10
        ),
        xaxis_title="วันที่",
        yaxis_title=""
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

with right:

    st.subheader("📊 สรุปข้อมูล")

    st.metric(
        "อัปเดตล่าสุด",
        thai_date
    )

    st.metric(
        "ค่าเฉลี่ย",
        round(df[selected].mean(),2)
    )

    st.metric(
        "ค่าสูงสุด",
        round(df[selected].max(),2)
    )

    avg_co2 = df["CO2"].mean()

    if avg_co2 < 450:

        status = "🟢 ปกติ"

    elif avg_co2 < 500:

        status = "🟡 เฝ้าระวัง"

    else:

        status = "🔴 วิกฤต"

    st.info(status)
