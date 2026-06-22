import streamlit as st
import plotly.express as px
import pandas as pd

from streamlit_autorefresh import st_autorefresh

from Services.database import load_data
from Services.api_loader import fetch_data


# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(
    page_title="Dashboard Tracking GHGs Emission",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)


# refresh ทุก 15 วินาที

st_autorefresh(
    interval=15000,
    key="refresh"
)



# =====================================================
# STYLE
# =====================================================

st.markdown("""
<style>

.stApp {

background:#030712;

}


section[data-testid="stSidebar"] {

background:#0f172a !important;

}


section[data-testid="stSidebar"] * {

color:white !important;

}


[data-testid="stMetric"] {

background:#0f172a !important;

border:1px solid #38bdf8 !important;

border-radius:12px;

padding:15px;

}


[data-testid="stMetricLabel"] {

color:#cbd5e1 !important;

}


[data-testid="stMetricValue"] {

color:white !important;

}


hr {

border-color:#334155;

}

</style>
""",
unsafe_allow_html=True)



# =====================================================
# SIDEBAR
# =====================================================

with st.sidebar:

    st.image(
        "Assets/logo.png",
        width=250
    )


    st.markdown("""
    <div style="
    margin-top:300px;
    border-top:1px solid #475569;
    padding-top:10px;
    text-align:center;
    color:#94a3b8;
    font-size:12px;
    ">
    (C) Dept. Engineering SBU
    </div>
    """,
    unsafe_allow_html=True)



# =====================================================
# LOAD DATA
# =====================================================


@st.cache_data(ttl=10)
def get_data():


    try:

        df = load_data()


    except Exception:

        df = pd.DataFrame()



    # ถ้าไม่มีข้อมูล
    # ใช้ API จำลอง

    if df.empty:

        df = fetch_data()



    if not df.empty:


        df["Date"] = pd.to_datetime(
            df["Date"],
            errors="coerce"
        )


        df = (
            df
            .dropna(subset=["Date"])
            .sort_values("Date")
            .reset_index(drop=True)
        )


    return df




df = get_data()



if df.empty:

    st.error(
        "ไม่พบข้อมูล"
    )

    st.stop()



latest = df.iloc[-1]


prev = (
    df.iloc[-2]
    if len(df)>1
    else latest
)



latest_time = latest["Date"].strftime(
    "%d/%m/%Y %H:%M:%S"
)



# =====================================================
# HEADER
# =====================================================


st.markdown(f"""

<div style="
background:linear-gradient(135deg,#0f172a,#1e293b);
padding:20px;
border-radius:15px;
border:1px solid #334155;
">

<h1 style="
color:white;
margin:0;
">

🌍 Dashboard Tracking Greenhouse Gases Emission

</h1>


<p style="
color:#cbd5e1;
">

🕒 Update : {latest_time}

</p>


</div>

""",
unsafe_allow_html=True)



st.markdown("---")



# =====================================================
# KPI
# =====================================================


def create_kpi(column):

    now = float(
        latest.get(column,0)
    )

    old = float(
        prev.get(column,0)
    )


    diff = now-old


    percent = (
        diff/old*100
        if old !=0
        else 0
    )


    arrow = (
        "↑"
        if diff>0
        else "↓"
        if diff<0
        else "→"
    )


    return now,f"{arrow} {percent:.1f}%"



c1,c2,c3,c4,c5,c6 = st.columns(6)



items = [

("CO2","CO₂"),

("CH4","CH₄"),

("NO2","NO₂"),

("PM25","PM2.5"),

("Temp","Temperature"),

("Humidity","Humidity")

]



cols=[
c1,c2,c3,c4,c5,c6
]


for i,(key,name) in enumerate(items):

    value,delta=create_kpi(key)

    cols[i].metric(
        name,
        f"{value:.2f}",
        delta
    )



st.markdown("---")



# =====================================================
# ALERT
# =====================================================


if latest.get("CO2",0)>500:

    st.error(
        "🔴 CO₂ สูงเกินกำหนด"
    )

else:

    st.success(
        "🟢 ระบบปกติ"
    )



# =====================================================
# GRAPH
# =====================================================


st.subheader(
    "📈 Graph"
)



period = st.selectbox(
    "ช่วงเวลา",
    [
        "รายวัน",
        "รายสัปดาห์",
        "รายเดือน",
        "ทั้งหมด"
    ]
)



if period=="รายวัน":

    plot_df=df.tail(24)

elif period=="รายสัปดาห์":

    plot_df=df.tail(168)

elif period=="รายเดือน":

    plot_df=df.tail(720)

else:

    plot_df=df



option={

"CO₂":"CO2",

"CH₄":"CH4",

"NO₂":"NO2",

"PM2.5":"PM25",

"Temperature":"Temp",

"Humidity":"Humidity"

}



selected_name = st.selectbox(

"เลือกข้อมูล",

list(option.keys())

)



selected=[option[selected_name]]



fig=px.line(

plot_df,

x="Date",

y=selected,

markers=True,

template="plotly_dark"

)



fig.update_layout(

height=500,

paper_bgcolor="#030712",

plot_bgcolor="#030712",

font=dict(
color="white"
)

)



st.plotly_chart(

fig,

use_container_width=True

)



# =====================================================
# STATUS
# =====================================================


st.sidebar.metric(
    "จำนวนข้อมูล",
    len(df)
)


st.sidebar.metric(
    "ล่าสุด",
    latest_time
)
