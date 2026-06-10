import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px

# ===== PAGE =====
st.set_page_config(layout="wide", page_title="GHG Real System")

# ===== DB READ =====
def load_data():

    conn = sqlite3.connect("ghg_data.db")

    df = pd.read_sql_query("""
        SELECT * FROM air_quality
    """, conn)

    df["time"] = pd.to_datetime(df["time"])

    return df

df = load_data()

if df.empty:
    st.warning("ยังไม่มีข้อมูล")
    st.stop()

# ===== SIDEBAR =====
stations = df["station"].unique()

station = st.selectbox("เลือกสถานี", stations)

df_plot = df[df["station"] == station]

# ===== METRICS =====
latest = df_plot.iloc[-1]

col1, col2 = st.columns(2)

col1.metric("AQI", int(latest["aqi"]))
col2.metric("PM2.5", latest["pm25"])

# ===== GRAPH =====
fig = px.line(
    df_plot,
    x="time",
    y="aqi",
    template="plotly_dark",
    height=350
)

fig.update_traces(line_width=3, line_color="#00ffcc")

st.plotly_chart(fig, use_container_width=True)
