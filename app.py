import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from datetime import datetime

# 1. SETUP
st.set_page_config(layout="wide", page_title="GHG Monitor Board")

# 2. CSS STYLING (ปรับแต่งให้รันผ่านและสวยงาม)
st.markdown("""
    <style>
        /* ฟอนต์ */
        @import url('https://fonts.googleapis.com/css2?family=Kanit:wght@300;400;500&display=swap');
        html, body, [class*="css"] { font-family: 'Kanit', sans-serif !important; }
        
        .stApp { background-color: #0e1117; }

        /* กรอบ Metric */
        [data-testid="stMetric"] { 
            background: rgba(255,255,255,0.05); padding: 20px; border-radius: 15px; 
            border: 1px solid rgba(255,255,255,0.1); text-align: center;
        }

        /* จัด Sidebar ให้ตรึงล่างสุดแบบชัวร์ๆ */
        section[data-testid="stSidebar"] > div {
            display: flex;
            flex-direction: column;
            height: 100vh;
        }
        .footer-container {
            margin-top: auto; 
            padding: 20px;
            background: rgba(255,255,255,0.03);
            border-radius: 15px;
            text-align: left;
        }
    </style>
""", unsafe_allow_html=True)

# 3. CONTENT
st.title("🌍 Tracking GHGs Emission")

# Metrics
cols = st.columns(6)
data = {"CO₂": 433, "CH₄": 1865, "NO₂": 42.1, "PM2.5": 22.4, "Temp": 33.2, "Humid": 64}
for i, (k, v) in enumerate(data.items()):
    cols[i].metric(k, v)

# Sidebar
with st.sidebar:
    st.markdown("## 📋 เมนูควบคุมระบบ")
    selected = st.selectbox("เลือกสารมลพิษ:", list(data.keys()))
    mode = st.radio("รูปแบบการแสดงผล:", ["รายวัน", "รายเดือน"])
    
    # กลุ่มล่างสุด (ใช้ div ครอบ)
    st.markdown("""
        <div class="footer-container">
            <img src="https://comci.southeast.ac.th/2025/img/SBU.png" width="80">
            <div style="font-weight:bold; margin-top:10px;">AE-IET [SBU]</div>
            <div style="font-size:11px; color:#888;">Produced by Engineering Team</div>
        </div>
    """, unsafe_allow_html=True)

# Graph
df = pd.DataFrame({'Date': pd.date_range(start='2026-05-01', periods=30), 'Value': np.random.randn(30).cumsum()})
fig = px.line(df, x='Date', y='Value', template="plotly_dark")
fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
st.plotly_chart(fig, use_container_width=True)
