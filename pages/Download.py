import streamlit as st
import pandas as pd

from Services.database import load_data, save_data
from Services.api_loader import fetch_data

# =====================================================
# การตั้งค่าหน้าจอ (Page Configuration)
# =====================================================
st.set_page_config(
    page_title="GHG Data Center",
    page_icon="🗄️",
    layout="wide"
)

# =====================================================
# แถบเมนูด้านข้าง (Sidebar)
# =====================================================
with st.sidebar:
    st.image("Assets/logo.png", width=250)
    
    st.markdown("""
        <style>
            [data-testid="stSidebar"] > div:first-child { display: flex; flex-direction: column; height: 90vh; }
            .sidebar-spacer { flex-grow: 1; }
            .sidebar-footer { border-top: 1px solid #4B5563; padding-top: 10px; margin-top: auto; font-size: 0.75em; color: #9CA3AF; }
        </style>
        <div class="sidebar-spacer"></div>
        <div class="sidebar-footer">(C) Dept. Engineering SBU</div>
    """, unsafe_allow_html=True)

st.markdown("<style>[data-testid='stSidebar'] img{ pointer-events: none; cursor: default; }</style>", unsafe_allow_html=True)

# =====================================================
# การตั้งค่าสไตล์ CSS
# =====================================================
st.markdown("""
<style>
.block-container { padding-top: 1rem; }
[data-testid="stMetric"] { background: #111827; border: 1px solid #374151; border-radius: 16px; padding: 15px; text-align: center; }
[data-testid="stMetricValue"] { font-size: 26px; font-weight: 700; }
</style>
""", unsafe_allow_html=True)

# =====================================================
# การโหลดข้อมูล (Data Loading)
# =====================================================
df = load_data()
if df is None or df.empty:
    df = fetch_data()
    save_data(df)

if "Date" in df.columns:
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df = df.dropna(subset=["Date"])

# =====================================================
# ส่วนหัวของหน้าจอ (Header)
# =====================================================
latest_str = "ไม่มีข้อมูล"
if not df.empty:
    latest_dt = df["Date"].max()
    latest_str = latest_dt.strftime("%d/%m/%Y %H:%M")

st.html(f"""
<div style="background:linear-gradient(135deg,#111827,#1F2937); padding:25px; border-radius:20px; border:1px solid #374151; margin-bottom:20px;">
    <h1 style="margin:0;color:white;">🗄️ GHG Data Management Center</h1>
    <p style="color:white;">อัปเดตล่าสุด : {latest_str}</p>
</div>
""")

# =====================================================
# สรุปข้อมูลสำคัญ (KPI Metrics)
# =====================================================
c1, c2, c3, c4 = st.columns(4)
is_data_available = not df.empty

c1.metric("จำนวนรายการทั้งหมด", f"{len(df):,}")
c2.metric("ค่า CO₂ ล่าสุด", f"{df['CO2'].iloc[-1]:.2f}" if (is_data_available and 'CO2' in df.columns) else "N/A")
c3.metric("อุณหภูมิล่าสุด", f"{df['Temp'].iloc[-1]:.2f} °C" if (is_data_available and 'Temp' in df.columns) else "N/A")
c4.metric("เวลาอัปเดตล่าสุด", latest_str)

st.markdown("---")

# =====================================================
# การปรับแต่งหัวคอลัมน์และตัวกรอง
# =====================================================
rename_map = {
    "CO2": "CO₂", "CH4": "CH₄", "NO2": "NO₂", 
    "PM25": "PM 2.5", "Temp": "อุณหภูมิ (°C)", "Humidity": "ความชื้น (%)"
}
display_df = df.rename(columns=rename_map)

# ตัวกรองข้อมูล (ไว้ด้านบนเพื่อให้ผลลัพธ์ในทุก Tab เปลี่ยนตาม)
selected_column = st.selectbox("เลือกประเภทข้อมูลที่ต้องการโฟกัส", ["ทั้งหมด"] + list(rename_map.values()))

if selected_column != "ทั้งหมด" and selected_column in display_df.columns:
    working_df = display_df[["Date", selected_column]]
else:
    working_df = display_df

# =====================================================
# ฟังก์ชันแสดงผลส่วนต่างๆ
# =====================================================
def show_statistics(data):
    st.subheader("📊 สถิติเชิงปริมาณ")
    stats_df = data.drop(columns=["Date"], errors="ignore")
    if not stats_df.empty:
        st.dataframe(stats_df.describe(), use_container_width=True)
    else:
        st.info("ไม่มีข้อมูลสำหรับคำนวณสถิติ")

def show_raw_data(data):
    st.subheader("📋 ข้อมูลรายละเอียดล่าสุด")
    # เรียงลำดับจากล่าสุดไปเก่า
    st.dataframe(data.sort_values(by="Date", ascending=False), use_container_width=True, height=550)

# =====================================================
# แสดง Tabs
# =====================================================
tab1, tab2 = st.tabs(["📊 สถิติเบื้องต้น", "📋 ข้อมูลล่าสุด"])

with tab1:
    show_statistics(working_df)

with tab2:
    show_raw_data(working_df)

# =====================================================
# การดาวน์โหลดข้อมูล
# =====================================================
st.markdown("---")
csv = working_df.to_csv(index=False)
col1, col2 = st.columns(2)

with col1:
    st.download_button("📥 ดาวน์โหลดไฟล์ CSV", csv, "GHG_Data.csv", "text/csv", use_container_width=True)

with col2:
    st.download_button("📊 ดาวน์โหลดไฟล์สำหรับ Excel", csv, "GHG_Data.csv", "text/csv", use_container_width=True)
