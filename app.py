import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from datetime import datetime

# 1. SETUP & STYLE
st.set_page_config(layout="wide", page_title="GHG Monitor Board")
st.markdown("""
    <style>
    .metric-card { background-color: #0f172a; padding: 20px; border-radius: 10px; border: 1px solid #334155; margin-bottom: 20px; }
    .stApp { background-color: #020617; color: white; }
    </style>
""", unsafe_allow_html=True)

# 2. DATA LAYER (จำลองข้อมูลให้สมจริงตามประเภท)
def get_latest_data():
    return {"CO₂ (ppm)": 433, "CH₄ (ppb)": 1865, "NO₂ (ppb)": 42.1, "PM 2.5": 22.4, "Temp (°C)": 33.2, "Humidity (%)": 64}

def get_history(pollutant):
    dates = pd.date_range(start="2026-05-01", periods=30)
    # logic ปรับค่าตามชนิดมลพิษเพื่อให้กราฟไม่มั่ว
    if "Temp" in pollutant:
        vals = np.random.normal(33, 2, 30)
    elif "CO₂" in pollutant:
        vals = np.random.normal(430, 5, 30)
    else:
        vals = np.random.normal(50, 10, 30)
    return pd.DataFrame({'Date': dates, 'Value': vals})

# 3. DASHBOARD UI
st.title("GHG Operational Monitor")

# --- แถบ Metrics ---
metrics = get_latest_data()
st.markdown('<div class="metric-card">', unsafe_allow_html=True)
cols = st.columns(len(metrics))
for i, (label, val) in enumerate(metrics.items()):
    cols[i].metric(label, val)
st.markdown('</div>', unsafe_allow_html=True)

# --- กราฟย้อนหลัง ---
st.subheader("Historical Trends Analysis")
selected = st.selectbox("เลือกสารมลพิษเพื่อดูย้อนหลัง", list(metrics.keys()))

# ดึงข้อมูลใหม่ตามตัวเลือก
df_hist = get_history(selected)

# กราฟนี้จะปรับสเกล (Autoscale) อัตโนมัติ เพราะไม่ได้ล็อกค่า
fig = px.line(df_hist, x='Date', y='Value', template="plotly_dark")
fig.update_layout(
    paper_bgcolor="rgba(0,0,0,0)", 
    plot_bgcolor="rgba(0,0,0,0)",
    yaxis=dict(autorange=True) # <--- สำคัญ: ปรับสเกลตามข้อมูลที่เข้ามาใหม่
)
st.plotly_chart(fig, use_container_width=True)
