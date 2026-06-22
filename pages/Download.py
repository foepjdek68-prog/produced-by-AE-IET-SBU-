import streamlit as st
import pandas as pd

from Services.database import load_data, save_data
from Services.api_loader import fetch_data

# =====================================================
# PAGE CONFIG
# =====================================================
st.set_page_config(page_title="GHG Data Management Center", page_icon="🗄️", layout="wide")

# =====================================================
# GLOBAL CSS
# =====================================================
st.markdown("""
<style>
    .stApp { background: #030712; }
    section[data-testid="stSidebar"] { background: #1e293b !important; border-right: 1px solid #334155; }
    section[data-testid="stSidebar"] * { color: #e2e8f0 !important; }
    
    [data-testid="stMetric"] { 
        background: #0f172a !important; 
        border: 1px solid #60a5fa !important; 
        border-radius: 12px !important; 
        padding: 15px !important; 
    }
    
    /* สไตล์สำหรับ DataFrame/Table ให้เข้ากับธีมมืด */
    [data-testid="stDataFrame"] { border: 1px solid #334155; border-radius: 8px; }
    
    h1, h2, h3 { color: white !important; }
    .stSelectbox > div > div { background: #111827 !important; color: white !important; }
</style>
""", unsafe_allow_html=True)

# =====================================================
# SIDEBAR
# =====================================================
with st.sidebar:
    st.markdown('<div style="background:rgba(255,255,255,0.05); padding:15px; border-radius:10px; margin-bottom:20px; text-align:center;">', unsafe_allow_html=True)
    st.image("Assets/logo.png", width=250)
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("""
        <div class="sidebar-footer" style="border-top:1px solid #4B5563; padding-top:10px; margin-top:20px; font-size:0.75em; color:#9CA3AF;">
        (C) Dept. Engineering SBU
        </div>
    """, unsafe_allow_html=True)

# =====================================================
# LOAD DATA
# =====================================================
df = load_data()
if df is None or df.empty:
    df = fetch_data()
    if df is not None and not df.empty:
        save_data(df)

if df is not None and "Date" in df.columns:
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df = df.dropna(subset=["Date"])

latest_str = df["Date"].max().strftime("%d/%m/%Y %H:%M") if not df.empty else "ไม่มีข้อมูล"

# =====================================================
# HEADER
# =====================================================
st.markdown(f"""
<div style="background:linear-gradient(135deg,#0f172a,#1e293b); padding:25px; border-radius:12px; border:1px solid #334155; margin-bottom:20px;">
    <h1 style="margin:0;">🗄️ GHG Data Management Center</h1>
    <p style="color:#cbd5e1;">อัปเดตล่าสุด : {latest_str}</p>
</div>
""", unsafe_allow_html=True)

# =====================================================
# KPI METRICS
# =====================================================
c1, c2, c3, c4 = st.columns(4)
is_data_available = df is not None and not df.empty
last_row = df.iloc[-1] if is_data_available else None

c1.metric("รายการทั้งหมด", f"{len(df):,}" if is_data_available else "0")
c2.metric("CO₂ ล่าสุด", f"{last_row['CO2']:.2f}" if is_data_available and 'CO2' in df.columns else "N/A")
c3.metric("อุณหภูมิล่าสุด", f"{last_row['Temp']:.2f} °C" if is_data_available and 'Temp' in df.columns else "N/A")
c4.metric("สถานะ", "🟢 ปกติ" if is_data_available else "🔴 ไม่มีข้อมูล")

st.markdown("---")

# =====================================================
# CONTENT
# =====================================================
rename_map = {"CO2": "CO₂", "CH4": "CH₄", "NO2": "NO₂", "PM25": "PM 2.5", "Temp": "อุณหภูมิ (°C)", "Humidity": "ความชื้น (%)"}
display_df = df.rename(columns=rename_map) if not df.empty else pd.DataFrame()
selected_column = st.selectbox("เลือกประเภทข้อมูลที่ต้องการโฟกัส", ["ทั้งหมด"] + list(rename_map.values()))

working_df = display_df[["Date", selected_column]] if selected_column != "ทั้งหมด" else display_df

tab1, tab2 = st.tabs(["📊 สถิติเบื้องต้น", "📋 ข้อมูลรายละเอียด"])

with tab1:
    if not working_df.empty:
        st.dataframe(working_df.drop(columns=["Date"], errors="ignore").describe(), use_container_width=True)
with tab2:
    if not working_df.empty:
        st.dataframe(working_df.sort_values(by="Date", ascending=False), use_container_width=True, height=550)

# =====================================================
# DOWNLOAD
# =====================================================
if not working_df.empty:
    csv = working_df.to_csv(index=False).encode('utf-8-sig')
    st.download_button("📥 ดาวน์โหลดข้อมูล (CSV)", csv, "GHG_Data.csv", "text/csv", use_container_width=True)
