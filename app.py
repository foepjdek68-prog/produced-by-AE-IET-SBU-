import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# กำหนด Config ให้หน้าจอเต็มความกว้าง
st.set_page_config(layout="wide", page_title="Environmental Dashboard")

# 1. CSS จัดระเบียบการ์ด
st.markdown("""
    <style>
        .card { background-color: #121826; padding: 20px; border-radius: 10px; border: 1px solid #1e293b; margin-bottom: 20px; }
    </style>
""", unsafe_allow_html=True)

st.title("📊 Environmental Monitoring System")

# 2. จัด Layout ส่วนบน (Metrics)
m1, m2, m3 = st.columns(3)
m1.metric("CO₂ Level", "421.5 ppm", "+0.3%")
m2.metric("Temp Anomaly", "1.8°C", "+0.1°C")
m3.metric("AQI", "85", "Moderate")

st.markdown("---")

# 3. จัด Layout ส่วนกลาง (Charts & Maps) - ใช้ Columns 2 ส่วน
col_left, col_right = st.columns([1, 1])

with col_left:
    st.subheader("Emission Trends")
    # ตัวอย่างกราฟที่คุมขนาดไว้ในกรอบ
    fig = go.Figure(data=go.Scatter(x=[1,2,3,4], y=[10,20,15,25], mode='lines'))
    fig.update_layout(template="plotly_dark", height=300, margin=dict(l=20,r=20,t=20,b=20))
    st.plotly_chart(fig, use_container_width=True)

with col_right:
    st.subheader("Regional Heatmap")
    # ตรวจสอบว่า Contour ไม่ล้นกรอบ
    x = np.linspace(0, 10, 50)
    y = np.linspace(0, 10, 50)
    X, Y = np.meshgrid(x, y)
    Z = np.sin(X) * np.cos(Y)
