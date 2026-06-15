import streamlit as st

from Services.database import load_data, save_data
from Services.api_loader import fetch_data


# =========================
# PAGE
# =========================
st.title("📥 Download Data")


# =========================
# LOAD DATA
# =========================
df = load_data()

if df.empty:
    df = fetch_data()
    save_data(df)


# =========================
# RENAME COLUMNS
# =========================
rename_columns = {
    "CO2": "CO₂",
    "CH4": "CO₄",
    "NO2": "NO₂",
    "PM25": "PM 2.5",
    "Temp": "Temperature",
    "Humidity": "Humidity"
}

display_df = df.rename(columns=rename_columns)


# =========================
# DISPLAY TABLE
# =========================
st.dataframe(
    display_df,
    use_container_width=True
)


# =========================
# DOWNLOAD CSV
# =========================
csv = display_df.to_csv(index=False)

st.download_button(
    label="📥 ดาวน์โหลดข้อมูล",
    data=csv,
    file_name="GHG_Dashboard_Data.csv",
    mime="text/csv"
)
