import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from datetime import datetime

# 1. SETUP
st.set_page_config(layout="wide", page_title="GHG Monitor Board")

# 2. CSS STYLING (หัวใจสำคัญของความสวยงาม)
st.markdown("""
    <style>
        /* จัดกรอบ Metric ให้สวยงาม */
        [data-testid="stMetric"] { 
            background: rgba(255, 255, 255, 0.05); 
            padding: 20px; 
            border-radius: 15px; 
            border: 1px solid rgba(255, 255, 255, 0.1);
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        }
        
        /* จัด Sidebar ให้ตรึงล่าง */
        [data-testid="stSidebarContent"] { 
            display: flex; flex-direction: column; height: 100vh; 
        }
        .footer-group { 
            margin-top: auto; padding: 20px; display: flex; flex-direction: column; gap: 5px;
            background: rgba(0,0,0,0.2); border-radius: 10px;
        }
        
        /* เปลี่ยนสีพื้นหลังหลัก */
        .stApp { background-color: #0e1117; }
    </style>
""", unsafe_allow_html=True)

# 3. DATA FUNCTIONS
def get_latest_data():
    return {"CO₂ (ppm)": 433, "CH₄ (ppb)": 1865, "NO₂ (ppb)": 42.1, "PM 2.5": 22.4, "Temp (°C)": 33.2, "Humidity (%)": 64}

# 4. MAIN LAYOUT
st.title("📊 Tracking GHGs Emission")

metrics = get_latest_data()
cols = st.columns(len(metrics))
for i, (label, val) in enumerate(metrics.items()):
    cols[i].metric(label, str(val))

# SIDEBAR (LOGO & CREDIT)
with st.sidebar:
    st.header("⚙️ Configuration")
    selected = st.selectbox("เลือกสารมลพิษ", ["CO₂ (ppm)", "CH₄ (ppb)", "NO₂ (ppb)", "PM 2.5", "Temp (°C)", "Humidity (%)"])
    mode = st.radio("รูปแบบการแสดงผล:", ["รายวัน", "รายเดือน"], horizontal=True)
    
    st.markdown('<div class="footer-group">', unsafe_allow_html=True)
    # ใส่โลโก้ (ใช้ URL ตรง เพื่อให้ไม่บั๊กเวลาคนอื่นเปิด)
    st.image("https://comci.southeast.ac.th/2025/img/SBU.png", width=120)
    st.markdown("""
        <div style="font-size: 16px; font-weight: bold; margin-top: 5px;">AE-IET [SBU]</div>
        <div style="font-size: 11px; color: #aaa;">produced by Engineering</div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# GRAPH
dates = pd.date_range(end=datetime.now(), periods=30, freq='D')
vals = np.random.normal(400, 10, 30)
df = pd.DataFrame({'Date': dates, 'Value': vals})

fig = px.line(df, x='Date', y='Value', template="plotly_dark")
fig.update_layout(
    paper_bgcolor="rgba(0,0,0,0)", 
    plot_bgcolor="rgba(0,0,0,0)",
    margin=dict(t=50, b=0, l=0, r=0)
)
st.plotly_chart(fig, use_container_width=True)
