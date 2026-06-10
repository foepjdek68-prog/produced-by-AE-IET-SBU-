import streamlit as st
from utils.database import load_data

st.title("TEST")

df = load_data()

st.write(df.head())
st.write("Rows =", len(df))
