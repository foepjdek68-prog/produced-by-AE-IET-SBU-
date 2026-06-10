# ===== IMPORT =====
import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from datetime import datetime
import pytz
import os

# ===== PAGE =====
st.set_page_config(layout="wide", page_title="GHG Monitor Board")

# ===== CSS =====
st.markdown("""
<style>
::-webkit-scrollbar { display: none; }
.stApp { overflow: hidden !important; }
</style>
""", unsafe_allow_html=True)

DATA_FILE = "ghg_data.csv"

# ===== LOAD DATA =====
def get_sensor_data():

    tz = pytz.timezone("Asia/Bangkok")
    now = datetime.now(tz)

    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE)
    else:
        dates = pd.date_range(end=now.replace(minute=0, second=0, microsecond=0),
                               periods=24, freq="h")

        df = pd.DataFrame({
            "Date": dates,
            "CO₂ (ppm)": np.random.normal(415, 10, 24).round(1),
            "CH₄ (ppb)": np.random.normal(1850, 20, 24).round(1),
            "NO₂ (ppb)": np.random.normal(40, 5, 24).round(1),
            "PM 2.5 (µg/m³)": np.random.normal(25, 8, 24).round(1),
            "Temp (°C)": np.random.normal(33, 2, 24).round(1),
            "Humid (%)": np.random.normal(60, 5, 24).round(1)
        })

        df.to_csv(DATA_FILE, index=False)

    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df = df.dropna(subset=["Date"])
    df = df.sort_values("Date")

    return df, now


df, current_time = get_sensor_data()

# ===== SIDEBAR =====
with st.sidebar:
    pollutants = [c for c in df.columns if c != "Date"]
    selected = st.selectbox("เลือกตัวแปร", pollutants)

# ===== GRAPH =====
df_plot = df.copy()
df_plot[selected] = pd.to_numeric(df_plot[selected], errors="coerce")
df_plot = df_plot.dropna(subset=["Date", selected])

if df_plot.empty:
    st.error("ไม่มีข้อมูล")
    st.stop()

# ===== 🔥 OVERVIEW GROUPING (ทำให้เป็นภาพรวม) =====
df_plot["TimeGroup"] = df_plot["Date"].dt.floor("3h")  # รวมทุก 3 ชั่วโมง

df_plot = df_plot.groupby("TimeGroup")[selected].mean().reset_index()

# ===== GRAPH =====
fig = px.line(
    df_plot,
    x="TimeGroup",
    y=selected,
    template="plotly_dark",
    height=350
)

fig.update_traces(mode="lines+markers")

# ===== OVERVIEW AXIS =====
fig.update_xaxes(
    tickformat="%d %H:%M",
    showgrid=False
)

# ===== Y AXIS (SMOOTH OVERVIEW SCALE) =====
y_min = np.floor(df_plot[selected].min() / 10) * 10
y_max = np.ceil(df_plot[selected].max() / 10) * 10

fig.update_yaxes(
    range=[y_min, y_max],
    dtick=(y_max - y_min) / 5  # 5 levels only = ภาพรวม
)

fig.update_layout(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    margin=dict(t=30, b=10, l=10, r=10),
    xaxis_title=None,
    yaxis_title=None
)

st.plotly_chart(fig, use_container_width=True)
