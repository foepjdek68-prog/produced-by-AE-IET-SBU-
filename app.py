import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from datetime import datetime
import pytz
import os

# ===== PAGE =====
st.set_page_config(
    layout="wide",
    page_title="GHG Monitor Board",
    initial_sidebar_state="expanded"
)

# ===== CSS (เหมือนของคุณ) =====
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
    background: rgba(255, 255, 255, 0.03);
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)

# ===== DATA SOURCE (REALISTIC SIMULATION / READY FOR API) =====
def get_data():

    tz = pytz.timezone("Asia/Bangkok")
    now = datetime.now(tz)

    dates = pd.date_range(end=now.replace(minute=0, second=0, microsecond=0), periods=30, freq="h")

    df = pd.DataFrame({
        "Date": dates,
        "CO₂ (ppm)": np.random.normal(430, 8, 30).round(1),
        "CH₄ (ppb)": np.random.normal(1860, 15, 30).round(1),
        "NO₂ (ppb)": np.random.normal(42, 3, 30).round(1),
        "PM 2.5 (µg/m³)": np.random.normal(25, 5, 30).round(1),
        "Temp (°C)": np.random.normal(33, 1.5, 30).round(1),
        "Humid (%)": np.random.normal(60, 4, 30).round(1)
    })

    df["Date"] = pd.to_datetime(df["Date"])
    return df, now


df, now = get_data()
latest = df.iloc[-1]

pollutants = [c for c in df.columns if c != "Date"]

# ===== HEADER =====
st.title("🌍 Tracking GHGs Emission")

# ===== METRICS (เหมือนของคุณ) =====
cols = st.columns(6)

for i, col in enumerate(pollutants):

    val = latest[col]
    delta = val - df.iloc[-2][col]

    cols[i].metric(
        label=col,
        value=int(round(val, 0)),
        delta=int(round(delta, 0))
    )

# ===== SIDEBAR =====
with st.sidebar:

    st.markdown("### 📋 เมนูควบคุม")

    selected = st.selectbox("สารมลพิษ:", pollutants)

    mode = st.radio("รูปแบบ:", ["รายชั่วโมง", "รายวัน"])

    st.markdown("""
        <div class="brand-box">
            <img src="https://comci.southeast.ac.th/2025/img/SBU.png" width="40">
            <div style="font-weight:bold; margin-top:5px; color:white; font-size: 12px;">AE-IET [SBU]</div>
            <div style="font-size:9px; color:#888;">Engineering Team</div>
        </div>
    """, unsafe_allow_html=True)

# ===== GRAPH (SIMPLE + CLEAN LIKE YOUR STYLE) =====
df_plot = df.copy()

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
