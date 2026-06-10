import streamlit as st
from utils.database import load_data

st.title("🗄️ Data Center")

df = load_data()

if df.empty:

    st.warning("No data")

else:

    st.dataframe(
        df,
        use_container_width=True
    )

    csv = df.to_csv(index=False)

    st.download_button(
        "📥 Download CSV",
        csv,
        "ghg_data.csv",
        "text/csv"
    )
