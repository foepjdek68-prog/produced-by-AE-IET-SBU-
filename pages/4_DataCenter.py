import streamlit as st
from utils.database import load_data

st.title("📂 ศูนย์ข้อมูล")

df = load_data()

if df.empty:

    st.warning("ไม่พบข้อมูล")

else:

    st.metric(
        "จำนวนข้อมูลทั้งหมด",
        len(df)
    )

    st.dataframe(
        df,
        use_container_width=True
    )

    csv = df.to_csv(index=False)

    st.download_button(
        "📥 ดาวน์โหลดข้อมูล CSV",
        csv,
        "ghg_data.csv",
        "text/csv"
    )

st.markdown("---")

st.caption("""
ผู้จัดทำ

ชื่อสมาชิก 1
ชื่อสมาชิก 2
ชื่อสมาชิก 3
""")
