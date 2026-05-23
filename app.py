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

# 3. DATA
def get_latest_data():
    return {"CO₂ (ppm)": 433, "CH₄ (ppb)": 1865, "NO₂ (ppb)": 42.1, "PM 2.5": 22.4, "Temp (°C)": 33.2, "Humidity (%)": 64}

def get_history(pollutant, mode):
    n = 30
    dates = pd.date_range(end=datetime.now(), periods=n, freq='D')
    vals = np.random.normal(400, 10, n)
    return pd.DataFrame({'Date': dates, 'Value': vals})

# 4. STYLING (เพิ่มการจัดกลุ่ม Sidebar)
st.markdown("""
    <style>
        /* จัดกรอบ Metric */
        [data-testid="stMetricValue"] { font-size: 20px !important; }
        [data-testid="stMetric"] { background-color: #262730; padding: 15px; border-radius: 10px; border: 1px solid #444; }
        
        /* ตรึงกลุ่มล่างสุดของ Sidebar */
        [data-testid="stSidebarContent"] { display: flex; flex-direction: column; height: 100vh; }
        .footer-group { margin-top: auto; padding-bottom: 20px; display: flex; flex-direction: column; gap: 5px; }
    </style>
""", unsafe_allow_html=True)

# Main Title
st.title("Tracking GHGs Emission")

# Metrics Section
metrics = get_latest_data()
cols = st.columns(len(metrics))
for i, (label, val) in enumerate(metrics.items()):
    cols[i].metric(label, val)

# Sidebar UI
selected = st.sidebar.selectbox("เลือกสารมลพิษ", list(UNIT_MAP.keys()))
mode = st.sidebar.radio("รูปแบบการแสดงผล:", ["รายวัน", "รายเดือน"], horizontal=True)

# Sidebar Footer Group (ย้ายมากลุ่มเดียวกันและติดล่างสุด)
with st.sidebar:
    st.markdown('<div class="footer-group">', unsafe_allow_html=True)
    # รูปโลโก้ (ใช้ไฟล์ในเครื่องชื่อ SBU.png)
    st.image("SBU.png", width=100) 
    # ข้อความเครดิตกลุ่มเดียวกัน
    st.markdown("""
        <div style="line-height: 1.2;">
            <div style="font-size: 16px; font-weight: bold;">AE-IET [SBU]</div>
            <div style="font-size: 11px; color: gray;">produced by Engineering</div>
        </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# Graph
df_hist = get_history(selected, mode)
fig = px.line(df_hist, x='Date', y='Value', template="plotly_dark", height=400)
fig.update_layout(margin=dict(l=20, r=20, t=30, b=20), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
st.plotly_chart(fig, use_container_width=True)
