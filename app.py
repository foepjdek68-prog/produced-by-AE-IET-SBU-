import streamlit as st
import pandas as pd
import plotly.express as px
import pydeck as pdk

# 1. ตั้งค่าหน้าจอ
st.set_page_config(layout="wide", page_title="GHG Monitor Board")

# 2. CSS สำหรับตกแต่ง (Dark Mode & Cards)
st.markdown("""
    <style>
    .card { background-color: #0f172a; padding: 20px; border-radius: 10px; border: 1px solid #334155; margin-bottom: 15px; }
    .stApp { background-color: #020617; color: white; }
    </style>
""", unsafe_allow_html=True)

# 3. ข้อมูลจำลอง (Mock Data)
data = {'Region': ['ภาคกลาง', 'ภาคเหนือ', 'ภาคใต้', 'ภาคอีสาน', 'ภาคตะวันออก', 'ภาคตะวันตก'],
        'Value': [433, 412, 405, 418, 420, 410]}
df = pd.DataFrame(data)

# 4. HEADER & METRICS
st.title("Monitor Board")
m1, m2, m3, m4, m5, m6 = st.columns(6)
m1.metric("CO₂", "433 ppm")
m2.metric("CH₄", "1865 ppb")
m3.metric("NO₂", "42.1 ppb")
m4.metric("Temp", "33.2 °C")
m5.metric("PM 2.5", "22.4")
m6.metric("Humidity", "64 %")

# 5. MAIN LAYOUT (แบ่ง 2:1)
col_main, col_side = st.columns([2, 1])

with col_main:
    # แผนที่
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("🗺️ Global/Regional Map")
    st.pydeck_chart(pdk.Deck(
        initial_view_state=pdk.ViewState(latitude=13.0, longitude=101.0, zoom=4, pitch=0),
        layers=[]
    ))
    st.markdown('</div>', unsafe_allow_html=True)
    
    # กราฟ
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("📈 Trends Analysis")
    fig = px.line(df, x='Region', y='Value')
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="white")
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col_side:
    # แผงควบคุม
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("⚙️ Controls")
    metric_choice = st.selectbox("เลือกสารมลพิษ/ตัวชี้วัด", 
                                 ["คาร์บอนไดออกไซด์ (CO₂)", "ก๊าซมีเทน (CH₄)", "ไนโตรเจนไดออกไซด์ (NO₂)", 
                                  "อุณหภูมิอากาศ (TEMP)", "ฝุ่น PM 2.5", "ความชื้น (HUMIDITY)"])
    region_choice = st.selectbox("เลือกภูมิภาค", 
                                 ["ภาคกลาง", "ภาคเหนือ", "ภาคใต้", "ภาคอีสาน", "ภาคตะวันออก", "ภาคตะวันตก"])
    st.markdown('</div>', unsafe_allow_html=True)
    
    # ตาราง
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("📋 Data Table")
    st.table(df)
    st.markdown('</div>', unsafe_allow_html=True)
