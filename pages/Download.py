import streamlit as st
import pandas as pd

from Services.database import load_data, save_data
from Services.api_loader import fetch_data

# =====================================================
# Page Configuration
# =====================================================
st.set_page_config(
    page_title="GHG Engineering Data Center",
    page_icon="⚙️", # เปลี่ยนเป็นรูปเฟืองที่สื่อถึงงานวิศวกรรม
    layout="wide"
)

# =====================================================
# Sidebar
# =====================================================
with st.sidebar:
    st.image("Assets/logo.png", width=250)
    st.markdown("---")
    st.write("🔧 **Engineering Tools**")
    st.markdown("""
        <style>
            .sidebar-footer { border-top: 1px solid #4B5563; padding-top: 10px; margin-top: 20px; font-size: 0.8em; color: #9CA3AF; }
        </style>
        <div class="sidebar-footer">(C) Dept. Engineering SBU</div>
    """, unsafe_allow_html=True)

# =====================================================
# Data Loading
# =====================================================
df = load_data()
if df is None or df.empty:
    df = fetch_data()
    save_data(df)

if "Date" in df.columns:
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df = df.dropna(subset=["Date"])

latest_str = df["Date"].max().strftime("%d/%m/%Y %H:%M") if not df.empty else "No Data"

# =====================================================
# Header (Custom Engineering Style)
# =====================================================
st.markdown(
    f"""
    <div style="
        border-left: 5px solid #3B82F6; 
        padding-left: 20px; 
        margin-bottom: 30px;
    ">
        <h2 style="margin:0; color: #E5E7EB;">GHG Engineering Data Center</h2>
        <p style="color: #6B7280; font-family: monospace;">SYSTEM_STATUS: ONLINE | LAST_SYNC: {latest_str}</p>
    </div>
    """, 
    unsafe_allow_html=True
)

# =====================================================
# Data Management Panel
# =====================================================
col_a, col_b = st.columns([1, 3])

with col_a:
    st.subheader("⚙️ Parameter Control")
    rename_map = {
        "CO2": "CO₂ (ppm)", "CH4": "CH₄ (ppm)", "NO2": "NO₂ (ppb)", 
        "PM25": "PM 2.5 (µg/m³)", "Temp": "Temp (°C)", "Humidity": "Humidity (%)"
    }
    display_df = df.rename(columns=rename_map)
    
    selected_param = st.selectbox("Select Parameter", ["All Parameters"] + list(rename_map.values()))
    
    # ส่วนแสดงข้อมูลสรุปขนาดเล็ก
    st.info(f"Total Entries: **{len(df):,}**")
    
    # Export Section
    st.markdown("---")
    st.write("💾 **Data Export**")
    filtered_df = display_df[["Date", selected_param]] if selected_param != "All Parameters" else display_df
    csv = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button("Export as CSV", csv, "Engineering_Data.csv", "text/csv", use_container_width=True)

with col_b:
    st.subheader("📋 Raw Data Records")
    st.dataframe(
        filtered_df.sort_values("Date", ascending=False), 
        use_container_width=True, 
        height=500
    )
