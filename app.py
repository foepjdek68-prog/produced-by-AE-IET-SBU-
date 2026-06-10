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

# ===== CSS =====
st.markdown("""
<style>
::-webkit-scrollbar { display: none; }

.stApp { overflow: hidden !important; }

[data-testid="stMetric"] {
    background: #161b22;
    padding: 8px !important;
    border-radius: 10px;
    border: 1px solid #30363d;
}

[data-testid="stMetricValue"] { font-size: 20px !important; }
[data-testid="stMetricLabel"] { font-size: 12px !important; }

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
st.markdown("<meta http-equiv='refresh' content='60'>", unsafe_allow_html=True)

# ===== DATA =====
DATA_FILE = "ghg_data.csv"

def load_data():
    tz = pytz.timezone("Asia/Bangkok")
    now = datetime.now(tz)
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


df, now, current_hour = load_data()

# ===== ADD NEW ROW =====
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

    # FIX: เอาเฉพาะ numeric columns
    pollutants = df.select_dtypes(include=["number"]).columns.tolist()

    selected_pollutant = st.selectbox("สารมลพิษ:", pollutants)

    period = st.selectbox(
        "ช่วงเวลา",
        ["24 ชั่วโมง", "7 วัน", "30 วัน", "90 วัน", "ทั้งหมด"]
    )

    if st.button("🔄 รีเฟรช"):
        st.rerun()

# ===== FILTER =====
df = df.sort_values("Date")

limit_map = {
    "24 ชั่วโมง": 24,
    "7 วัน": 24,
    "30 วัน": 24,
    "90 วัน": 24,
    "ทั้งหมด": None
}

limit = limit_map[period]

df_show = df.tail(limit) if limit else df.copy()

df_show["Date"] = pd.to_datetime(df_show["Date"], errors="coerce")
df_show = df_show.dropna(subset=["Date"])

# ===== HEADER =====
col1, col2 = st.columns([2, 1])

with col1:
    st.title("🌍 GHG Dashboard")

with col2:
    st.markdown(
        f"<div style='text-align:right;color:#888;'>🕒 {now.strftime('%Y-%m-%d %H:%M:%S')}</div>",
        unsafe_allow_html=True
    )

# ===== METRICS =====
latest = df_show.iloc[-1]
cols = st.columns(len(pollutants))

for i, c in enumerate(pollutants):
    val = latest[c]
    delta = val - df_show.iloc[-2][c] if len(df_show) > 1 else 0

    cols[i].metric(c, round(val, 2), round(delta, 2))

# ===== GRAPH FIX (สำคัญสุด) =====
df_show[selected_pollutant] = pd.to_numeric(df_show[selected_pollutant], errors="coerce")
df_show = df_show.dropna(subset=[selected_pollutant, "Date"])

if df_show.empty:
    st.error("ไม่มีข้อมูลสำหรับกราฟ")
    st.stop()

fig = px.line(
    df_show,
    x="Date",
    y=selected_pollutant,
    title=f"แนวโน้ม {selected_pollutant}",
    template="plotly_dark",
    height=500
)

fig.update_traces(mode="lines+markers")

fig.update_layout(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    hovermode="x unified"
)

st.plotly_chart(fig, use_container_width=True)
