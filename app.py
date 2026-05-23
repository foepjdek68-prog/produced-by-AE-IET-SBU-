import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# 1. ประกาศตัวแปรพื้นฐานก่อนเสมอ
st.set_page_config(layout="wide")
st.title("GHG Historical Analysis")

# 2. สร้างรายการสารมลพิษ (เป็น List ธรรมดา)
pollutants = ["CO2", "CH4", "NO2", "PM2.5", "Temp"]

# 3. สร้าง Layout แบบ Column
col1, col2 = st.columns([1, 3])

with col1:
    # 4. Selector สำหรับเลือกปีและสารมลพิษ
    year = st.selectbox("เลือกปี:", [2026, 2025, 2024, 2023])
    pollutant = st.selectbox("เลือกสารมลพิษ:", pollutants)

with col2:
    # 5. สร้างข้อมูลจำลอง (ไม่ต้องเชื่อม API ก่อน เพื่อทดสอบว่ารันขึ้นไหม)
    dates = pd.date_range(start=f"{year}-01-01", periods=12, freq='M')
    values = np.random.rand(12) * 100
    df = pd.DataFrame({'Date': dates, 'Value': values})
    
    # 6. สร้างกราฟ
    fig = px.line(df, x='Date', y='Value', title=f"ข้อมูลปี {year} ของ {pollutant}")
    st.plotly_chart(fig, use_container_width=True)

# 7. จบแค่นี้ก่อนเพื่อให้รันผ่าน
