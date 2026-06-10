import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from datetime import datetime
import pytz

# ===== PAGE =====
st.set_page_config(
    layout="wide",
    page_title="GHG Monitor Board",
    initial_sidebar_state="expanded"
)

# ===== CSS (เหมือนเดิม) =====
st.markdown("""
<style>
::-webkit-scrollbar { display: none; }
.stApp { overflow: hidden !important; height: 100vh !important; }

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

# ===== DATA =====
def get_data():

    tz = pytz.timezone("Asia/Bangkok")
    now = datetime.now(tz)

    dates = pd.date_range(end=now.replace(minute=0, second=0, microsecond=0),
                           periods=365, freq="h")  # เพิ่ม data สำหรับปี

    df = pd.DataFrame({
        "Date": dates,
        "CO₂ (ppm)": np.random.normal(430, 8, 365).round(1),
        "CH₄ (ppb)": np.random.normal(1860, 15, 365).round(1),
        "NO₂ (ppb)": np.random.normal(42, 3, 365).round(1),
        "PM 2.5 (µg/m³)": np.random.normal(25, 5, 365).round(1),
        "Temp (°C)": np.random.normal(33, 1.5, 365).round(1),
        "Humid (%)": np.random.normal(60, 4, 365).round(1)
    })

    df["Date"] = pd.to_datetime(df["Date"])
    return df, now


df, now = get_data()

pollutants = [c for c in df.columns if c != "Date"]

# ===== SIDEBAR =====
with st.sidebar:

    st.markdown("### 📋 เมนูควบคุม")

    selected = st.selectbox("สารมลพิษ:", pollutants)

    mode = st.radio(
        "รูปแบบ:",
        ["รายวัน (24h)", "รายเดือน (30d)", "รายปี (overview)"]
    )

# ===== FILTER =====
df_plot = df.copy()

if mode == "รายวัน (24h)":
    df_plot = df_plot.tail(24)

elif mode == "รายเดือน (30d)":
    df_plot = df_plot.groupby(df_plot["Date"].dt.date).mean(numeric_only=True).reset_index()
    df_plot["Date"] = pd.to_datetime(df_plot["Date"])

elif mode == "รายปี (overview)":
    df_plot = df_plot.groupby(df_plot["Date"].dt.month).mean(numeric_only=True).reset_index()
    df_plot["Date"] = pd.to_datetime("2026-" + df_plot["Date"].astype(str) + "-01")

# ===== METRICS =====
latest = df.iloc[-1]
cols = st.columns(len(pollutants))

for i, col in enumerate(pollutants):
    cols[i].metric(
        label=col,
        value=int(round(latest[col], 0)),
        delta=int(round(df.iloc[-1][col] - df.iloc[-2][col], 0))
    )

# ===== GRAPH =====
fig = px.line(
    df_plot,
    x="Date",
    y=selected,
    template="plotly_dark",
    height=280
)

fig.update_traces(line_color="#00ffcc", line_width=3)

fig.update_layout(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    margin=dict(t=20, b=10, l=10, r=10),
    xaxis_title=None,
    yaxis_title=None
)

st.plotly_chart(fig, use_container_width=True)
