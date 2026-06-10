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
        dates = pd.date_range(end=now, periods=24, freq="h")

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
latest_data = df.iloc[-1]

# ===== SIDEBAR =====
with st.sidebar:

    pollutants = [c for c in df.columns if c != "Date"]

    selected = st.selectbox("เลือกตัวแปร", pollutants)

# ===== METRICS =====
cols = st.columns(len(pollutants))

for i, c in enumerate(pollutants):
    val = latest_data[c]
    delta = val - df.iloc[-2][c] if len(df) > 1 else 0

    cols[i].metric(c, int(round(val, 0)), int(round(delta, 0)))

# ===== GRAPH =====
df_plot = df.copy()

df_plot["Date"] = pd.to_datetime(df_plot["Date"], errors="coerce")
df_plot[selected] = pd.to_numeric(df_plot[selected], errors="coerce")

df_plot = df_plot.dropna(subset=["Date", selected])

if df_plot.empty:
    st.error("ไม่มีข้อมูล")
    st.stop()

# ===== 🔥 FIX Y AXIS (ROUND TO NEAREST 10) =====
y_min = np.floor(df_plot[selected].min() / 10) * 10
y_max = np.ceil(df_plot[selected].max() / 10) * 10

fig = px.line(
    df_plot,
    x="Date",
    y=selected,
    template="plotly_dark",
    height=300
)

fig.update_traces(mode="lines+markers")

fig.update_yaxes(
    range=[y_min, y_max],
    tick0=y_min,
    dtick=10  # ทุก 10 หน่วย + ไม่มีเลขแปลก ๆ
)

st.plotly_chart(fig, use_container_width=True)
