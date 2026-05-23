import streamlit as st
import pandas as pd
import numpy as np

# 1. PAGE CONFIG
st.set_page_config(layout="wide", page_title="GHG Monitor Board")

# 2. CSS - แถบ Metrics ที่ปรับตัวตามจำนวนข้อมูล
st.markdown("""
    <style>
    .metric-container { background-color: #0f172a; padding: 20px; border-radius: 10px; border: 1px solid #334155; margin-bottom: 20px; }
    .stApp { background-color: #020617; color: white; }
    </style>
""", unsafe_allow_html=True)

# 3. จำลองการดึงข้อมูลทุกตัว (Function นี้ต้องส่งคืนข้อมูลที่มีทุกค่า)
def get_all_realtime_metrics():
    # สมมติว่านี่คือข้อมูลที่ API ส่งกลับมา
    return {
        "CO₂ (ppm)": 433,
        "CH₄ (ppb)": 1865,
        "NO₂ (ppb)": 42.1,
        "SO₂ (ppb)": 15.5,
        "O₃ (ppb)": 35.0,
        "Temp (°C)": 33.2,
        "Humidity (%)": 64,
        "PM 2.5": 22.4
    }

# 4. แสดงผลแบบ DYNAMIC (แสดงทุกตัวที่ดึงมา)
st.title("GHG Operational Monitor")

metrics = get_all_realtime_metrics()

# สร้างแถวที่คำนวณจำนวนคอลัมน์ให้อัตโนมัติ (เช่น แบ่งทีละ 4-6 ตัวต่อแถว)
st.markdown('<div class="metric-container">', unsafe_allow_html=True)
cols = st.columns(len(metrics)) # สร้างคอลัมน์ตามจำนวนข้อมูลจริง

for i, (label, value) in enumerate(metrics.items()):
    cols[i].metric(label, value)
st.markdown('</div>', unsafe_allow_html=True)

# 5. กราฟย้อนหลัง (ยังคงใช้การเลือกตามเดิม)
st.subheader("Historical Trends Analysis")
selected_pollutant = st.selectbox("เลือกสารมลพิษเพื่อดูย้อนหลัง", list(metrics.keys()))
# ... (ส่วนกราฟของคุณ)
