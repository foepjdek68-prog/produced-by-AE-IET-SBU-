import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from datetime import datetime

# 1. SETUP
st.set_page_config(layout="wide", page_title="GHG Monitor Board")

# 2. MAPPING (ใส่หน่วยกำกับให้ชัดเจน)
DATA_MAP = {
    "CO₂": "433 ppm",
    "CH₄": "1865 ppb",
    "NO₂": "42.1 ppb",
    "PM2.5": "22.4 µg/m³",
    "Temp": "33.2 °C",
    "Humid": "64 %"
}

# 3. CSS STYLING
st.markdown("""
    <style>
        section[data-testid="stSidebar"] > div { display: flex; flex-direction: column; height: 100vh; }
        .brand-box { margin-top: auto; padding: 20px; background: rgba(255, 255, 255, 0.03); border-radius: 12px; border: 1px solid rgba(255, 255, 255, 0.05); }
        [data-testid="stMetric"] { background: #161b22; padding: 20px; border-radius: 12px; border: 1px solid #30363d; }
    </style>
""", unsafe_allow_html=True)

# 4. CONTENT
st.title("🌍 Tracking GHGs Emission")

# Metrics Display (แยกค่าและหน่วย)
cols = st.columns(6)
for i, (k, v) in enumerate(DATA_MAP.items()):
    val_only = v.split(" ")[0]
    unit_only = " ".join(v.split(" ")[1:])
    cols[i].metric(label=k, value=val_only, help=unit_only) # ใช้ help แสดงหน่วย หรือจะเขียนต่อท้ายก็ได้

# หากต้องการให้หน่วยโชว์ตรงๆ ในกรอบ Metric ให้ใช้แบบนี้ครับ:
cols = st.columns(6)
for i, (k, v) in enumerate(DATA_MAP.items()):
    cols[i].metric(label=k, value=v) # ใส่ค่าเต็มที่มีหน่วยเข้าไปเลย

# Graph
df = pd.DataFrame({'Date': pd.date_range(start='2026-05-01', periods=30), 'Value': np.random.randn(30).cumsum()})
fig = px.line(df, x='Date', y='Value', template="plotly_dark")
fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
st.plotly_chart(fig, use_container_width=True)

# 5. SIDEBAR
with st.sidebar:
    st.markdown("### 📋 เมนูควบคุม")
    selected = st.selectbox("เลือกสารมลพิษ:", list(DATA_MAP.keys()))
    mode = st.radio("รูปแบบ:", ["รายวัน", "รายเดือน"])
    
    st.markdown("""
        <div class="brand-box">
            <img src="https://comci.southeast.ac.th/2025/img/SBU.png" width="70">
            <div style="font-weight:bold; margin-top:10px; color:white;">AE-IET [SBU]</div>
            <div style="font-size:11px; color:#888;">Produced by Engineering Team</div>
        </div>
    """, unsafe_allow_html=True)
