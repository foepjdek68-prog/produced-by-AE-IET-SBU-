import streamlit as st

from Services.database import load_data



st.title("📥 Download")



df = load_data()



if df.empty:

    st.warning(
        "ไม่พบข้อมูล"
    )


else:

    st.dataframe(
        df,
        use_container_width=True
    )


    csv = df.to_csv(
        index=False
    )


    st.download_button(
        "📥 ดาวน์โหลดข้อมูล",
        csv,
        "ghg_data.csv",
        "text/csv"
    )
