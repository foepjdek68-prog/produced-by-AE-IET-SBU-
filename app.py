import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from datetime import datetime

# 1. SETUP
st.set_page_config(layout="wide", page_title="GHG Monitor Board")

# 2. CSS STYLING: ปรับพื้นหลัง Sidebar และตรึง Footer
st.markdown("""
    <style>
        /* ปรับสีพื้นหลัง Sidebar ให้ดูพรีเมียม */
        [data-testid="stSidebar"] { 
            background-color: #0b0e14 !important; 
            border-right: 1px solid #262730;
        }
        
        /* ตรึงตำแหน่ง Footer ไว้ล่างสุดของ Sidebar */
        section[data-testid="stSidebar"] > div {
            display: flex;
            flex-direction: column;
            height: 100vh;
        }
        
        /* สไตล์กรอบแบรนด์ด้านล่าง */
        .brand-box {
            margin-top: auto;
            padding: 20px;
            background: rgba(255, 255, 255, 0.03);
            border-radius: 12px;
            border: 1px solid rgba(255, 255, 255, 0.05);
        }
        
        /* สไตล์ Metric */
        [data-testid="stMetric"] { 
            background: #161b22; padding: 20px; border-radius: 12px; border: 1px solid #30363d;
        }
    </style>
""", unsafe_allow_html=True)

# 3. CONTENT
st.title("🌍 Tracking GHGs Emission")

# Metrics
data = {"CO₂": 433, "CH₄": 1865, "NO₂": 42.1, "PM2.5": 22.4, "Temp": 33.2, "Humid": 64}
cols = st.columns(len(data))
for i, (k, v) in enumerate(data.items()):
    cols[i].metric(k, v)

# SIDEBAR: ปรับให้เหลือแค่เมนูหลัก
with st.sidebar:
    st.markdown("### 📋 เมนูควบคุม")
    selected = st.selectbox("เลือกสารมลพิษ:", list(data.keys()))
    mode = st.radio("รูปแบบ:", ["รายวัน", "รายเดือน"])
    
    # กลุ่มแบรนด์ (ย้ายไปล่างสุด)
    st.markdown("""
        <div class="brand-box">
            <img src="https://comci.southeast.ac.th/2025/img/SBU.png" width="70">
            <div style="font-weight:bold; margin-top:10px; color:white;">AE-IET [SBU]</div>
            <div style="font-size:11px; color:#888;">Produced by Engineering Team</div>
        </div>
    """, unsafe_allow_html=True)

# Graph
df = pd.DataFrame({'Date': pd.date_range(start='2026-05-01', periods=30), 'Value': np.random.randn(30).cumsum()})
fig = px.line(df, x='Date', y='Value', template="plotly_dark")
fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
st.plotly_chart(fig, use_container_width=True)
