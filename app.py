import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from datetime import datetime

# 1. PAGE CONFIG
st.set_page_config(layout="wide", page_title="GHG Monitor Board")

# 2. CSS - จัดสไตล์ให้แถบสถานะดูโดดเด่น
st.markdown("""
    <style>
    .metric-container { background-color: #0f172a; padding: 15px; border-radius: 10px; border: 1px solid #334155; margin-bottom: 20px; }
    .stApp { background-color: #020617; color: white; }
    </style>
""", unsafe_allow_html=True)

# 3. ฟังก์ชันดึงค่าปัจจุบัน (Real-time) และข้อมูลย้อนหลัง
def get_realtime_metrics():
    # ในอนาคต ให้เปลี่ยนเป็น requests.get(".../api/current")
    return {"CO2": 433, "CH4": 1865, "NO2": 42.1, "PM2.5": 22.4}

def get_historical_data(pollutant):
    # ในอนาคต ให้เปลี่ยนเป็น requests.get(".../api/history")
    dates = pd.date_range(start="2026-05-01", periods=30)
    return pd.DataFrame({'Date': dates, 'Value': np.random.normal(400, 10, 30)})

# --- ส่วนที่เพิ่ม: แถบด้านบนแสดงค่าเรียลไทม์ ---
st.title("GHG Operations Center")
metrics = get_realtime_metrics()

st.markdown('<div class="metric-container">', unsafe_allow_html=True)
col1, col2, col3, col4 = st.columns(4)
col1.metric("CO₂ (ppm)", metrics["CO2"], "0.2")
col2.metric("CH₄ (ppb)", metrics["CH4"], "-1.5")
col3.metric("NO₂ (ppb)", metrics["NO2"], "0.1")
col4.metric("PM 2.5", metrics["PM2.5"], "-2.0")
st.markdown('</div>', unsafe_allow_html=True)

# --- ส่วนเดิม: กราฟย้อนหลัง ---
st.subheader("Historical Trends Analysis")
selected_pollutant = st.selectbox("เลือกสารมลพิษเพื่อดูย้อนหลัง", ["CO2", "CH4", "NO2", "PM2.5"])

df_hist = get_historical_data(selected_pollutant)
fig = px.line(df_hist, x='Date', y='Value', template="plotly_dark")
fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
st.plotly_chart(fig, use_container_width=True)
