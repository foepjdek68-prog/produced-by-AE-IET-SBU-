import streamlit as st

from utils.database import (
    load_data,
    save_data
)

from utils.api_loader import fetch_data

df = load_data()

if df.empty:

    st.warning("Database ว่าง กำลังสร้างข้อมูล...")

    df = fetch_data()

    save_data(df)

    st.success(f"สร้างข้อมูลแล้ว {len(df)} rows")

st.write("Rows:", len(df))

st.dataframe(df.head())
