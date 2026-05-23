import streamlit as st
import pandas as pd
import plotly.express as px

# ตั้งค่าหน้าจอ
st.set_page_config(layout="wide")

# ข้อมูลจำลอง
data = {
    "ภาค": ["ภาคกลาง", "ภาคเหนือ", "ภาคใต้", "ภาคอีสาน", "ภาคตะวันออก", "ภาคตะวันตก"],
    "ค่า CO2": [433, 412, 405, 418, 420, 410]
}
df = pd.DataFrame(data)

st.title("ระบบวิเคราะห์ข้อมูลสภาพภูมิอากาศ")

# ส่วนแสดงตัวเลขสรุป
cols = st.columns(6)
for i, col in enumerate(cols):
    col.metric(df["ภาค"][i], f"{df['ค่า CO2'][i]} ppm")

# แบ่งหน้าจอ 50/50
left, right = st.columns(2)

with left:
    st.subheader("แผนที่แสดงข้อมูล")
    # ใช้ Bar chart แทน Map ในขั้นตอนนี้เพื่อป้องกัน Error จาก Pydeck
    fig_bar = px.bar(df, x="ภาค", y="ค่า CO2", color="ค่า CO2")
    st.plotly_chart(fig_bar, use_container_width=True)

with right:
    st.subheader("ตารางข้อมูล")
    st.table(df)

# กราฟด้านล่าง
st.subheader("แนวโน้มข้อมูล")
fig_line = px.line(df, x="ภาค", y="ค่า CO2")
st.plotly_chart(fig_line, use_container_width=True)
