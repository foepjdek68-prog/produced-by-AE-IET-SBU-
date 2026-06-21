import streamlit as st
import pandas as pd

from Services.database import load_data, save_data
from Services.api_loader import fetch_data

# =====================================================
# การตั้งค่าหน้าจอ
# =====================================================
st.set_page_config(page_title="GHG Data Center", page_icon="🗄️", layout="wide")

# =====================================================
# แถบเมนูด้านข้าง
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

# =====================================================
# การโหลดข้อมูล
# =====================================================
df = load_data()
if df is None or df.empty:
    df = fetch_data()
    if df is not None and not df.empty:
        save_data(df)

if df is not None and "Date" in df.columns:
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df = df.dropna(subset=["Date"])

# =====================================================
# ส่วนหัวของหน้าจอ
# =====================================================
latest_str = df["Date"].max().strftime("%d/%m/%Y %H:%M") if not df.empty else "ไม่มีข้อมูล"

st.markdown(f"""
<div style="background:linear-gradient(135deg,#111827,#1F2937); padding:25px; border-radius:20px; border:1px solid #374151; margin-bottom:20px;">
    <h1 style="margin:0;color:white;">🗄️ GHG Data Management Center</h1>
    <p style="color:white;">อัปเดตล่าสุด : {latest_str}</p>
</div>
""", unsafe_allow_html=True)

# =====================================================
# สรุปข้อมูลสำคัญ (KPI Metrics)
# =====================================================
c1, c2, c3, c4 = st.columns(4)
is_data_available = df is not None and not df.empty

c1.metric("จำนวนรายการทั้งหมด", f"{len(df):,}" if is_data_available else "0")

last_row = df.iloc[-1] if is_data_available else None
c2.metric("ค่า CO₂ ล่าสุด", f"{last_row['CO2']:.2f}" if is_data_available and 'CO2' in df.columns else "N/A")
c3.metric("อุณหภูมิล่าสุด", f"{last_row['Temp']:.2f} °C" if is_data_available and 'Temp' in df.columns else "N/A")
c4.metric("เวลาอัปเดตล่าสุด", latest_str)

st.markdown("---")

# =====================================================
# การปรับแต่งและตัวกรอง
# =====================================================
rename_map = {
    "CO2": "CO₂", "CH4": "CH₄", "NO2": "NO₂", 
    "PM25": "PM 2.5", "Temp": "อุณหภูมิ (°C)", "Humidity": "ความชื้น (%)"
}
display_df = df.rename(columns=rename_map) if not df.empty else pd.DataFrame()

selected_column = st.selectbox("เลือกประเภทข้อมูลที่ต้องการโฟกัส", ["ทั้งหมด"] + list(rename_map.values()))

if selected_column != "ทั้งหมด" and selected_column in display_df.columns:
    working_df = display_df[["Date", selected_column]]
else:
    working_df = display_df

# =====================================================
# ส่วนแสดงผล
# =====================================================
tab1, tab2 = st.tabs(["📊 สถิติเบื้องต้น", "📋 ข้อมูลล่าสุด"])

with tab1:
    st.subheader("📊 สถิติเชิงปริมาณ")
    if not working_df.empty:
        st.dataframe(working_df.drop(columns=["Date"], errors="ignore").describe(), use_container_width=True)
    else:
        st.info("ไม่มีข้อมูล")

with tab2:
    st.subheader("📋 ข้อมูลรายละเอียดล่าสุด")
    if not working_df.empty:
        st.dataframe(working_df.sort_values(by="Date", ascending=False), use_container_width=True, height=550)
    else:
        st.info("ไม่มีข้อมูล")

# =====================================================
# การดาวน์โหลด
# =====================================================
st.markdown("---")
if not working_df.empty:
    csv = working_df.to_csv(index=False).encode('utf-8-sig')
    col1, col2 = st.columns(2)
    col1.download_button("📥 ดาวน์โหลดไฟล์ CSV", csv, "GHG_Data.csv", "text/csv", use_container_width=True)
    col2.download_button("📊 ดาวน์โหลดไฟล์สำหรับ Excel", csv, "GHG_Data.csv", "text/csv", use_container_width=True)
