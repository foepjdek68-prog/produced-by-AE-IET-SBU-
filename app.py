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
    # แก้ไขบั๊กตรงนี้: กำหนดจำนวนวันแยกชัดเจน
    n = 12 if mode == "รายเดือน" else 30
    freq = 'MS' if mode == "รายเดือน" else 'D'
    
    dates = pd.date_range(end=datetime.now(), periods=n, freq=freq)
    
    mapping = {"Temp": 30, "CO₂": 430, "CH₄": 1800, "NO₂": 40, "PM 2.5": 25, "Humidity": 60}
    base = next((val for key, val in mapping.items() if key in pollutant), 50)
    
    # สร้างข้อมูลสุ่มโดยใช้ n
    vals = np.random.normal(base, 5, n)
    return pd.DataFrame({'Date': dates, 'Value': vals})

# 4. UI
col_h1, col_h2 = st.columns([4, 1])
with col_h1:
    st.title("Tracking GHGs Emission")
    st.subheader("Dashboard ระบบติดตามการปล่อยก๊าซเรือนกระจก")
with col_h2:
    st.image("https://comci.southeast.ac.th/2025/img/SBU.png", width=120)
    st.caption("SBU - Engineering")

with st.sidebar:
    st.header("Settings")
    selected = st.selectbox("เลือกสารมลพิษ", list(UNIT_MAP.keys()))
    mode = st.radio("รูปแบบการแสดงผล:", ["รายวัน", "รายเดือน"], horizontal=True)
    
    st.markdown("---")
    st.markdown(
        """
        <div style="font-size: 10px; color: gray;">
            produced by AE-IET [SBU]
        </div>
        """, 
        unsafe_allow_html=True
    )

# Metrics
metrics = get_latest_data()
cols = st.columns(len(metrics))
for i, (label, val) in enumerate(metrics.items()):
    cols[i].metric(label, val)

# Graph
df_hist = get_history(selected, mode)
fig = px.line(df_hist, x='Date', y='Value', template="plotly_dark", height=400)
fig.update_layout(
    margin=dict(l=20, r=20, t=30, b=20),
    yaxis_title=UNIT_MAP[selected],
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)"
)
fig.update_traces(mode='lines+markers')
st.plotly_chart(fig, use_container_width=True)
