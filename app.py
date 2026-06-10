import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import pytz
import os

# ===== PAGE =====
st.set_page_config(layout="wide", page_title="GHG Monitor Board")

# ===== DATA =====
DATA_FILE = "ghg_data.csv"

def load_data():
    tz = pytz.timezone("Asia/Bangkok")
    now = datetime.now(tz)
    current_hour = now.replace(minute=0, second=0, microsecond=0)

    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE)
    else:
        dates = pd.date_range(end=current_hour, periods=24, freq="h")
        df = pd.DataFrame({
            "Date": dates,
            "CO₂ (ppm)": [415]*24,
            "CH₄ (ppb)": [1850]*24,
            "NO₂ (ppb)": [40]*24,
            "PM 2.5 (µg/m³)": [25]*24,
            "Temp (°C)": [33]*24,
            "Humid (%)": [60]*24
        })
        df.to_csv(DATA_FILE, index=False)

    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df = df.dropna(subset=["Date"])
    df = df.sort_values("Date")

    return df, now, current_hour


df, now, current_hour = load_data()

# ===== SIDEBAR =====
with st.sidebar:
    st.title("Control")

    pollutants = df.select_dtypes(include=["number"]).columns.tolist()
    selected = st.selectbox("เลือกตัวแปร", pollutants)

    period = st.selectbox(
        "ช่วงเวลา",
        ["24 ชั่วโมง", "7 วัน", "30 วัน", "90 วัน", "ทั้งหมด"]
    )

# ===== IMPORTANT FIX: ใช้ "ข้อมูลจริง" ไม่เดา =====

df = df.sort_values("Date")

# หา min/max เวลาใน data จริง
min_time = df["Date"].min()
max_time = df["Date"].max()

# map ช่วงเวลาแบบ "เวลา" ไม่ใช่ tail()
if period == "24 ชั่วโมง":
    start_time = max_time - pd.Timedelta(hours=24)
elif period == "7 วัน":
    start_time = max_time - pd.Timedelta(days=7)
elif period == "30 วัน":
    start_time = max_time - pd.Timedelta(days=30)
elif period == "90 วัน":
    start_time = max_time - pd.Timedelta(days=90)
else:
    start_time = min_time

# ===== FILTER ด้วยเวลา (สำคัญมาก) =====
df_show = df[df["Date"] >= start_time].copy()

# ===== DEBUG (ดูว่ามีข้อมูลจริงไหม) =====
st.write("DEBUG rows:", len(df_show))
st.write("DEBUG date range:", df_show["Date"].min(), "→", df_show["Date"].max())

# ===== กันกราฟว่าง =====
if df_show.empty:
    st.error("ไม่มีข้อมูลในช่วงเวลานี้ → data ยังไม่พอ (ต้องมีข้อมูลมากกว่านี้)")
    st.stop()

# ===== FIX TYPE =====
df_show[selected] = pd.to_numeric(df_show[selected], errors="coerce")
df_show = df_show.dropna(subset=[selected])

# ===== GRAPH =====
fig = px.line(
    df_show,
    x="Date",
    y=selected,
    template="plotly_dark",
    height=500
)

fig.update_traces(mode="lines+markers")

st.plotly_chart(fig, use_container_width=True)
