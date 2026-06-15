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

st.caption(
    f"ข้อมูลล่าสุด : {thai_date}"
)


# =========================
# KPI
# =========================

c1,c2,c3,c4,c5,c6 = st.columns(6)

c1.metric("CO₂", round(float(latest["CO2"]),1))
c2.metric("CH₄", round(float(latest["CH4"]),1))
c3.metric("NO₂", round(float(latest["NO2"]),1))
c4.metric("PM 2.5", round(float(latest["PM25"]),1))
c5.metric("Temp", round(float(latest["Temp"]),1))
c6.metric("Humidity", round(float(latest["Humidity"]),1))

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

    graph_mode = st.radio(
        "โหมดการแสดงผล",
        [
            "Actual Values",
            "Comparison Mode"
        ],
        horizontal=True
    )

    options = {

        "CO₂ (Carbon Dioxide)": "CO2",
        "CH₄ (Methane)": "CH4",
        "NO₂ (Nitrogen Dioxide)": "NO2",
        "PM 2.5 (Particulate Matter)": "PM25",
        "Temp (Temperature)": "Temp",
        "Humidity (Relative Humidity)": "Humidity"

    }

    color_map = {

        "CO2": "#DC2626",
        "CH4": "#F97316",
        "NO2": "#7C3AED",
        "PM25": "#EAB308",
        "Temp": "#22C55E",
        "Humidity": "#2563EB"

    }

    if graph_mode == "Actual Values":

        selected = [
            "CO2",
            "CH4",
            "NO2",
            "PM25",
            "Temp",
            "Humidity"
        ]

        plot_df = df_plot.copy()

    else:

        selected_labels = st.multiselect(
            "เลือกข้อมูล",
            list(options.keys()),
            default=["CO₂ (Carbon Dioxide)"]
        )

        selected = [
            options[x]
            for x in selected_labels
        ]

        if not selected:

            st.warning(
                "Please select at least one parameter."
            )

            st.stop()

        plot_df = df_plot.copy()

        reference_scale = {

            "CO2": 1000,
            "CH4": 100,
            "NO2": 100,
            "PM25": 100,
            "Temp": 50,
            "Humidity": 100

        }

        for col in selected:

            plot_df[col] = (
                plot_df[col]
                /
                reference_scale[col]
            ) * 100

    fig = px.line(
        plot_df,
        x="Date",
        y=selected,
        template="plotly_dark",
        markers=True
    )

    for trace in fig.data:

        if trace.name in color_map:

            trace.line.color = color_map[trace.name]
            trace.line.width = 3

        display_names = {

            "CO2": "CO₂",
            "CH4": "CH₄",
            "NO2": "NO₂",
            "PM25": "PM 2.5",
            "Temp": "Temp",
            "Humidity": "Humidity"

        }

        trace.name = display_names.get(
            trace.name,
            trace.name
        )

    fig.update_layout(

        legend=dict(
            orientation="h",
            y=1.05,
            x=0
        ),

        hovermode="x unified",

        xaxis=dict(
            automargin=True
        )

    )

    if graph_mode == "Actual Values":

        fig.update_yaxes(
            title_text="Actual Value"
        )

    else:

        fig.update_yaxes(
            title_text="Relative Scale (%)",
            range=[0,100]
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

    name_map = {

        "CO2": "CO₂",
        "CH4": "CH₄",
        "NO2": "NO₂",
        "PM25": "PM 2.5",
        "Temp": "Temp",
        "Humidity": "Humidity"

    }

    for item in selected:

        st.metric(
            f"AVG {name_map[item]}",
            round(df[item].mean(), 2)
        )

        st.metric(
            f"MAX {name_map[item]}",
            round(df[item].max(), 2)
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
