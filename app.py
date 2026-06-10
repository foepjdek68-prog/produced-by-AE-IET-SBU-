import streamlit as st
from utils.database import load_data, save_data
from utils.api_loader import fetch_data

st.set_page_config(
    page_title="GHG Tracking System",
    layout="wide"
)

df = load_data()

if df.empty:
    df = fetch_data()
    save_data(df)

st.title("🌍 Smart GHG Tracking System")

st.markdown("""
### Tracking Greenhouse Gas Emissions

1️⃣ Data Sources

2️⃣ API Collection

3️⃣ SQLite Storage

4️⃣ Analytics

5️⃣ Dashboard

6️⃣ Users
""")

st.success("เลือกเมนูจาก Sidebar")
