# ===== IMPORT =====
import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from datetime import datetime
import pytz
import os

# ===== PAGE SETTING =====
st.set_page_config(
    layout="wide",
    page_title="GHG Monitor Board",
    initial_sidebar_state="expanded"
)

# ===== CSS =====
st.markdown("""
<style>
::-webkit-scrollbar { display: none; }
.stApp { overflow: hidden !important; }
</style>
""", unsafe_allow_html=True)

# ===== DATA FILE =====
DATA_FILE = "ghg_data.csv"

# ===== LOAD DATA =====
def get_sensor_data():

    bkk_tz = pytz.timezone("Asia/Bangkok")
    now = datetime.now(bkk_tz)

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

    st.markdown("### 📋 เมนูควบคุม")

    pollutants = [col for col in df.columns if col != "Date"]

    selected_pollutant = st.selectbox(
        "สารมลพิษที่ต้องการดูสถิติ:",
        pollutants
    )

    mode = st.radio(
        "รูปแบบข้อมูล:",
        ["รายชั่วโมง (24h)", "รายวัน"]
    )

    if st.button("🔄 อัปเดตข้อมูลตอนนี้"):
        st.rerun()

# ===== HEADER =====
col_title, col_time = st.columns([2, 1])

with col_title:
    st.title("🌍 Tracking GHGs Emission")

with col_time:
    st.markdown(
        f"🕒 {current_time.strftime('%Y-%m-%d %H:%M:%S')}",
        unsafe_allow_html=True
    )

# ===== METRICS =====
cols = st.columns(len(pollutants))

for i, col_name in enumerate(pollutants):

    val = latest_data[col_name]

    delta_val = val - df.iloc[-2][col_name] if len(df) > 1 else 0

    cols[i].metric(
        label=col_name,
        value=int(round(val, 0)),
        delta=int(round(delta_val, 0))
    )

# ===== GRAPH CLEAN =====
df_plot = df.copy()

df_plot["Date"] = pd.to_datetime(df_plot["Date"], errors="coerce")
df_plot[selected_pollutant] = pd.to_numeric(df_plot[selected_pollutant], errors="coerce")

df_plot = df_plot.dropna(subset=["Date", selected_pollutant])

# ===== CHECK =====
if df_plot.empty:
    st.error("ไม่มีข้อมูลสำหรับกราฟ")
    st.stop()

# ===== GRAPH =====
fig = px.line(
    df_plot,
    x="Date",
    y=selected_pollutant,
    title=f"แนวโน้ม {selected_pollutant}",
    template="plotly_dark",
    height=300
)

fig.update_traces(
    line_color="#00ffcc",
    line_width=3
)

# ===== 🔥 FIX Y-AXIS (NO DECIMAL, NO SCIENTIFIC) =====
fig.update_yaxes(
    tickformat="d",   # integer only
    separatethousands=True
)

fig.update_layout(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    margin=dict(t=40, b=10, l=10, r=10),
    xaxis_title=None,
    yaxis_title=None
)

st.plotly_chart(fig, use_container_width=True)
