import streamlit as st
from utils.database import load_data

st.title("🗄️ Data Center")

# --------------------------
# Project Objective
# --------------------------

st.subheader("📌 Project Objective")

st.info("""
พัฒนา Web Dashboard เพื่อรวบรวมและเชื่อมโยงข้อมูลสิ่งแวดล้อม
จากหลายแหล่งข้อมูลมาไว้ในระบบเดียว

ช่วยให้สามารถติดตาม วิเคราะห์ และเฝ้าระวัง
สถานการณ์ด้านสิ่งแวดล้อมได้อย่างมีประสิทธิภาพ
""")

st.markdown("---")

# --------------------------
# Data Sources
# --------------------------

st.subheader("🔗 Data Sources")

col1,col2 = st.columns(2)

with col1:
    st.success("Air4Thai")
    st.success("TMD")

with col2:
    st.warning("OpenAQ (Planned)")
    st.warning("Sentinel-5P (Planned)")

st.markdown("---")

# --------------------------
# Team
# --------------------------

st.subheader("👨‍💻 Team Members")

st.write("""
• Member 1

• Member 2

• Member 3
""")

st.markdown("---")

# --------------------------
# Raw Data
# --------------------------

st.subheader("📊 Raw Data")

df = load_data()

if df.empty:

    st.warning("No Data")

else:

    st.write(f"Total Records : {len(df)}")

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
