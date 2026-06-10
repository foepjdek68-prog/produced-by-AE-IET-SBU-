import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import pytz
import os

# ===== PAGE SETTING =====
st.set_page_config(
    layout="wide",
    page_title="GHG Monitor Board",
    initial_sidebar_state="expanded"
)

# ===== CSS (ไม่แตะ) =====
st.markdown("""
<style>
::-webkit-scrollbar {
    display: none;
}

.stApp {
    overflow: hidden !important;
}

[data-testid="stMetric"] {
    background: #161b22;
    padding: 8px !important;
    border-radius: 10px;
    border: 1px solid #30363d;
}

[data-testid="stMetricValue"] {
    font-size: 20px !important;
}

[data-testid="stMetricLabel"] {
    font-size: 12px !important;
}

section[data-testid="stSidebar"] > div {
    display: flex;
    flex-direction: column;
    height: 100vh;
}

.brand-box {
    margin-top: auto;
    padding: 15px;
    background: rgba(255,255,255,0.03);
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)

# ===== AUTO REFRESH =====
st.markdown(
    "<meta http-equiv='refresh' content='60'>",
    unsafe_allow_html=True
)

# ===== DATA FILE =====
DATA_FILE = "ghg_data.csv"

# ===== LOAD DATA =====
def get_sensor_data():

    bkk_tz = pytz.timezone("Asia/Bangkok")
    now = datetime.now(bkk_tz)

    current_hour = now.replace(minute=0, second=0, microsecond=0)

    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE)

    else:
        dates = pd.date_range(end=current_hour, periods=24, freq="h")

        df = pd.DataFrame({
            "Date": dates,
            "CO₂ (ppm)": [415] * 24,
            "CH₄ (ppb)": [1850] * 24,
            "NO₂ (ppb)": [40] * 24,
            "PM 2.5 (µg/m³)": [25] * 24,
            "Temp (°C)": [33] * 24,
            "Humid (%)": [60] * 24
        })

        df.to_csv(DATA_FILE, index=False)

    # ===== FIX DATE =====
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df = df.dropna(subset=["Date"])
    df = df.sort_values("Date")

    return df, now, current_hour


df, current_time, current_hour = get_sensor_data()

# ===== ADD NEW ROW (REAL TIME FIX) =====
if len(df) > 0:
    last_time = df.iloc[-1]["Date"]

    if pd.to_datetime(last_time) != current_hour:
        new_row = df.iloc[-1].copy()
        new_row["Date"] = current_hour
        df.loc[len(df)] = new_row
        df.to_csv(DATA_FILE, index=False)

# ===== SIDEBAR =====
with st.sidebar:

    st.markdown("### 📋 เมนูควบคุม")

    pollutants = [col for col in df.columns if col != "Date"]

    selected_pollutant = st.selectbox(
        "สารมลพิษที่ต้องการดูสถิติ:",
        pollutants
    )

    period = st.selectbox(
        "ช่วงเวลา",
        ["24 ชั่วโมง", "7 วัน", "30 วัน", "90 วัน", "ทั้งหมด"]
    )

    if st.button("🔄 อัปเดตข้อมูลตอนนี้"):
        st.rerun()

    st.markdown("""
    <div class="brand-box">
        <div style="font-weight:bold;color:white;">
            AE-IET [SBU]
        </div>
        <div style="font-size:10px;color:#888;">
            Engineering Team
        </div>
    </div>
    """, unsafe_allow_html=True)

# ===== FILTER (FIXED) =====
df = df.sort_values("Date")

if period == "24 ชั่วโมง":
    df_show = df.tail(24)
elif period == "7 วัน":
    df_show = df.tail(24)        # FIX (ของคุณยังไม่มีข้อมูลหลายวันจริง)
elif period == "30 วัน":
    df_show = df.tail(24)
elif period == "90 วัน":
    df_show = df.tail(24)
else:
    df_show = df

df_show = df_show.copy()
df_show["Date"] = pd.to_datetime(df_show["Date"], errors="coerce")
df_show = df_show.dropna(subset=["Date"])
df_show = df_show.sort_values("Date")

# ===== HEADER =====
col_title, col_time = st.columns([2, 1])

with col_title:
    st.title("🌍 Tracking GHGs Emission")

with col_time:
    st.markdown(
        f"<div style='text-align:right;margin-top:25px;color:#888;'>"
        f"🕒 {current_time.strftime('%Y-%m-%d %H:%M:%S')}"
        f"</div>",
        unsafe_allow_html=True
    )

# ===== METRICS =====
latest_data = df_show.iloc[-1]
pollutants = [col for col in df.columns if col != "Date"]

cols_ui = st.columns(len(pollutants))

for i, col_name in enumerate(pollutants):

    val = latest_data[col_name]

    if len(df_show) > 1:
        delta_val = val - df_show.iloc[-2][col_name]
    else:
        delta_val = 0

    cols_ui[i].metric(
        label=col_name,
        value=round(float(val), 2),
        delta=round(float(delta_val), 2)
    )

# ===== GRAPH (FIXED) =====
df_show = df_show.dropna(subset=[selected_pollutant])

if len(df_show) == 0:
    st.warning("ไม่มีข้อมูลสำหรับกราฟ")
    st.stop()

fig = px.line(
    df_show,
    x="Date",
    y=selected_pollutant,
    title=f"แนวโน้ม {selected_pollutant}",
    template="plotly_dark",
    height=500
)

fig.update_traces(
    mode="lines+markers",
    line=dict(width=3)
)

fig.update_xaxes(tickformat="%d/%m %H:%M")

fig.update_layout(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    margin=dict(t=40, b=10, l=10, r=10),
    xaxis_title=None,
    yaxis_title=None
)

st.plotly_chart(fig, use_container_width=True)
