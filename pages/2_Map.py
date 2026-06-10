import streamlit as st
import pandas as pd

st.title("🗺️ Map")

map_df = pd.DataFrame({
    "lat":[13.7, 18.8, 7.9],
    "lon":[100.5, 98.9, 98.4],
    "city":["Bangkok","Chiang Mai","Phuket"]
})

st.map(map_df)
