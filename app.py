import streamlit as st
import pandas as pd
import requests
import plotly.express as px
from datetime import datetime
import pytz

# ===== PAGE =====
st.set_page_config(layout="wide", page_title="GHG Real Monitor", initial_sidebar_state="expanded")

# ===== CSS (คงของเดิม) =====
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
</style>
""", unsafe_allow_html=True)

# ===== REAL API FETCH (Air4Thai) =====
def get_real_data():

    # ตัวอย่าง endpoint (air4thai public endpoint)
    url = "http://air4thai.pcd.go.th/services/getNewAQI_JSON.php"

    try:
        res = requests.get(url, timeout=10)
        data = res.json()

        records = data["stations"]

        rows = []
        for r in records:
            rows.append({
                "station": r["nameTH"],
                "AQI": float(r["AQI"]["aqi"]),
                "PM2.5": float(r["AQI"]["PM25"]["value"]) if "PM25" in r["AQI"] else None,
                "time": r["AQI"]["date"]
            })

        df = pd.DataFrame(rows)

        df["time"] = pd.to_datetime(df["time"], errors="coerce")

        return df

    except Exception as e:
        st.error("❌ ดึงข้อมูล API ไม่ได้")
        return pd.DataFrame()


df = get_real_data()

# ===== CHECK =====
if df.empty:
    st.stop()

# ===== SIDEBAR =====
with st.sidebar:
    st.title("📊 Real Monitoring")

    station = st.selectbox("เลือกสถานี", df["station"].unique())

# ===== FILTER =====
df_plot = df[df["station"] == station]

latest = df_plot.iloc[-1]

# ===== METRICS =====
col1, col2 = st.columns(2)

col1.metric("AQI", int(latest["AQI"]))
col2.metric("PM2.5", latest["PM2.5"])

# ===== GRAPH =====
fig = px.line(
    df_plot,
    x="time",
    y="AQI",
    template="plotly_dark",
    height=350
)

fig.update_traces(line_color="#00ffcc", line_width=3)

fig.update_layout(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    margin=dict(t=20, b=10, l=10, r=10)
)

st.plotly_chart(fig, use_container_width=True)
