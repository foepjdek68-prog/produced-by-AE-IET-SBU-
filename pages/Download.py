import streamlit as st
import pandas as pd

from Services.database import load_data, save_data
from Services.api_loader import fetch_data

# =====================================================
# Page Configuration
# =====================================================
st.set_page_config(
    page_title="GHG Engineering Data Center",
    page_icon="📊",
    layout="wide"
)

# =====================================================
# Sidebar
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
# Data Loading & Preparation
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
# Header
# =====================================================
st.markdown(
    f"""
    <div style="
        background:linear-gradient(135deg,#111827,#1F2937); 
        padding: 25px; 
        border-radius: 15px; 
        border: 1px solid #374151; 
        margin-bottom: 25px;
    ">
        <h1 style="margin:0; color:white; font-size: 2.2rem; font-weight: 800;">
            🌍 GHG Engineering Data Center
        </h1>
        <p style="color:#9CA3AF; margin-top:10px; font-size: 1.1rem;">
            Data Management & Export Portal | Last Updated: {latest_str}
        </p>
    </div>
    """, 
    unsafe_allow_html=True
)

# =====================================================
# KPI Overview
# =====================================================
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Records", f"{len(df):,}")
c2.metric("Latest CO₂", f"{df['CO2'].iloc[-1]:.2f}" if 'CO2' in df.columns else "N/A")
c3.metric("Latest Temp", f"{df['Temp'].iloc[-1]:.2f} °C" if 'Temp' in df.columns else "N/A")
c4.metric("Status", "Active")

st.markdown("---")

# =====================================================
# Filter & Data View
# =====================================================
rename_map = {
    "CO2": "CO₂ (ppm)", "CH4": "CH₄ (ppm)", "NO2": "NO₂ (ppb)", 
    "PM25": "PM 2.5 (µg/m³)", "Temp": "Temperature (°C)", "Humidity": "Humidity (%)"
}
display_df = df.rename(columns=rename_map)

selected_col = st.selectbox("Select Parameter to Inspect", ["All Data"] + list(rename_map.values()))
filtered_df = display_df[["Date", selected_col]] if selected_col != "All Data" else display_df

st.subheader("📋 Data Preview")
st.dataframe(filtered_df, use_container_width=True, height=450)

# =====================================================
# Export Section
# =====================================================
st.markdown("---")
st.subheader("📥 Data Export")
col1, col2 = st.columns(2)

csv = filtered_df.to_csv(index=False).encode('utf-8')
with col1:
    st.download_button("Download CSV", csv, "GHG_Data.csv", "text/csv", use_container_width=True)
with col2:
    st.download_button("Download for Excel", csv, "GHG_Data.csv", "text/csv", use_container_width=True)
