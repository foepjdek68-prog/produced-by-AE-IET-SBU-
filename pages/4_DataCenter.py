import streamlit as st
from utils.database import load_data

df = load_data()

st.write("Rows:", len(df))

if not df.empty:
    st.write(df.head())
else:
    st.warning("Database ว่าง")
