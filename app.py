import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime

# ตั้งค่าหน้าจอ
st.set_page_config(layout="wide", page_title="Environmental Dashboard")

# ใส่ CSS เพื่อความสวยงามและเสถียรของ UI
st.markdown("""
    <style>
        .main { background-color: #0b111e; }
        .stMetric { background-color: #121826; padding: 20px; border-radius: 10px; }
    </style>
""", unsafe_allow_html=True)

# 1. จัดเตรียมข้อมูล (Data Mock)
def get_data():
    return {
        "co2": 421.5,
        "temp": 1.8,
        "aqi": 85,
        "history": [250, 390, 520, 680, 810, 1020, 1420]
    }

data = get_data()

# 2. หัวข้อ
st.title("📊 Intelligent Environmental Monitoring")
st.write(f"Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# 3. แสดง Metric (แก้ไขปัญหาการแสดงผลซ้อน)
col1, col2, col3 = st.columns(3)
col1.metric("CO₂ Level", f"{data['co2']} ppm", "+0.3%")
col2.metric("Temp Anomaly", f"{data['temp']}°C", "+0.1°C")
col3.metric("AQI", data['aqi'], "Moderate")

# 4. แสดงกราฟ (แก้ไขการจัดการ Object)
st.subheader("Emission Trends")
fig = go.Figure(data=go.Scatter(
