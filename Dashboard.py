import streamlit as st
import plotly.express as px
import pandas as pd
from datetime import datetime

from Services.database import load_data, save_data
from Services.api_loader import fetch_data


st.set_page_config(
    page_title="Dashboard Tracking Greenhouse Gases Emission",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)


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


df = load_data()

if df.empty:
    df = fetch_data()
    save_data(df)

df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
df = df.dropna(subset=["Date"])

latest = df.iloc[-1]

thai_date = latest["Date"].strftime("%d/%m/%y")


st.info("""
### 🌍 Dashboard Tracking

## Greenhouse Gases Emission

ระบบรายงานและติดตามก๊าซเรือนกระจกอัจฉริยะ
""")

st.caption(f"ข้อมูลล่าสุด : {thai_date}")


c1, c2, c3, c4, c5, c6 = st.columns(6)

c1.metric("CO₂", f"{round(float(latest['CO2']),1)} (คาร์บอนไดออกไซด์)")
c2.metric("CH₄", f"{round(float(latest['CH4']),1)} (มีเทน)")
c3.metric("NO₂", f"{round(float(latest['NO2']),1)} (ไนโตรเจนไดออกไซด์)")
c4.metric("PM 2.5", round(float(latest["PM25"]), 1))
c5.metric("Temp", round(float(latest["Temp"]), 1))
c6.metric("Humidity", round(float(latest["Humidity"]), 1))

st.markdown("---")


period = st.selectbox(
    "ช่วงการแสดงผล",
    ["Daily", "Weekly", "Monthly", "Annual"]
)

if period == "Daily":
    df_plot = df.tail(24)
elif period == "Weekly":
    df_plot = df.tail(24 * 7)
elif period == "Monthly":
    df_plot = df.tail(24 * 30)
else:
    df_plot = df


left, right = st.columns([4, 1])

with left:

    st.subheader("📈 กราฟแสดงข้อมูล")

    graph_mode = st.radio(
        "โหมดการแสดงผล",
        ["Actual Values", "Comparison Mode"],
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

    display_names = {v: k for k, v in options.items()}

    color_map = {
        "CO2": "#DC2626",
        "CH4": "#F97316",
        "NO2": "#7C3AED",
        "PM25": "#EAB308",
        "Temp": "#22C55E",
        "Humidity": "#2563EB"
    }

    if graph_mode == "Actual Values":

        selected_actual = st.selectbox(
            "เลือกข้อมูล",
            list(options.keys())
        )

        selected = [options[selected_actual]]
        plot_df = df_plot.copy()

    else:

        selected_labels = st.multiselect(
            "เลือกข้อมูล",
            list(options.keys()),
            default=["CO₂ (Carbon Dioxide)"]
        )

        selected = [options[x] for x in selected_labels]

        if not selected:
            st.warning("Please select at least one parameter.")
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
            plot_df[col] = pd.to_numeric(plot_df[col], errors="coerce").fillna(0)
            plot_df[col] = (plot_df[col] / reference_scale[col]) * 100


    fig = px.line(
        plot_df,
        x="Date",
        y=selected,
        template="plotly_dark",
        markers=True
    )

    for trace in fig.data:

        key = trace.name

        if key in color_map:
            trace.line.color = color_map[key]
            trace.line.width = 3

        trace.name = display_names.get(key, key)

        trace.hovertemplate = "%{y:.2f}<br>%{x|%d/%m/%Y %H:%M}<extra></extra>"

    fig.update_layout(
        legend=dict(
            orientation="h",
            y=-0.25,
            x=0
        ),
        hovermode="x unified",
        xaxis=dict(type="date", automargin=True)
    )

    st.plotly_chart(fig, use_container_width=True)


with right:

    st.subheader("📊 สรุประบบ")

    avg_co2 = df["CO2"].mean()

    if avg_co2 < 450:
        status = "🟢 Normal"
    elif avg_co2 < 500:
        status = "🟡 Warning"
    else:
        status = "🔴 Critical"

    st.info(status)
