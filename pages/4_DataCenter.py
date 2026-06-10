import streamlit as st
from utils.database import load_data

st.title("🗄️ Data Center")

# -------------------
# Project Info
# -------------------

st.subheader("📌 Project Information")

st.info("""
Dashboard Tracking Greenhouse Gases Emission

ระบบรายงานและติดตามก๊าซเรือนกระจกอัจฉริยะ

พัฒนาเพื่อรวบรวมและเชื่อมโยงข้อมูลมลพิษ
จากหลายแหล่งข้อมูลมาไว้ในระบบเดียว
""")

# -------------------
# Data Sources
# -------------------

st.subheader("🔗 Data Sources")

col1,col2 = st.columns(2)

with col1:

    st.success("Air4Thai")
    st.success("TMD")

with col2:

    st.warning("OpenAQ (Planned)")
    st.warning("Sentinel-5P (Planned)")

st.markdown("---")

# -------------------
# Raw Data
# -------------------

df = load_data()

st.subheader("📊 Database")

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

st.markdown("---")

# -------------------
# Team
# -------------------

st.caption("""
Developed By

Member 1
Member 2
Member 3
""")
