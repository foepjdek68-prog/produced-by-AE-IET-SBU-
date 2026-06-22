import streamlit as st
import plotly.express as px
import pandas as pd
import time

from streamlit_autorefresh import st_autorefresh
from Services.database import load_data, save_data
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


# =====================================================
# REFRESH CONTROL
# =====================================================

AUTO_REFRESH_TIME = 60

if "refresh_time" not in st.session_state:
    st.session_state.refresh_time = time.time()


# refresh timer ทุก 1 วินาที
st_autorefresh(
    interval=1000,
    key="refresh_timer"
)


# =====================================================
# LOAD DATA
# =====================================================

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
        "ไม่พบข้อมูลในระบบ กรุณาตรวจสอบการเชื่อมต่อฐานข้อมูล"
    )

    st.stop()



latest = df.iloc[-1]

prev = (
    df.iloc[-2]
    if len(df) > 1
    else latest
)


latest_str = latest["Date"].strftime(
    "%d/%m/%Y %H:%M:%S"
)



# =====================================================
# SIDEBAR
# =====================================================

with st.sidebar:


    st.markdown(
        """
        <div style="
            background:rgba(255,255,255,0.05);
            padding:15px;
            border-radius:10px;
            margin-bottom:20px;
            text-align:center;
        ">
        """,
        unsafe_allow_html=True
    )


    st.image(
        "Assets/logo.png",
        width=250
    )


    st.markdown(
        "</div>",
        unsafe_allow_html=True
    )



    st.markdown(
        """
        <style>

        [data-testid="stSidebar"] > div:first-child {

            display:flex;
            flex-direction:column;
            height:90vh;

        }


        .sidebar-footer {

            border-top:1px solid #4B5563;
            padding-top:10px;
            margin-top:auto;
            font-size:0.75em;
            color:#9CA3AF;

        }

        </style>


        <div class="sidebar-footer">

        (C) Dept. Engineering SBU

        </div>

        """,
        unsafe_allow_html=True
    )



# =====================================================
# HEADER
# =====================================================


st.markdown(
f"""
<div style="

background:linear-gradient(135deg,#0f172a,#1e293b);

padding:20px;

border-radius:12px;

border:1px solid #334155;

margin-bottom:20px;

">

<h1 style="

margin:0;

color:white;

">

🌍 Dashboard Tracking Greenhouse Gases Emission

</h1>


<p style="

margin-top:8px;

color:#cbd5e1;

">

🕒 อัปเดตล่าสุด : {latest_str}

</p>


</div>

""",
unsafe_allow_html=True
)



# =====================================================
# REFRESH BUTTON
# =====================================================


r1,r2,r3 = st.columns(
    [1.5,2,5]
)


with r1:

    if st.button(
        "🔄 Refresh Now",
        use_container_width=True
    ):

        st.cache_data.clear()

        st.session_state.refresh_time = time.time()

        st.rerun()



with r2:


    elapsed = int(
        time.time()
        -
        st.session_state.refresh_time
    )


    remain = AUTO_REFRESH_TIME - elapsed



    if remain <= 0:


        st.cache_data.clear()

        st.session_state.refresh_time = time.time()

        st.rerun()



    st.info(
        f"⏱ Refresh ใน {remain} วินาที"
    )



with r3:

    st.caption(
        "ระบบจะอัปเดตข้อมูลอัตโนมัติทุก 60 วินาที"
    )



# =====================================================
# CSS
# =====================================================


st.markdown(
"""

<style>


.stApp {

background:#030712;

}


.block-container {

padding-top:1rem;

}



section[data-testid="stSidebar"] {

background:#1e293b !important;

border-right:1px solid #334155;

}



section[data-testid="stSidebar"] * {

color:#e2e8f0 !important;

}



[data-testid="stMetric"] {


background:#0f172a !important;

border:1px solid #60a5fa !important;

border-radius:12px !important;

padding:15px !important;

text-align:center;

}



[data-testid="stMetricLabel"] {

color:#cbd5e1 !important;

font-weight:600 !important;

}



[data-testid="stMetricValue"] {

color:white !important;

font-weight:700 !important;

}



.stSelectbox > div > div,

.stMultiSelect > div > div {

background:#111827 !important;

color:white !important;

}


.stRadio label {

color:white !important;

}


hr {

border-color:#334155 !important;

}



</style>

""",
unsafe_allow_html=True
)



# =====================================================
# KPI
# =====================================================


alerts=[]


if latest.get("CO2",0)>500:

    alerts.append(
        "🔴 ระดับ CO₂ สูงเกินเกณฑ์"
    )


if latest.get("PM25",0)>35:

    alerts.append(
        "⚠ แจ้งเตือนค่า PM2.5"
    )


if latest.get("Temp",0)>38:

    alerts.append(
        "🌡 อุณหภูมิสูงเกินเกณฑ์"
    )



