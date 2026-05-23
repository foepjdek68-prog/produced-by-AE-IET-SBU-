import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from datetime import datetime

# 1. SETUP
st.set_page_config(layout="wide", page_title="GHG Monitor Board")

# 2. MAPPING (ประกาศไว้บนสุดเพื่อให้เรียกใช้ได้ทั่วถึง)
UNIT_MAP = {
    "CO₂ (ppm)": "Concentration (ppm)",
    "CH₄ (ppb)": "Concentration (ppb)",
    "NO₂ (ppb)": "Concentration (ppb)",
    "PM 2.5": "Concentration (µg/m³)",
    "Temp (°C)": "Temperature (°C)",
    "Humidity (%)": "Relative Humidity (%)"
}

# 3. DATA SIMULATION
def get_latest_data():
    # ค่าต้องตรงกับ Key ใน UNIT_MAP
    return {"CO₂ (ppm)": 433, "CH₄ (ppb)": 1865, "NO₂ (ppb)": 42.1, "PM 2.5": 22.4, "Temp (°C)": 33.2, "Humidity (%)": 64}

def get_history(pollutant):
    dates = pd.date_range(start="2026-05-01", periods=30)
    # ปรับสเกลข้อมูลให้สมจริงตามประเภท
    vals = np.random.normal(30 if "Temp" in pollutant else 400, 5, 30)
    return pd.DataFrame({'Date': dates, 'Value': vals})

# 4. UI
st.title("GHG Operational Monitor")

# Metrics
metrics = get_latest_data()
st.markdown('<div style="background-color: #0f172a; padding: 20px; border-radius: 10px;">', unsafe_allow_html=True)
cols = st.columns(len(metrics))
for i, (label, val) in enumerate(metrics.items()):
    cols[i].metric(label, val)
st.markdown('</div>', unsafe_allow_html=True)

# Graph
st.subheader("Historical Trends Analysis")
selected = st.selectbox("เลือกสารมลพิษเพื่อดูย้อนหลัง", list(UNIT_MAP.keys()))

df_hist = get_history(selected)

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
