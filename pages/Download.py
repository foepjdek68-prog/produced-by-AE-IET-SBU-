import streamlit as st
import pandas as pd

from Services.database import load_data, save_data
from Services.api_loader import fetch_data

# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(
    page_title="GHG Data Center",
    page_icon="📥",
    layout="wide"
)

# =====================================================
# SIDEBAR
# =====================================================

with st.sidebar:
    # 1. ส่วนเนื้อหาด้านบน (รูปโลโก้ + เมนู)
    st.image("Assets/logo.png", width=250)
    # ใส่เมนูอื่นๆ ของคุณตรงนี้...

    # 2. ส่วน Footer ที่จะบังคับให้อยู่ล่างสุด
    st.markdown("""
        <style>
            /* บังคับให้ Sidebar เป็น Flexbox */
            [data-testid="stSidebar"] > div:first-child {
                display: flex;
                flex-direction: column;
                height: 90vh; /* ความสูงเกือบเต็มหน้าจอ */
            }
            /* ส่วนนี้จะทำหน้าที่ดัน Footer ลงไปล่างสุด */
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
            (C) Dept. Engineering SBU
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
# CSS
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
# LOAD DATA
# =====================================================

df = load_data()

if df is None or df.empty:
    df = fetch_data()
    save_data(df)

# กัน Date error
if "Date" in df.columns:
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

df = df.dropna(subset=["Date"])

# =====================================================
# HANDLE EMPTY DATA
# =====================================================

if df.empty:
    latest_date = "No Data"
    date_range_text = "No Data Available"
else:
    latest_dt = df["Date"].max()
    date_range_text = f"{df['Date'].min().strftime('%d/%m/%Y')} - {df['Date'].max().strftime('%d/%m/%Y')}"
    latest_date = latest_dt.strftime("%d/%m/%Y %H:%M")

# =====================================================
# HEADER (FIXED)
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
        📊 Greenhouse Gas Monitoring Dashboard
    </h1>

    <p style="color:white;">
        Last Update : {latest_date}
    </p>
</div>
""")

# =====================================================
# KPI
# =====================================================

c1, c2, c3, c4 = st.columns(4)

c1.metric("Records", f"{len(df):,}")

c2.metric(
    "Latest CO₂",
    f"{df['CO2'].iloc[-1]:.2f}" if not df.empty else "No Data"
)

c3.metric(
    "Latest Temp",
    f"{df['Temp'].iloc[-1]:.2f} °C" if not df.empty else "No Data"
)

c4.metric(
    "Last Update",
    latest_date if isinstance(latest_date, str) else latest_date.strftime("%H:%M")
)

st.markdown("---")

# =====================================================
# RENAME COLUMNS
# =====================================================

rename_columns = {
    "CO2": "CO₂",
    "CH4": "CH₄",
    "NO2": "NO₂",
    "PM25": "PM 2.5",
    "Temp": "Temperature",
    "Humidity": "Humidity"
}

display_df = df.rename(columns=rename_columns)

# =====================================================
# COLUMN FILTER
# =====================================================

selected_column = st.selectbox(
    "เลือกข้อมูลที่ต้องการดู",
    ["ทั้งหมด", "CO₂", "CH₄", "NO₂", "PM 2.5", "Temperature", "Humidity"]
)

if selected_column != "ทั้งหมด":
    display_df = display_df[["Date", selected_column]]

# =====================================================
# QUICK STATS
# =====================================================

st.subheader("📊 Quick Statistics")

stats_df = display_df.copy()

if "Date" in stats_df.columns:
    stats_df = stats_df.drop(columns=["Date"])

if len(stats_df.columns) > 0:
    st.dataframe(stats_df.describe(), use_container_width=True)

# =====================================================
# TABLE
# =====================================================

st.subheader("📋 Data Preview")

st.dataframe(
    display_df,
    use_container_width=True,
    height=550
)

# =====================================================
# DOWNLOAD
# =====================================================

st.markdown("---")

col1, col2 = st.columns(2)

csv = display_df.to_csv(index=False)

with col1:
    st.download_button(
        label="📥 Download CSV",
        data=csv,
        file_name="GHG_Dashboard_Data.csv",
        mime="text/csv",
        use_container_width=True
    )

with col2:
    excel_data = display_df.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="📊 Export Excel Compatible",
        data=excel_data,
        file_name="GHG_Dashboard_Data.xls",
        mime="application/vnd.ms-excel",
        use_container_width=True
    )
