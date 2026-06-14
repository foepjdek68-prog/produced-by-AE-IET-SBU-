import streamlit as st

from Services.database import load_data, save_data
from Services.api_loader import fetch_data


# =========================
# PAGE
# =========================

st.title("📥 Download")


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
    "CH4": "CH₄",
    "NO2": "NO₂",
    "PM25": "PM₂.₅",
    "Temp": "Temp",
    "Humidity": "RH"

}

display_df = df.rename(
    columns=rename_columns
)


# =========================
# TABLE STYLE
# =========================

def color_columns(col):

    colors = {

        "CO₂": "border:2px solid #DC2626;",
        "CH₄": "border:2px solid #F97316;",
        "NO₂": "border:2px solid #7C3AED;",
        "PM₂.₅": "border:2px solid #EAB308;",
        "Temp": "border:2px solid #22C55E;",
        "RH": "border:2px solid #2563EB;"

    }

    return [colors.get(col.name, "")] * len(col)


# =========================
# DISPLAY
# =========================

st.dataframe(
    display_df.style.apply(
        color_columns,
        axis=0
    ),
    use_container_width=True
)


# =========================
# DOWNLOAD
# =========================

csv = display_df.to_csv(
    index=False
)


st.download_button(
    "📥 ดาวน์โหลดข้อมูล",
    csv,
    "ghg_data.csv",
    "text/csv"
)
