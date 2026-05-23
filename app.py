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

# 2. DATA LAYER (ฟังก์ชันสำหรับดึงค่า)
def get_latest_data():
    # ในอนาคตเปลี่ยนเป็น API Call
    return {"CO₂ (ppm)": 433, "CH₄ (ppb)": 1865, "NO₂ (ppb)": 42.1, "PM 2.5": 22.4, "Temp (°C)": 33.2, "Humidity (%)": 64}

def get_history(pollutant):
    dates = pd.date_range(start="2026-05-01", periods=30)
    return pd.DataFrame({'Date': dates, 'Value': np.random.normal(400, 20, 30)})

# 3. DASHBOARD UI
st.title("GHG Operational Monitor")
st.caption(f"Status: Live | Last Update: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

# --- แถบ Metrics ด้านบน (เรียลไทม์) ---
metrics = get_latest_data()
st.markdown('<div class="metric-card">', unsafe_allow_html=True)
cols = st.columns(len(metrics))
for i, (label, val) in enumerate(metrics.items()):
    cols[i].metric(label, val)
st.markdown('</div>', unsafe_allow_html=True)

# --- ส่วนกราฟย้อนหลัง (ด้านล่าง) ---
col_graph, col_ctrl = st.columns([3, 1])

with col_graph:
    st.subheader("Historical Trends Analysis")
    selected = st.selectbox("เลือกสารมลพิษเพื่อดูย้อนหลัง", list(metrics.keys()))
    df_hist = get_history(selected)
    fig = px.line(df_hist, x='Date', y='Value', template="plotly_dark")
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig, use_container_width=True)

with col_ctrl:
    st.subheader("⚙️ System Control")
    st.write("โหมดการทำงาน: **อัตโนมัติ**")
    st.info("ระบบจะอัปเดตค่าปัจจุบันทุกต้นชั่วโมง (:00)")
    if st.button("Force Refresh Data"):
        st.rerun()

# 4. AUTO-REFRESH LOGIC (เช็กทุกต้นชั่วโมง)
if datetime.now().minute == 0:
    st.rerun()
