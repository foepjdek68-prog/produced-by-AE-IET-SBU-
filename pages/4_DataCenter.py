import streamlit as st
from utils.database import load_data

st.title("📁 Data Repository")

df = load_data()

if df.empty:

    st.warning("No Data Available")

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

st.markdown("---")

st.caption("""
Developed By

1.

2.



Institution :



Logo :
""")
