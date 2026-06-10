import streamlit as st

from utils.database import load_data

df = load_data()

st.title("📈 Analytics")

if not df.empty:

    st.subheader("Correlation")

    st.dataframe(
        df.corr(
            numeric_only=True
        )
    )
