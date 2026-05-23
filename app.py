import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# ... (ส่วน Setup และ Data Simulation เหมือนเดิม)

# 3. DASHBOARD UI
st.title("GHG Operational Monitor")

# ... (ส่วน Metric Bar เหมือนเดิม)

# กราฟย้อนหลัง
st.subheader("Historical Trends Analysis")
selected = st.selectbox("เลือกสารมลพิษเพื่อดูย้อนหลัง", list(UNIT_MAP.keys()))

df_hist = get_history(selected)

# สร้างกราฟพร้อมแกน Y ที่ถูกต้อง
fig = px.line(df_hist, x='Date', y='Value', template="plotly_dark")
fig.update_layout(
    xaxis_title="Date",
    yaxis_title=UNIT_MAP[selected], # เรียกใช้คำที่เหมาะสมจาก Mapping
    paper_bgcolor="rgba(0,0,0,0)", 
    plot_bgcolor="rgba(0,0,0,0)",
    yaxis=dict(autorange=True)
)
st.plotly_chart(fig, use_container_width=True)
