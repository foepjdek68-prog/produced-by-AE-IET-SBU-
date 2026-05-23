import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# 1. SETUP
st.set_page_config(layout="wide", page_title="Annual GHG Summary")
st.title("GHG Annual Summary Dashboard")

# 2. ปุ่มเลือกปี (Horizontal Radio Buttons เพื่อความเร็ว)
selected_year = st.radio(
    "เลือกปีที่ต้องการสรุปข้อมูล:",
    [2026, 2025, 2024, 2023],
    horizontal=True
)

# 3. จำลองข้อมูลสรุปรายปี (Mock Data)
def get_annual_data(year):
    # ข้อมูลจำลองรายเดือนสำหรับปีที่เลือก
    dates = pd.date_range(start=f"{year}-01-01", periods=12, freq='M')
    return pd.DataFrame({
        'Date': dates,
        'CO2': np.random.normal(430, 5, 12),
        'PM2.5': np.random.normal(30, 10, 12)
    })

df = get_annual_data(selected_year)

# 4. ส่วนสรุปตัวเลข (KPIs Summary)
st.subheader(f"สรุปภาพรวมปี {selected_year}")
col1, col2, col3 = st.columns(3)
col1.metric("ค่าเฉลี่ย CO₂", f"{df['CO2'].mean():.1f} ppm")
col2.metric("ค่าสูงสุด PM 2.5", f"{df['PM2.5'].max():.1f} µg/m³")
col3.metric("ข้อมูลที่บันทึก", "12 เดือน")

# 5. กราฟสรุปรายปี
st.write("---")
tab1, tab2 = st.tabs(["กราฟ CO₂", "กราฟ PM 2.5"])

with tab1:
    fig1 = px.line(df, x='Date', y='CO2', title=f"แนวโน้ม CO₂ ปี {selected_year}")
    st.plotly_chart(fig1, use_container_width=True)

with tab2:
    fig2 = px.bar(df, x='Date', y='PM2.5', title=f"แนวโน้ม PM 2.5 ปี {selected_year}")
    st.plotly_chart(fig2, use_container_width=True)