def kpi(col,symbol,name=None):

    now=float(
        latest.get(col,0)
    )


    old=float(
        prev.get(col,0)
    )


    diff=now-old


    percent=(

        diff/old*100

        if old!=0

        else 0

    )


    arrow=(

        "↑"
        if diff>0
        else "↓"
        if diff<0
        else "→"

    )


    label=f"{symbol} ({name})" if name else symbol


    return now, f"{arrow} {percent:.1f}%", label



c1,c2,c3,c4,c5,c6 = st.columns(6)


metrics=[

("CO2","CO₂","Carbon Dioxide"),

("CH4","CH₄","Methane"),

("NO2","NO₂","Nitrogen Dioxide"),

("PM25","PM2.5",None),

("Temp","อุณหภูมิ",None),

("Humidity","ความชื้น",None)

]



for i,(col,sym,name) in enumerate(metrics):

    value,delta,label=kpi(
        col,
        sym,
        name
    )


    [
        c1,c2,c3,c4,c5,c6
    ][i].metric(
        label,
        f"{value:.2f}",
        delta
    )



if alerts:

    cols=st.columns(
        len(alerts)
    )


    for i,a in enumerate(alerts):

        if "🔴" in a:

            cols[i].error(a)

        else:

            cols[i].warning(a)


else:

    st.success(
        "🟢 สภาพแวดล้อมปกติ"
    )
# =====================================================
# GRAPH SECTION
# =====================================================


period = st.selectbox(
    "เลือกช่วงเวลาการแสดงผล",
    [
        "รายวัน",
        "รายสัปดาห์",
        "รายเดือน",
        "รายปี"
    ]
)



if period == "รายวัน":

    df_plot = df.tail(24)


elif period == "รายสัปดาห์":

    df_plot = df.tail(24*7)


elif period == "รายเดือน":

    df_plot = df.tail(24*30)


else:

    df_plot = df



center,right = st.columns(
    [4,1.2]
)



with center:


    st.subheader(
        "📈 กราฟแสดงข้อมูล"
    )



    graph_mode = st.radio(

        "โหมดการแสดงผลกราฟ",

        [
            "ค่าจริง (Actual)",
            "โหมดเปรียบเทียบ (Comparison)"
        ],

        horizontal=True

    )



    options = {


        "CO₂ (Carbon Dioxide)":"CO2",

        "CH₄ (Methane)":"CH4",

        "NO₂ (Nitrogen Dioxide)":"NO2",

        "PM 2.5 (Particulate Matter)":"PM25",

        "อุณหภูมิ (Temperature)":"Temp",

        "ความชื้น (Humidity)":"Humidity"


    }



    if graph_mode == "ค่าจริง (Actual)":


        select = st.selectbox(

            "เลือกข้อมูลที่ต้องการแสดง",

            list(options.keys())

        )


        selected=[

            options[select]

        ]



    else:


        select = st.multiselect(

            "เลือกข้อมูลที่ต้องการเปรียบเทียบ",

            list(options.keys()),

            default=[

                list(options.keys())[0],

                list(options.keys())[1]

            ]

        )


        selected=[

            options[x]

            for x in select

        ]



        if not selected:


            st.warning(

                "กรุณาเลือกข้อมูลอย่างน้อย 1 รายการ"

            )

            st.stop()




    plot_df=df_plot.copy()



    # NORMALIZE DATA

    if graph_mode == "โหมดเปรียบเทียบ (Comparison)":


        for col in selected:


            series=pd.to_numeric(

                plot_df[col],

                errors="coerce"

            )


            min_val=series.min()

            max_val=series.max()



            if max_val-min_val !=0:


                plot_df[col]=(

                    (series-min_val)

                    /

                    (max_val-min_val)

                )*100


            else:

                plot_df[col]=0




    fig=px.line(

        plot_df,

        x="Date",

        y=selected,

        markers=True,

        template="plotly_dark"

    )



    color_map={


        "CO2":"#DC2626",

        "CH4":"#F97316",

        "NO2":"#7C3AED",

        "PM25":"#EAB308",

        "Temp":"#22C55E",

        "Humidity":"#2563EB"


    }




    rev_map={

        v:k

        for k,v in options.items()

    }




    for trace in fig.data:


        trace.line.color = (

            color_map.get(

                trace.name,

                "#FFFFFF"

            )

        )


        trace.line.width=3


        trace.name=rev_map.get(

            trace.name,

            trace.name

        )





    fig.update_layout(


        height=550,


        hovermode="x unified",


        legend_title_text="",


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
# STATUS PANEL
# =====================================================


with right:


    st.subheader(

        "📊 สถานะระบบ"

    )



    st.success(

        "🟢 ระบบออนไลน์ (Normal)"

    )



    st.metric(

        "จำนวนรายการ",

        len(df)

    )



    st.metric(

        "อัปเดตล่าสุดเมื่อ",

        latest["Date"].strftime(

            "%H:%M:%S"

        )

    )



    st.metric(

        "สถานะข้อมูล",

        "ปกติ"

    )



# =====================================================
# FOOTER
# =====================================================


st.markdown(

"""

<hr>

<center style="color:#64748b;font-size:12px">

🌍 Greenhouse Gas Monitoring Dashboard

</center>

""",

unsafe_allow_html=True

)


st.markdown("---")
