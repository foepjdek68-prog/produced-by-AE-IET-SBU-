import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# --- 1. DATA ACCESS LAYER (ส่วนนี้เชื่อมต่อ Backend API ของคุณ) ---
@st.cache_data
def fetch_historical_data(pollutant, region):
    # ในฐานะผู้เชี่ยวชาญ: ตรงนี้คือจุดที่คุณต้องแก้ไขให้ชี้ไปที่ FastAPI ของคุณ
    # ตัวอย่าง: response = requests.get(f"http://api/history?pollutant={pollutant}&region={region}")
    
    # จำลองข้อมูลย้อนหลังเพื่อให้โค้ดนี้รันได้ทันที
    dates = pd.date_range(start="2026-01-01", periods=100)
    values = np.random.normal(loc=400 if pollutant == 'CO2' else 20, scale=5, size=100)
    return pd.DataFrame({'Date': dates, 'Value': values, 'Pollutant': pollutant})

# --- 2. CONFIG & UI ---
st.set_page_config(layout="wide")
st.title("Historical Trends Analysis")

# --- 3. CONTROLS (ตัวเลือกมลพิษและภูมิภาค) ---
col1, col2 = st.columns(2)
with col1:
    selected_pollutant = st.selectbox("เลือกสารมลพิษ", ["CO2", "CH4", "NO2", "PM2.5"])
with col2:
    selected_region = st.selectbox("เลือกภูมิภาค", ["ภาคกลาง", "ภาคเหนือ", "ภาคใต้"])

# --- 4. EXECUTION & VISUALIZATION ---
# ดึงข้อมูลตามค่าที่เลือก
df = fetch_historical_data(selected_pollutant, selected_region)

# แสดงกราฟ (Professional Line Chart)
st.subheader(f"กราฟแสดงค่า {selected_pollutant} ย้อนหลัง")

fig = px.line(df, x='Date', y='Value', template="plotly_dark")
fig.update_layout(
    xaxis_title="วันที่",
    yaxis_title="ค่าความเข้มข้น",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)"
)
st.plotly_chart(fig, use_container_width=True)

# ตารางข้อมูล
with st.expander("ดูข้อมูลดิบ (Raw Data)"):
    st.dataframe(df)
