import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# 1. Page Configuration
st.set_page_config(layout="wide", page_title="Professional Dashboard")

# 2. Injection Style: คุมหน้าตาแบบเข้ม (Dark Mode & Professional)
st.markdown("""
    <style>
        .stApp { background-color: #0b111e; }
        .metric-card { background: #121826; padding: 20px; border-radius: 12px; border: 1px solid #1e293b; }
        h1, h2, h3 { color: #f8fafc; font-family: 'Inter', sans-serif; }
    </style>
""", unsafe_allow_html=True)

# 3. Helper: สร้างการ์ดข้อมูล (Modularize)
def metric_card(label, value, delta):
    st.markdown(f"""
        <div class="metric-card">
            <div style="color: #94a3b8; font-size: 12px; font-weight: 700;">{label}</div>
            <div style="font-size: 24px; font-weight: 800; color: white;">{value}</div>
            <div style="color: #10b981; font-size: 12px;">{delta}</div>
        </div>
    """, unsafe_allow_html=True)

# 4. Main UI Layout
st.title("Environmental Monitoring System")

# Row 1: Metrics
c1, c2, c3 = st.columns(3)
with c1: metric_card("CO₂ Level", "421.5 ppm", "+0.3% vs last month")
with c2: metric_card("Temp Anomaly", "1.8°C", "+0.1°C")
with c3: metric_card("AQI", "85", "Moderate")

st.write("##") # Spacer

# Row 2: Charts (Grid 2x2)
col_a, col_b = st.columns([1, 1])

with col_a:
    st.subheader("Emission Trend")
    fig = go.Figure(data=go.Scatter(y=[200, 300, 400, 350, 500], mode='lines+markers', line=dict(color='#38bdf8')))
    fig.update_layout(template="plotly_dark", height=300, margin=dict(l=10, r=10, t=10, b=10))
    st.plotly_chart(fig, use_container_width=True)

with col_b:
    st.subheader("Pollution Distribution")
    fig2 = go.Figure(data=go.Bar(y=[12, 15, 8, 22], marker_color='#ef4444'))
    fig2.update_layout(template="plotly_dark", height=300, margin=dict(l=10, r=10, t=10, b=10))
    st.plotly_chart(fig2, use_container_width=True)

# Row 3: Water Quality Table (ตามแบบในรูปที่คุณส่งมา)
st.subheader("Water Quality Monitoring")
data = {
    "River": ["Chao Phraya", "Tha Chin", "Mae Klong"],
    "DO Status": ["PASS", "
