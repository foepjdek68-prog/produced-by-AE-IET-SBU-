import streamlit as st

from utils.database import load_data

st.title("📈 Analytics")

df = load_data()

if df.empty:
    st.warning("ไม่มีข้อมูล")
    st.stop()

c1, c2, c3 = st.columns(3)

c1.metric(
    "Average CO2",
    round(df["CO2"].mean(), 2)
)

c2.metric(
    "Maximum CO2",
    round(df["CO2"].max(), 2)
)

c3.metric(
    "Minimum CO2",
    round(df["CO2"].min(), 2)
)

st.divider()

st.subheader("Correlation Matrix")

st.dataframe(
    df.corr(numeric_only=True),
    use_container_width=True
)
