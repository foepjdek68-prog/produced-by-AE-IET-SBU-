import streamlit as st

from utils.database import load_data

df = load_data()

st.title("🗄️ Data Center")

st.dataframe(
    df,
    use_container_width=True
)

csv = df.to_csv(index=False)

st.download_button(
    "Download CSV",
    csv,
    "ghg_data.csv"
)
