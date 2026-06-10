import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from datetime import datetime
import pytz
import random

# 1. SETUP: บังคับให้หน้าจอไม่แสดงแถบเลื่อน
st.set_page_config(layout="wide", page_title="GHG Monitor Board", initial_sidebar_state="expanded")

# 2. CSS: ล็อกความสูงและซ่อน Scrollbar
st.markdown("""
    <style>
        ::-webkit-scrollbar { display: none; }
        .stApp { overflow: hidden !important; height: 100vh !important; }
        
        /* ปรับ Metrics ให้กะทัดรัดที่สุด */
        [data-testid="stMetric"] { 
            background: #161b22; padding: 8px !important; border-radius: 10px; border: 1px solid #30363d;
        }
        [data-testid="stMetricValue"] { font-size: 20px !important; }
        [data-testid="stMetricLabel"] { font-size: 12px !important; }
        
        /* Sidebar layout */
        section[data-testid="stSidebar"] > div { display: flex; flex-direction: column; height: 100vh; }
        .brand-box { margin-top: auto; padding: 15px; background: rgba(255, 255, 255, 0.03); border-radius: 10px; }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# ฟังก์ชันดึงข้อมูล: จุดนี้คือที่ที่คุณต้องนำ API หรือ Database จริงมาเชื่อม
# ---------------------------------------------------------
@st.cache_data(ttl=60)
def get_sensor_data():

    bkk_tz = pytz.timezone('Asia/Bangkok')
    now = datetime.now(bkk_tz)

    if "history_df" not in st.session_state:

        dates = pd.date_range(
            end=now,
            periods=24,
            freq="h"
        )

        df = pd.DataFrame({
            'Date': dates,
            'CO₂ (ppm)': np.random.normal(415, 10, 24).round(1),
            'CH₄ (ppb)': np.random.normal(1850, 20, 24).round(1),
            'NO₂ (ppb)': np.random.normal(40, 5, 24).round(1),
            'PM 2.5 (µg/m³)': np.random.normal(25, 8, 24).round(1),
            'Temp (°C)': np.random.normal(33, 2, 24).round(1),
            'Humid (%)': np.random.normal(60, 5, 24).round(1)
        })

        st.session_state.history_df = df

    else:

        df = st.session_state.history_df.copy()

        new_row = {
            'Date': now,
            'CO₂ (ppm)': round(df['CO₂ (ppm)'].iloc[-1] + random.uniform(-2, 2), 1),
            'CH₄ (ppb)': round(df['CH₄ (ppb)'].iloc[-1] + random.uniform(-10, 10), 1),
            'NO₂ (ppb)': round(df['NO₂ (ppb)'].iloc[-1] + random.uniform(-1, 1), 1),
            'PM 2.5 (µg/m³)': round(df['PM 2.5 (µg/m³)'].iloc[-1] + random.uniform(-2, 2), 1),
            'Temp (°C)': round(df['Temp (°C)'].iloc[-1] + random.uniform(-0.5, 0.5), 1),
            'Humid (%)': round(df['Humid (%)'].iloc[-1] + random.uniform(-1, 1), 1),
        }

        df.loc[len(df)] = new_row

        if len(df) > 24:
            df = df.tail(24).reset_index(drop=True)

        st.session_state.history_df = df

    return st.session_state.history_df, now

# ดึงข้อมูล
df, current_time = get_sensor_data()
latest_data = df.iloc[-1] # ดึงข้อมูลแถวสุดท้าย (ล่าสุด) มาแสดงที่ Metric

# 3. SIDEBAR (ย้ายขึ้นมาบนเพื่อรับค่าก่อนไปวาดกราฟ)
with st.sidebar:
    st.markdown("### 📋 เมนูควบคุม")
    
    # ดึงรายชื่อคอลัมน์ยกเว้นคอลัมน์ 'Date'
    pollutants = [col for col in df.columns if col != 'Date']
    selected_pollutant = st.selectbox("สารมลพิษที่ต้องการดูสถิติ:", pollutants)
    mode = st.radio("รูปแบบข้อมูล:", ["รายชั่วโมง (24h)", "รายวัน"])
    
    # ปุ่มกด Refresh ข้อมูลด้วยตัวเอง
    if st.button("🔄 อัปเดตข้อมูลตอนนี้"):
    if "history_df" in st.session_state:
        del st.session_state["history_df"]

    st.cache_data.clear()
    st.rerun()
    
    st.markdown("""
        <div class="brand-box">
            <img src="https://comci.southeast.ac.th/2025/img/SBU.png" width="40">
            <div style="font-weight:bold; margin-top:5px; color:white; font-size: 12px;">AE-IET [SBU]</div>
            <div style="font-size:9px; color:#888;">Engineering Team</div>
        </div>
    """, unsafe_allow_html=True)

# 4. CONTENT
# Header แสดงเวลาอัปเดตล่าสุด
col_title, col_time = st.columns([2, 1])
with col_title:
    st.title("🌍 Tracking GHGs Emission")
with col_time:
    st.markdown(f"<div style='text-align: right; margin-top: 25px; color: #888;'>🕒 อัปเดตล่าสุด: {current_time.strftime('%Y-%m-%d %H:%M:%S')}</div>", unsafe_allow_html=True)

# Metrics (แสดงค่าล่าสุดที่ตรงกับกราฟจุดสุดท้ายเป๊ะๆ)
cols = st.columns(6)
for i, col_name in enumerate(pollutants):
    val = latest_data[col_name]
    # หาค่าความต่างจากชั่วโมงที่แล้ว (เพื่อทำลูกศรขึ้นลง)
    delta_val = (val - df.iloc[-2][col_name]).round(1) 
    cols[i].metric(label=col_name, value=f"{val}", delta=f"{delta_val}")

# Graph: แสดงกราฟตามที่เลือกใน Sidebar
fig = px.line(df, x='Date', y=selected_pollutant, 
              title=f"แนวโน้ม {selected_pollutant} ในช่วง 24 ชั่วโมงที่ผ่านมา",
              template="plotly_dark", height=300)

# ตกแต่งกราฟเพิ่มเติม
fig.update_traces(line_color='#00ffcc', line_width=3)
fig.update_layout(
    paper_bgcolor="rgba(0,0,0,0)", 
    plot_bgcolor="rgba(0,0,0,0)", 
    margin=dict(t=40, b=10, l=10, r=10),
    xaxis_title=None,
    yaxis_title=None
)
st.plotly_chart(fig, use_container_width=True)
