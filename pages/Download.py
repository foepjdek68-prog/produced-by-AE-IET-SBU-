import streamlit as st
import pandas as pd

from Services.database import load_data, save_data
from Services.api_loader import fetch_data

# =====================================================
# การตั้งค่าหน้าจอ (Page Configuration)
# =====================================================

st.set_page_config(
    page_title="GHG Data Center",
    page_icon="📥",
    layout="wide"
)

# =====================================================
# แถบเมนูด้านข้าง (Sidebar)
# =====================================================

with st.sidebar:
    # 1. โลโก้และเมนูหลัก
    st.image("Assets/logo.png", width=250)
    
    # 2. ส่วนท้ายของ Sidebar (Footer)
    st.markdown("""
        <style>
            /* บังคับให้ Sidebar เป็น Flexbox เพื่อจัดวาง Footer */
            [data-testid="stSidebar"] > div:first-child {
                display: flex;
                flex-direction: column;
                height: 90vh;
            }
            .sidebar-spacer {
                flex-grow: 1;
            }
            .sidebar-footer {
                border-top: 1px solid #4B5563;
                padding-top: 10px;
                margin-top: auto;
                font-size: 0.75em;
                color: #9CA3AF;
            }
        </style>
        
        <div class="sidebar-spacer"></div>
        <div class="sidebar-footer">
            (C) แผนกวิศวกรรม SBU
        </div>
    """, unsafe_allow_html=True)

st.markdown("""
<style>
[data-testid="stSidebar"] img{
    pointer-events: none;
    cursor: default;
}
</style>
""", unsafe_allow_html=True)

# =====================================================
# การตั้งค่าสไตล์ CSS (Custom Styles)
# =====================================================

st.markdown("""
<style>
.block-container{
    padding-top:1rem;
}
[data-testid="stMetric"]{
    background:#111827;
    border:1px solid #374151;
    border-radius:16px;
    padding:15px;
    text-align:center;
}
[data-testid="stMetricValue"]{
    font-size:26px;
    font-weight:700;
}
</style>
""", unsafe_allow_html=True)

# =====================================================
# การโหลดข้อมูล (Data Loading)
# =====================================================

df = load_data()

if df is None or df.empty:
    df = fetch_data()
    save_data(df)

# จัดรูปแบบวันที่
if "Date" in df.columns:
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

df = df.dropna(subset=["Date"])

# =====================================================
# การจัดการกรณีไม่มีข้อมูล
# =====================================================

if df.empty:
    latest_date = "ไม่มีข้อมูล"
    date_range_text = "ไม่พบข้อมูลในระบบ"
else:
    latest_dt = df["Date"].max()
    date_range_text = f"{df['Date'].min().strftime('%d/%m/%Y')} - {df['Date'].max().strftime('%d/%m/%Y')}"
    latest_date = latest_dt.strftime("%d/%m/%Y %H:%M")

# =====================================================
# ส่วนหัวของหน้าจอ (Header)
# =====================================================

st.html(f"""
<div style="
    background:linear-gradient(135deg,#111827,#1F2937);
    padding:25px;
    border-radius:20px;
    border:1px solid #374151;
    margin-bottom:20px;
">
    <h1 style="margin:0;color:white;">
        📊 Dashboard Tracking Greenhouse Gases Emission
    </h1>
    <p style="color:white;">
        อัปเดตล่าสุด : {latest_date}
    </p>
</div>
""")

# =====================================================
# สรุปข้อมูลสำคัญ (KPI Metrics)
# =====================================================

c1, c2, c3, c4 = st.columns(4)

c1.metric("จำนวนรายการทั้งหมด", f"{len(df):,}")

c2.metric(
    "ค่า CO₂ ล่าสุด",
    f"{df['CO2'].iloc[-1]:.2f}" if not df.empty else "ไม่มีข้อมูล"
)

c3.metric(
    "อุณหภูมิล่าสุด",
    f"{df['Temp'].iloc[-1]:.2f} °C" if not df.empty else "ไม่มีข้อมูล"
)

c4.metric(
    "เวลาอัปเดตล่าสุด",
    latest_date if isinstance(latest_date, str) else latest_date.split(" ")[1]
)

st.markdown("---")

# =====================================================
# การปรับแต่งหัวคอลัมน์เพื่อแสดงผล
# =====================================================

rename_columns = {
    "CO2": "CO₂",
    "CH4": "CH₄",
    "NO2": "NO₂",
    "PM25": "PM 2.5",
    "Temp": "อุณหภูมิ (°C)",
    "Humidity": "ความชื้น (%)"
}

display_df = df.rename(columns=rename_columns)

# =====================================================
# ตัวกรองข้อมูล (Filter)
# =====================================================

selected_column = st.selectbox(
    "เลือกประเภทข้อมูลที่ต้องการดู",
    ["ทั้งหมด", "CO₂", "CH₄", "NO₂", "PM 2.5", "อุณหภูมิ (°C)", "ความชื้น (%)"]
)

if selected_column != "ทั้งหมด":
    display_df = display_df[["Date", selected_column]]

# =====================================================
# สถิติเบื้องต้น (Quick Statistics)
# =====================================================

st.subheader("📊 สถิติเบื้องต้นของข้อมูล")

stats_df = display_df.copy()

if "Date" in stats_df.columns:
    stats_df = stats_df.drop(columns=["Date"])

if len(stats_df.columns) > 0:
    st.dataframe(stats_df.describe(), use_container_width=True)

# =====================================================
# ตารางแสดงข้อมูลดิบ (Data Preview)
# =====================================================

st.subheader("📋 ตัวอย่างข้อมูลล่าสุด")

st.dataframe(
    display_df,
    use_container_width=True,
    height=550
)

# =====================================================
# การดาวน์โหลดข้อมูล (Download Section)
# =====================================================

st.markdown("---")

col1, col2 = st.columns(2)

csv = display_df.to_csv(index=False)

with col1:
    st.download_button(
        label="📥 ดาวน์โหลดไฟล์ CSV",
        data=csv,
        file_name="GHG_Dashboard_Data.csv",
        mime="text/csv",
        use_container_width=True
    )

with col2:
    excel_data = display_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📊 ดาวน์โหลดไฟล์สำหรับ Excel",
        data=excel_data,
        file_name="GHG_Dashboard_Data.csv",
        mime="application/vnd.ms-excel",
        use_container_width=True
    )
