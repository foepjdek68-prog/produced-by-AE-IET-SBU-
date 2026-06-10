import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(layout="wide")

# ข้อมูลจำลอง
st.title("Environmental Dashboard")

# ทดสอบการทำงานด้วยการสร้างกราฟที่ง่ายที่สุด
df = pd.DataFrame({
    'x': [1, 2, 3, 4],
    'y': [10, 20, 15, 25]
})

fig = go.Figure(data=go.Scatter(x=df['x'], y=df['y'], mode='lines+markers'))
fig.update_layout(template="plotly_dark")

st.plotly_chart(fig)

st.write("ถ้าคุณเห็นกราฟนี้แสดงว่าระบบ Python ของคุณปกติ")
