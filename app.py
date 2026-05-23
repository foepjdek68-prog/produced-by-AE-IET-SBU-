import streamlit as st
import pandas as pd
import plotly.express as px
import pydeck as pdk
import requests
from datetime import datetime, timedelta

# --- 1. CONFIG & STYLE ---
st.set_page_config(layout="wide", page_title="GHG Historical Dashboard")
st.markdown("""
    <style>
    .card { background-color: #0f172a; padding: 20px; border-radius: 10px; border: 1px solid #334155; margin-bottom: 15px; }
    .stApp { background-color: #020617; color: white; }
    </style>
""", unsafe_allow_html=True)

# --- 2. DATA LAYER (ส่วนนี้คือหัวใจของการดึงข้อมูลย้อนหลัง) ---
def get_historical_data(start_date, end_date, region):
    # ตรงนี้คือจุดที่คุณต้องเชื่อมกับ FastAPI เพื่อดึงข้อมูลจาก PostgreSQL
    # เช่น: response = requests.get(f"http://api/history?start={start_date}&end={end_date}")
    # ในที่นี้ใช้ข้อมูลจำลองเพื่อรันให้คุณเห็นภาพ
    dates = pd.date_range(start=start_date, end=end_date)
    data = {
        'Date': dates,
        'Value': [400 + (i*0.5) for i in range(len(dates))],
        'Region': region
    }
    return pd.DataFrame(data)

# --- 3. UI LAYOUT ---
st.title("GHG Historical Monitor")

with st.sidebar:
    st.subheader("⚙️ Historical Controls")
    start_date = st.date_input("Start Date", datetime.now() - timedelta(days=30))
    end_date = st.date_input("End Date", datetime.now())
    region_sel = st.selectbox("Select Region", ["ภาคกลาง", "ภาคเหนือ", "ภาคใต้"])
    
    if st.button("Fetch Historical Data"):
        st.session_state.data = get_historical_data(start_date, end_date, region_sel)

# --- 4. MAIN DISPLAY ---
if 'data' in st.session_state:
    df = st.session_state.data
    
    col_main, col_side = st.columns([2, 1])
    
    with col_main:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader(f"📈 Trends: {region_sel} ({start_date} to {end_date})")
        fig = px.line(df, x='Date', y='Value')
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="white")
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col_side:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("📋 Summary")
        st.write(f"Avg Value: {df['Value'].mean():.2f}")
        st.table(df.tail(5))
        st.markdown('</div>', unsafe_allow_html=True)
else:
    st.info("กรุณาเลือกช่วงเวลาและกดปุ่ม Fetch Historical Data เพื่อเริ่มดูข้อมูลย้อนหลัง")
