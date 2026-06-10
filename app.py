import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# 1. SETUP: บังคับให้หน้าจอไม่แสดงแถบเลื่อน
st.set_page_config(layout="wide", page_title="GHG Monitor Board", initial_sidebar_state="expanded")

# 2. CSS: ล็อกความสูงและซ่อน Scrollbar
st.markdown("""
    <style>
        /* ซ่อนแถบเลื่อนของแอปทั้งหมด */
        ::-webkit-scrollbar { display: none; }
        .stApp { overflow: hidden !important; height: 100vh !important; }
        
        /* ปรับ Metrics ให้กะทัดรัดที่สุด */
        [data-testid="stMetric"] { 
            background: #161b22; padding: 8px !important; border-radius: 10px; border: 1px solid #30363d;
        }
        [data-testid="stMetricValue"] { font-size: 20px !important; }
        [data-testid="stMetricLabel"] { font-size: 12px !important; }
        
        /* Sidebar layout */
        section[data-testid="stSidebar"] > div { display: flex; flex-direction: column; height: 100vh; }
        .brand-box { margin-top: auto; padding: 15px; background: rgba(255, 255, 255, 0.03); border-radius: 10px; }
    </style>
""", unsafe_allow_html=True)

# 3. CONTENT
st.title("🌍 Tracking GHGs Emission")

# Metrics
metrics_data = {
    "CO₂ (ppm)": "433", "CH₄ (ppb)": "1865", "NO₂ (ppb)": "42.1",
    "PM 2.5 (µg/m³)": "22.4", "Temp (°C)": "33.2", "Humid (%)": "64"
}
cols = st.columns(6)
for i, (label, val) in enumerate(metrics_data.items()):
    cols[i].metric(label=label, value=val)

# Graph: ปรับ height ให้พอดีเป๊ะ
df = pd.DataFrame({'Date': pd.date_range(start='2026-05-01', periods=30), 'Value': np.random.randn(30).cumsum()})
fig = px.line(df, x='Date', y='Value', template="plotly_dark", height=280)
fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", margin=dict(t=20, b=10, l=10, r=10))
st.plotly_chart(fig, use_container_width=True)

# 4. SIDEBAR
with st.sidebar:
    st.markdown("### 📋 เมนูควบคุม")
    selected = st.selectbox("สารมลพิษ:", list(metrics_data.keys()))
    mode = st.radio("รูปแบบ:", ["รายวัน", "รายเดือน"])
    
    st.markdown("""
        <div class="brand-box">
            <img src="https://comci.southeast.ac.th/2025/img/SBU.png" width="40">
            <div style="font-weight:bold; margin-top:5px; color:white; font-size: 12px;">AE-IET [SBU]</div>
            <div style="font-size:9px; color:#888;">Engineering Team</div>
        </div>
    """, unsafe_allow_html=True)
