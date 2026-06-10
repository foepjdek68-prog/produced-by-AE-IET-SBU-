import streamlit as st
import plotly.express as px
from datetime import datetime

from utils.database import load_data, save_data
from utils.api_loader import fetch_data

# ------------------------
# Page Config
# ------------------------

st.set_page_config(
    page_title="Dashboard Tracking Greenhouse Gases Emission",
    page_icon="🌍",
    layout="wide"
)

# ------------------------
# Sidebar
# ------------------------

with st.sidebar:
    st.header("📋 เมนู")

# ------------------------
# Load Data
# ------------------------

df = load_data()

if df.empty:
    df = fetch_data()
    save_data(df)

latest = df.iloc[-1]

# ------------------------
# Thai Date
# ------------------------

date_obj = datetime.fromisoformat(
    str(latest["Date"]).replace("Z", "")
)

thai_date = (
    f"{date_obj.day:02d}/"
    f"{date_obj.month:02d}/"
    f"{(date_obj.year + 543) % 100:02d}"
)

# ------------------------
# Header
# ------------------------

st.title("Dashboard Tracking")

st.subheader("Greenhouse Gases Emission")

st.caption(
    "ระบบรายงานและติดตามก๊าซเรือนกระจกอัจฉริยะ"
)

st.caption(
    f"ข้อมูลล่าสุด : {thai_date}"
)

st.markdown("---")

# ------------------------
# KPI
# ------------------------

c1, c2, c3, c4, c5, c6 = st.columns(6)

c1.metric("CO₂", round(latest["CO2"], 1))
c2.metric("CH₄", round(latest["CH4"], 1))
c3.metric("NO₂", round(latest["NO2"], 1))
c4.metric("PM2.5", round(latest["PM25"], 1))
c5.metric("อุณหภูมิ", round(latest["Temp"], 1))
c6.metric("ความชื้น", round(latest["Humidity"], 1))

st.markdown("---")

# ------------------------
# Graph + Overview
# ------------------------

left, right = st.columns([4, 1])

with left:

    st.subheader("📈 กราฟแสดงข้อมูล")

    options = {
        "CO₂ - Carbon Dioxide (ก๊าซคาร์บอนไดออกไซด์)": "CO2",
        "CH₄ - Methane (ก๊าซมีเทน)": "CH4",
        "NO₂ - Nitrogen Dioxide (ก๊าซไนโตรเจนไดออกไซด์)": "NO2",
        "PM2.5 - ฝุ่นละอองขนาดเล็ก": "PM25",
        "Temperature - อุณหภูมิ": "Temp",
        "Humidity - ความชื้นสัมพัทธ์": "Humidity"
    }

    selected_label = st.selectbox(
        "เลือกข้อมูล",
        list(options.keys())
    )

    selected = options[selected_label]

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
        round(df[selected].mean(), 2)
    )

    st.metric(
        "ค่าสูงสุด",
        round(df[selected].max(), 2)
    )
