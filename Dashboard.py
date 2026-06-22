import streamlit as st
import pandas as pd
import plotly.express as px

from streamlit_autorefresh import st_autorefresh

from Services.database import load_data, save_data
from Services.api_loader import fetch_data



st.set_page_config(

    page_title="GHG Dashboard",

    page_icon="🌍",

    layout="wide"

)



st_autorefresh(

    interval=60000,

    key="refresh"

)



st.markdown("""
<style>

.stApp{

background:#030712;

}


section[data-testid="stSidebar"]{

background:#0f172a;

}


[data-testid="stMetric"]{

background:#111827;

border:1px solid #38bdf8;

border-radius:12px;

padding:15px;

}


</style>

""",
unsafe_allow_html=True)




with st.sidebar:

    st.image(
        "Assets/logo.png",
        width=250
    )


    st.write(
        "(C) Dept. Engineering SBU"
    )




@st.cache_data(ttl=30)

def get_data():


    df = load_data()


    if df.empty:

        df = fetch_data()

        save_data(df)



    if not df.empty:


        df["Date"] = pd.to_datetime(
            df["Date"],
            errors="coerce"
        )


        df=df.dropna(
            subset=["Date"]
        )


        df=df.sort_values(
            "Date"
        )


    return df




df=get_data()



if df.empty:

    st.error(
        "ไม่มีข้อมูล"
    )

    st.stop()



latest=df.iloc[-1]

previous=df.iloc[-2] if len(df)>1 else latest




st.markdown(f"""

<div style="
background:linear-gradient(135deg,#0f172a,#1e293b);
padding:25px;
border-radius:15px;
">

<h1 style="color:white">

🌍 Dashboard Tracking Greenhouse Gases Emission

</h1>


<p style="color:#cbd5e1">

Update :
{latest['Date']}

</p>


</div>

""",
unsafe_allow_html=True)



st.divider()



# KPI

cols=st.columns(6)


items=[

("CO2","CO₂"),

("CH4","CH₄"),

("NO2","NO₂"),

("PM25","PM2.5"),

("Temp","Temperature"),

("Humidity","Humidity")

]


for i,(key,name) in enumerate(items):


    value=float(
        latest.get(key,0)
    )


    old=float(
        previous.get(key,0)
    )


    delta=value-old


    cols[i].metric(

        name,

        f"{value:.2f}",

        f"{delta:.2f}"

    )




st.divider()



# GRAPH


choice=st.selectbox(

    "เลือกข้อมูล",

    [

    "CO2",

    "CH4",

    "NO2",

    "PM25",

    "Temp",

    "Humidity"

    ]

)



fig=px.line(

    df.tail(200),

    x="Date",

    y=choice,

    markers=True,

    template="plotly_dark"

)



fig.update_layout(

    height=500,

    paper_bgcolor="#030712",

    plot_bgcolor="#030712"

)



st.plotly_chart(

    fig,

    use_container_width=True

)



st.success(
    "🟢 ระบบออนไลน์"
)
