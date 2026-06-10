import streamlit as st
from utils.database import load_data

df = load_data()

st.title("📁 Data Center")

st.dataframe(df)

st.download_button(
    "Download CSV",
    df.to_csv(index=False),
    "data.csv"
)
