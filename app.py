import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from datetime import datetime

# 1. SETUP
st.set_page_config(layout="wide", page_title="GHG Monitor Board")

# 2. MAPPING
UNIT_MAP = {
    "CO₂ (ppm)": "Concentration (ppm)",
    "CH₄ (ppb)": "Concentration (ppb)",
    "NO₂ (ppb)": "Concentration (ppb)",
    "PM 2.5": "Concentration (µg/m³)",
    "Temp (°C)": "Temperature (°C)",
    "Humidity (%)": "Relative Humidity (%)"
}

# 3. DATA FUNCTIONS
def get_latest_data():
    return {"CO₂ (ppm)": 433, "CH₄ (ppb)": 1865, "NO₂ (ppb)": 42.1, "PM 2.5": 22.4, "Temp (°C)": 33.2, "Humidity (%)": 64}

def get_history(pollutant, mode):
    # กำหนดความถี่ตามโหมด
    periods = 12 if mode == "รายเดือน" else 30
    freq = 'M' if mode == "รายเดือน" else 'D'
    
    dates = pd.date_range(end=datetime.now(), periods=periods, freq=freq)
    
    # กำหนดค่าฐานให้เหมาะสมกับชนิดข้อมูล
    mapping = {"Temp": 30, "CO₂": 430, "CH₄": 1800, "NO₂": 40, "PM 2.5": 25, "Humidity": 60}
    base = next((val for key, val in mapping.items() if key in pollutant), 50)
    
    vals = np.random.normal(base, 5, periods)
    return pd.DataFrame({'Date': dates, 'Value': vals})

# 4. UI - MAIN DASHBOARD
st.title("GHG Operational Monitor")

# Metrics Section
metrics = get_latest_data()
st.markdown('<div style="background-color: #0f172a; padding: 20px; border-radius: 10px;">', unsafe_allow_html=True)
cols = st.columns(len(metrics))
for i, (label, val) in enumerate(metrics.items()):
    cols[i].metric(label, val)
st.markdown('</div>', unsafe_allow_html=True)

# Analysis Section
st.subheader("Historical Trends Analysis")
col1, col2 = st.columns([1, 3])

with col1:
    selected = st.selectbox("เลือกสารมลพิษ", list(UNIT_MAP.keys()))
    mode = st.radio("รูปแบบการแสดงผล:", ["รายวัน", "รายเดือน"], horizontal=True)

with col2:
    df_hist = get_history(selected, mode)
    
    # สร้างกราฟ
    fig = px.line(df_hist, x='Date', y='Value', template="plotly_dark")
    fig.update_layout(
        xaxis_title="Date",
        yaxis_title=UNIT_MAP[selected], 
        paper_bgcolor="rgba(0,0,0,0)", 
        plot_bgcolor="rgba(0,0,0,0)",
        yaxis=dict(autorange=True)
    )
    st.plotly_chart(fig, use_container_width=True)
