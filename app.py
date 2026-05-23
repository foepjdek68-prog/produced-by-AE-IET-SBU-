import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# 1. การกำหนดตัวแปรให้ตรงตามฐานข้อมูล
POLLUTANT_MAP = {
    "CO (Carbon Monoxide)": "co",
    "NO2 (Nitrogen Dioxide)": "no2",
    "O3 (Ozone)": "o3",
    "SO2 (Sulfur Dioxide)": "so2",
    "PM 2.5": "pm25",
    "Temperature": "temp",
    "Humidity": "humidity"
}

# 2. ฟังก์ชันดึงข้อมูลแบบครอบคลุม
@st.cache_data
def fetch_all_historical_data(pollutant_key, region):
    # เชื่อมต่อ FastAPI ของคุณที่นี่ (ส่ง key ที่ map แล้วไป)
    # response = requests.get(f"http://api/history?param={pollutant_key}&region={region}")
    
    # ข้อมูลจำลอง: สร้างข้อมูลที่รองรับทุกตัวแปรที่คุณต้องการ
    dates = pd.date_range(start="2026-01-01", periods=100)
    data = {
        'Date': dates,
        'Value': np.random.rand(100) * 100, 
        'Type': pollutant_key
    }
    return pd.DataFrame(data)

# 3. UI
st.title("Historical Monitor Board")

# --- ส่วนเลือกค่ามลพิษ ---
selected_pollutant_name = st.selectbox("เลือกสารมลพิษที่จะแสดงบนกราฟ", list(POLLUTANT_MAP.keys()))
pollutant_key = POLLUTANT_MAP[selected_pollutant_name]

# ดึงข้อมูลตาม Key ที่เลือก
df = fetch_all_historical_data(pollutant_key, "ภาคกลาง")

# กราฟแสดงผล
fig = px.line(df, x='Date', y='Value', title=f"Trends of {selected_pollutant_name}")
fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)")
st.plotly_chart(fig, use_container_width=True)

# ตารางแสดงสถานะปัจจุบัน (Metrics)
st.subheader("Current Levels")
col1, col2, col3, col4 = st.columns(4)
col1.metric(selected_pollutant_name, f"{df['Value'].iloc[-1]:.2f}")
