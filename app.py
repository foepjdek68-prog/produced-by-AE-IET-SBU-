import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import time
from datetime import datetime

# 1. PAGE CONFIG
st.set_page_config(layout="wide", page_title="GHG Real-time Monitor")

# 2. LOGIC: ตรวจสอบว่าถึงนาทีที่ 00 หรือยัง
def is_top_of_hour():
    now = datetime.now()
    return now.minute == 0 and now.second < 5 # อนุโลมช่วงเวลาอัปเดต 5 วินาที

# 3. MOCK DATA (ส่วนนี้จะถูกเรียกใหม่ทุกครั้งที่นาทีเป็น 00)
def get_latest_data():
    return {
        "CO₂ (ppm)": 433 + np.random.randint(-2, 2),
        "CH₄ (ppb)": 1865 + np.random.randint(-5, 5),
        "NO₂ (ppb)": 42.1 + np.random.randint(-1, 1),
        "PM 2.5": 22.4 + np.random.randint(-1, 1)
    }

# 4. DASHBOARD UI
st.title("GHG Operational Monitor (Real-time)")
st.caption(f"Last Update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# แสดง Metrics
metrics_data = get_latest_data()
cols = st.columns(len(metrics_data))
for i, (label, val) in enumerate(metrics_data.items()):
    cols[i].metric(label, val)

# 5. AUTO-REFRESH LOGIC
# ระบบจะตรวจสอบทุก 10 วินาที ถ้าถึงนาทีที่ 00 จะสั่งให้หน้าเว็บโหลดใหม่
placeholder = st.empty()
time.sleep(10)
if is_top_of_hour():
    st.rerun()
else:
    placeholder.text("Waiting for next hourly update at :00...")
