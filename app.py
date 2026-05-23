import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# 1. SETUP & MAPPING
st.set_page_config(layout="wide", page_title="GHG Historical Explorer")
UNIT_MAP = {
    "CO₂ (ppm)": "Concentration (ppm)",
    "CH₄ (ppb)": "Concentration (ppb)",
    "NO₂ (ppb)": "Concentration (ppb)",
    "PM 2.5": "Concentration (µg/m³)",
    "Temp (°C)": "Temperature (°C)"
}

# 2. DATA LAYER: ดึงข้อมูลตามปี
def get_data_for_year(pollutant, year):
    # นี่คือ Logic ที่คุณจะไปต่อกับ PostgreSQL
    # เช่น: "SELECT * FROM ghg_data WHERE year = {year} AND type = '{pollutant}'"
    dates = pd.date_range(start=f"{year}-01-01", end=f"{year}-12-31", freq='M')
    vals = np.random.normal(30 if "Temp" in pollutant else 400, 10, len(dates))
    return pd.DataFrame({'Date': dates, 'Value': vals})

# 3. DASHBOARD UI
st.title("GHG Historical Explorer")

# ส่วนเลือกปีและมลพิษ
col1, col2 = st.columns([1, 3])
with col1:
    selected_year = st.selectbox("เลือกปีที่ต้องการดู", [2026, 2025, 2024, 2023, 2022])
    selected_pollutant = st.selectbox("เลือกสารมลพิษ", list(UNIT_MAP.keys()))

with col2:
    st.subheader(f"วิเคราะห์ข้อมูลประจำปี: {selected_year}")
    df = get_data_for_year(selected_pollutant, selected_year)
    
    fig = px.line(df, x='Date', y='Value', template="plotly_dark")
    fig.update_layout(
        yaxis_title=UNIT_MAP[selected_pollutant],
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )
    st.plotly_chart(fig, use_container_width=True)

# 4. DATA TABLE (สำหรับดูข้อมูลละเอียดรายปี)
with st.expander("ดูตารางข้อมูลรายเดือน"):
    st.dataframe(df, use_container_width=True)
