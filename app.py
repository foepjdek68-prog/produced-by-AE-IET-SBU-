import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# 1. SETUP
st.set_page_config(layout="wide")
st.title("GHG Operational Monitor")

# 2. จำลองข้อมูล (ใช้ฟังก์ชันแยกส่วน Data)
def get_metrics():
    # ค่าปัจจุบัน (Real-time)
    return {"CO₂": 433, "CH₄": 1865, "NO₂": 42.1, "PM 2.5": 22.4}

def get_data(year, pollutant):
    # ข้อมูลย้อนหลังตามปีและชนิดมลพิษ
    dates = pd.date_range(start=f"{year}-01-01", end=f"{year}-12-31", freq='M')
    return pd.DataFrame({'Date': dates, 'Value': np.random.rand(len(dates)) * 100})

# 3. แสดงค่าปัจจุบันด้านบน
metrics = get_metrics()
cols = st.columns(len(metrics))
for i, (label, val) in enumerate(metrics.items()):
    cols[i].metric(label, val)

st.write("---")

# 4. ส่วนเลือกข้อมูลและแสดงกราฟ (รูปแบบดั้งเดิม)
selected_year = st.selectbox("เลือกปีที่ต้องการดูข้อมูล:", [2026, 2025, 2024, 2023])
selected_pollutant = st.selectbox("เลือกสารมลพิษ:", list(metrics.keys()))

# 5. แสดงกราฟ
df = get_data(selected_year, selected_pollutant)
fig = px.line(df, x='Date', y='Value', title=f"แนวโน้ม {selected_pollutant} ประจำปี {selected_year}")
fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
st.plotly_chart(fig, use_container_width=True)
