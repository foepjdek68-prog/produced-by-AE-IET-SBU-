import streamlit as st
import plotly.express as px
from datetime import datetime

from Services.database import load_data, save_data
from Services.api_loader import fetch_data

# =========================
# PAGE CONFIG
# =========================

st.set_page_config(
    page_title="Dashboard Tracking Greenhouse Gases Emission",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================
# SIDEBAR
# =========================

st.sidebar.markdown("## 📋 เมนู")

# =========================
# CSS
# =========================

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

# =========================
# LOAD DATA
# =========================

df = load_data()

if df.empty:

    df = fetch_data()
    save_data(df)

latest = df.iloc[-1]

# =========================
# DATE
# =========================

date_obj = datetime.fromisoformat(
    str(latest["Date"]).replace("Z","")
)

thai_date = (
    f"{date_obj.day:02d}/"
    f"{date_obj.month:02d}/"
    f"{(date_obj.year+543)%100:02d}"
)

# =========================
# HEADER
# =========================

st.info("""
### 🌍 Dashboard Tracking

## Greenhouse Gases Emission

ระบบรายงานและติดตามก๊าซเรือนกระจกอัจฉริยะ
""")

st.caption(f"ข้อมูลล่าสุด : {thai_date}")

# =========================
# KPI
# =========================

c1,c2,c3,c4,c5,c6 = st.columns(6)

c1.metric(
    "Carbon Dioxide",
    round(float(latest["CO2"]),1)
)

c2.metric(
    "Methane",
    round(float(latest["CH4"]),1)
)

c3.metric(
    "Nitrogen Dioxide",
    round(float(latest["NO2"]),1)
)

c4.metric(
    "PM2.5",
    round(float(latest["PM25"]),1)
)

c5.metric(
    "Temperature",
    round(float(latest["Temp"]),1)
)

c6.metric(
    "Humidity",
    round(float(latest["Humidity"]),1)
)

st.markdown("---")

# =========================
# FILTER
# =========================

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

# =========================
# GRAPH
# =========================

left, right = st.columns([4,1])

with left:

    st.subheader("📈 กราฟแสดงข้อมูล")

    options = {

        "Carbon Dioxide": "CO2",

        "Methane": "CH4",

        "Nitrogen Dioxide": "NO2",

        "PM2.5": "PM25",

        "Temperature": "Temp",

        "Humidity": "Humidity"
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
        )
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    descriptions = {

        "CO2":
        "Carbon dioxide from fuel combustion and industrial activities.",

        "CH4":
        "Methane emissions from agriculture and waste.",

        "NO2":
        "Air pollutant from transportation and industry.",

        "PM25":
        "Fine particulate matter affecting health.",

        "Temp":
        "Ambient air temperature.",

        "Humidity":
        "Relative humidity in atmosphere."
    }

    st.info(descriptions[selected])

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

        status = "🟢 Normal"

    elif avg_co2 < 500:

        status = "🟡 Warning"

    else:

        status = "🔴 Critical"

    st.info(
        f"""
สถานะระบบ

{status}
"""
    )
