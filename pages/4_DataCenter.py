import streamlit as st
from utils.database import load_data

st.title("📁 ข้อมูลและดาวน์โหลด")

df = load_data()

if df.empty:

    st.warning("ไม่พบข้อมูล")

else:

    st.dataframe(
        df,
        use_container_width=True
    )

    csv = df.to_csv(index=False)

    st.download_button(
        "📥 ดาวน์โหลดข้อมูล",
        csv,
        "ghg_data.csv",
        "text/csv"
    )

st.markdown("---")

st.subheader("แหล่งข้อมูล")

st.success("ฐานข้อมูล GHG Dashboard")

st.markdown("---")

st.caption("""
ผู้จัดทำ

1.

2.



สถาบัน :




โลโก้ :
""")
