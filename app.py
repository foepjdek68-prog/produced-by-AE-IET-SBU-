import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# 1. SETUP
st.set_page_config(layout="wide")
st.title("GHG Operational Monitor")

# 2. จำลองข้อมูล (ใช้ฟังก์ชันเพื่อแยกส่วน Data)
def get_metrics():
    return {"CO₂": 433, "CH₄": 1865, "NO₂": 42.1, "PM 2.5": 22.4}

def get_data_by_year(year, pollutant):
    # ข้อมูลย้อนหลังของปีที่เลือก
    dates = pd.date_range(start=f"{year}-01-01", end=f"{year}-12-31", freq='M')
    return pd.DataFrame({'Date': dates, 'Value': np.random.rand(len(dates)) * 100})

# 3. แถบเรียลไทม์ (ส่วนที่ชอบที่สุด)
metrics = get_metrics()
cols = st.columns(len(metrics))
for i, (label, val) in enumerate(metrics.items()):
    cols[i].metric(label, val)

st.write("---")

# 4. ส่วนเลือกปีและมลพิษ (รวมอยู่ในแถวเดียว เพื่อไม่ให้เสียพื้นที่)
col1, col2, col3 = st.columns([1, 1, 2])
with col1:
    year = st.selectbox("เลือกปี:", [2026, 2025, 2024, 2023])
with col2:
    pollutant = st.selectbox("เลือกสารมลพิษ:", list(metrics.keys()))

# 5. กราฟ (เอาส่วนกราฟกลับมาในรูปแบบเดิม)
df = get_data_by_year(year, pollutant)
fig = px.line(df, x='Date', y='Value', title=f"แนวโน้ม {pollutant} ปี {year}")
fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
st.plotly_chart(fig, use_container_width=True)
