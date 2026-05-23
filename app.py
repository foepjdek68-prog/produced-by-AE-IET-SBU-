import streamlit as st
import pandas as pd
import plotly.express as px
import pydeck as pdk

# --- 1. CONFIGURATION & STYLE (หัวใจหลักของ UI) ---
st.set_page_config(layout="wide", page_title="GHG Monitor Board")
st.markdown("""
    <style>
    .stApp { background-color: #020617; color: white; }
    .card { background-color: #0f172a; padding: 20px; border-radius: 10px; border: 1px solid #334155; margin-bottom: 15px; }
    </style>
""", unsafe_allow_html=True)

# --- 2. DATA SOURCE MOCKUP (จำลองตามส่วน "รวบรวมข้อมูล" ในแผนผัง) ---
# นี่คือส่วนที่จะไปดึงจาก FastAPI/PostgreSQL ของคุณในอนาคต
@st.cache_data
def get_mock_data():
    data = {
        'Region': ['ภาคกลาง', 'ภาคเหนือ', 'ภาคใต้', 'ภาคอีสาน', 'ภาคตะวันออก', 'ภาคตะวันตก'],
        'co2': [433, 412, 405, 418, 420, 410],
        'ch4': [1865, 1810, 1800, 1830, 1845, 1820],
        'lat': [13.75, 18.78, 7.88, 14.97, 12.92, 13.52],
        'lon': [100.50, 98.98, 98.39, 102.10, 100.88, 99.81]
    }
    return pd.DataFrame(data)

df = get_mock_data()

# --- 3. DASHBOARD UI (แสดงผลตาม Architecture) ---
st.title("Monitor Board")

# Metric Bar (แสดงผลตามส่วน "แสดงผล")
m1, m2, m3, m4, m5, m6 = st.columns(6)
m1.metric("CO₂", "433 ppm")
m2.metric("CH₄", "1865 ppb")
m3.metric("NO₂", "42.1 ppb")
m4.metric("Temp", "33.2 °C")
m5.metric("PM 2.5", "22.4")
m6.metric("Humidity", "64 %")

# Split Layout (Main & Sidebar Controls)
col_main, col_side = st.columns([2, 1])

with col_main:
    # แผนที่ (Map Layering แบบมาตรฐาน)
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("🗺️ Global/Regional Map")
    st.pydeck_chart(pdk.Deck(
        layers=[pdk.Layer("ScatterplotLayer", df, get_position="[lon, lat]", get_radius=50000, get_color=[0, 255, 255, 160])],
        initial_view_state=pdk.ViewState(latitude=13.0, longitude=101.0, zoom=5, pitch=0)
    ))
    st.markdown('</div>', unsafe_allow_html=True)
    
    # กราฟแนวโน้ม
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("📈 Trends Analysis")
    fig = px.line(df, x='Region', y='co2')
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="white")
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col_side:
    # แผงควบคุม (Filter Data ตามที่วางแผนไว้)
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("⚙️ Controls")
    metric = st.selectbox("เลือกสารมลพิษ", ["CO2", "CH4", "NO2", "Temp", "PM2.5", "Humidity"])
    region = st.selectbox("เลือกภูมิภาค", df['Region'].unique())
    st.markdown('</div>', unsafe_allow_html=True)
    
    # ตาราง
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("📋 Data Table")
    st.table(df[['Region', 'co2', 'ch4']])
    st.markdown('</div>', unsafe_allow_html=True)
