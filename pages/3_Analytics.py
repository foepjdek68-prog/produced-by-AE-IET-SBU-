import streamlit as st
from utils.database import load_data

df = load_data()

st.title("📊 Analytics")

st.metric("Avg CO2", df["CO2"].mean())
st.metric("Max CO2", df["CO2"].max())
st.metric("Min CO2", df["CO2"].min())
