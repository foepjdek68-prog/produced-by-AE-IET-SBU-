import streamlit as st
import pandas as pd

from streamlit_autorefresh import st_autorefresh

from Services.database import load_data, save_data
from Services.api_loader import fetch_data


# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(
    page_title="GHG Data Center",
    page_icon="🗄️",
    layout="wide",
    initial_sidebar_state="expanded"
)


# Auto refresh
st_autorefresh(
    interval=15000,
    key="data_refresh"
)


# =====================================================
# GLOBAL STYLE
# =====================================================

st.markdown("""
<style>

/* Background */

.stApp {
    background:#020617;
}


/* Sidebar */

section[data-testid="stSidebar"] {

    background:#0f172a !important;
    border-right:1px solid #334155;

}


section[data-testid="stSidebar"] * {

    color:#f8fafc !important;

}


/* Metric Card */

[data-testid="stMetric"] {

    background:#0f172a !important;
    border:1px solid #38bdf8 !important;
    border-radius:14px;
    padding:15px;

}


[data-testid="stMetricLabel"] {

    color:#cbd5e1 !important;

}


[data-testid="stMetricValue"] {

    color:white !important;

}


/* Table */

[data-testid="stDataFrame"] {

    border-radius:12px;

}


/* Divider */

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

    st.markdown("""
    <div style="
    background:#1e293b;
    padding:15px;
    border-radius:15px;
    text-align:center;
    ">
    """,
    unsafe_allow_html=True)


    st.image(
        "Assets/logo.png",
        width=250
    )


    st.markdown(
    "</div>",
    unsafe_allow_html=True
    )


    st.markdown("""
    <div style="
    margin-top:400px;
    border-top:1px solid #475569;
    padding-top:10px;
    color:#94a3b8;
    text-align:center;
    font-size:12px;
    ">
    (C) Dept. Engineering SBU
    </div>
    """,
    unsafe_allow_html=True
    )



# =====================================================
# LOAD DATA
# =====================================================

@st.cache_data(ttl=5)
def get_data():

    df = load_data()


    if df.empty:

        df = fetch_data()

        if not df.empty:

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
        "ไม่พบข้อมูลในระบบ"
    )

    st.stop()



latest = df.iloc[-1]


latest_str = latest["Date"].strftime(
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
margin-bottom:20px;
">

<h1 style="
color:white;
margin:0;
">

🗄️ GHG Data Management Center

</h1>


<p style="
color:#cbd5e1;
">

🕒 อัปเดตล่าสุด : {latest_str}

</p>


</div>

""",
unsafe_allow_html=True)



# =====================================================
# KPI
# =====================================================


c1,c2,c3,c4 = st.columns(4)



c1.metric(
    "จำนวนข้อมูล",
    f"{len(df):,}"
)


c2.metric(
    "CO₂ ล่าสุด",
    f"{latest['CO2']:.2f}"
)


c3.metric(
    "อุณหภูมิ",
    f"{latest['Temp']:.2f} °C"
)


c4.metric(
    "สถานะ",
    "🟢 ONLINE"
)



st.markdown("---")



# =====================================================
# FILTER
# =====================================================


rename_map = {

    "CO2":"CO₂",

    "CH4":"CH₄",

    "NO2":"NO₂",

    "PM25":"PM2.5",

    "Temp":"Temperature",

    "Humidity":"Humidity"

}



display_df = df.rename(
    columns=rename_map
)



selected = st.selectbox(

    "เลือกข้อมูล",

    [
        "ทั้งหมด"
    ]
    +
    list(rename_map.values())

)



if selected != "ทั้งหมด":

    working_df = display_df[
        [
            "Date",
            selected
        ]
    ]

else:

    working_df = display_df



# =====================================================
# DATA VIEW
# =====================================================


tab1,tab2 = st.tabs(
    [
        "📊 Statistics",
        "📋 Latest Data"
    ]
)



with tab1:


    st.subheader(
        "📊 สถิติข้อมูล"
    )


    st.dataframe(

        working_df.describe(),

        use_container_width=True

    )



with tab2:


    st.subheader(
        "📋 ข้อมูลล่าสุด"
    )


    st.dataframe(

        working_df
        .sort_values(
            "Date",
            ascending=False
        ),

        height=550,

        use_container_width=True

    )



# =====================================================
# DOWNLOAD
# =====================================================


st.markdown("---")


csv = working_df.to_csv(
    index=False
).encode(
    "utf-8-sig"
)


st.download_button(

    "📥 Download CSV",

    csv,

    "GHG_Data.csv",

    "text/csv",

    use_container_width=True

)
