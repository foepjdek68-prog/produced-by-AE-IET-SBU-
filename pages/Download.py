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
# DISPLAY
# =========================

st.dataframe(
    df,
    use_container_width=True
)



# =========================
# DOWNLOAD
# =========================

csv = df.to_csv(
    index=False
)


st.download_button(
    "📥 ดาวน์โหลดข้อมูล",
    csv,
    "ghg_data.csv",
    "text/csv"
)
