import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from datetime import datetime

# 1. SETUP
st.set_page_config(layout="wide", page_title="GHG Monitor Board")

# 2. ADVANCED CSS STYLING
st.markdown("""
    <style>
        /* ฟอนต์หลักและพื้นหลัง */
        @import url('https://fonts.googleapis.com/css2?family=Kanit:wght@300;400;500&display=swap');
        html, body, [class*="css"]  { font-family: 'Kanit', sans-serif; }
        
        .stApp { background-color: #0e1117; }

        /* ตกแต่งกรอบ Metric (ค่ามลพิษ) */
        [data-testid="stMetric"] { 
            background: linear-gradient(135deg, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0.01) 100%);
            padding: 25px !important; 
            border-radius: 20px !important; 
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
            transition: 0.3s;
        }
        [data-testid="stMetric"]:hover {
            border: 1px solid rgba(255, 255, 255, 0.3) !important;
            transform: translateY(-5px);
        }

        /* ปรับแต่ง Sidebar */
        [data-testid="stSidebar"] { background-color: #161b22 !important; border-right: 1px solid rgba(255,255,255,0.1); }
        
        /* จัดโครงสร้างเมนูและ Footer */
        [data-testid="stSidebarContent"] {
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            height: 100vh;
        }

        .menu-title {
            font-size: 24px;
            font-weight: 500;
            color: #ffffff;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #30363d;
        }

        /* กลุ่มโลโก้และเครดิตด้านล่าง (Signature Block) */
        .brand-container {
            background: rgba(255, 255, 255, 0.03);
            padding: 20px;
            border-radius: 15px;
            border: 1px solid rgba(255, 255, 255, 0.05);
            margin-bottom: 20px;
            text-align: left;
        }
        .brand-name {
            font-size: 18px;
            font-weight: 600;
            color: #ffffff;
            margin-top: 10px;
            letter-spacing: 1px;
        }
        .brand-sub {
            font-size: 11px;
            color: #8b949e;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
    </style>
""", unsafe_allow_html=True)

# 3. DATA FUNCTIONS
def get_latest_data():
    return {"CO₂ (ppm)": 433, "CH₄ (ppb)": 1865, "NO₂ (ppb)": 42.1, "PM 2.5": 22.4, "Temp (°C)": 33.2, "Humidity (%)": 64}

# 4. MAIN CONTENT
st.title("🌍 Tracking GHGs Emission")
st.markdown("---")

# Display Metrics
metrics = get_latest_data()
cols = st.columns(len(metrics))
for i, (label, val) in enumerate(metrics.items()):
    cols[i].metric(label, str(val))

# 5. SIDEBAR DESIGN
with st.sidebar:
    # ส่วนหัวเมนู
    st.markdown('<div class="menu-title">📋 เมนูควบคุมระบบ</div>', unsafe_allow_html=True)
    
    # ส่วนการตั้งค่า
    selected = st.selectbox("เลือกสารมลพิษที่ต้องการดู:", list(get_latest_data().keys()))
    mode = st.radio("เลือกช่วงเวลาแสดงผล:", ["รายวัน", "รายเดือน"], horizontal=True)
    
    # พื้นที่ว่างดัน Footer ลงล่าง
    st.container() 
    
    # กลุ่มโลโก้และเครดิต (Signature Block)
    st.markdown('<div class="brand-container">', unsafe_allow_html=True)
    st.image("https://comci.southeast.ac.th/2025/img/SBU.png", width=90)
    st.markdown("""
        <div class="brand-name">AE-IET [SBU]</div>
        <div class="brand-sub">Produced by Engineering Team</div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# 6. GRAPH (Dummy Data for visual)
dates = pd.date_range(end=datetime.now(), periods=30, freq='D')
vals = np.random.normal(400,
