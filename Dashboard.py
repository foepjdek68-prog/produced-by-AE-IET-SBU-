import streamlit as st
import plotly.express as px
import pandas as pd
from datetime import datetime

from Services.database import load_data, save_data
from Services.api_loader import fetch_data

st.set_page_config(
    page_title="Dashboard Tracking Greenhouse Gases Emission",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>

[data-testid="stMetric"]{
    background:#111827;
    border:1px solid #374151;
    padding:15px;
    border-radius:12px;
}

.block-container{
    padding-top:1rem;
}

</style>
""", unsafe_allow_html=True)

# ---------------- DATA ----------------
df = load_data()

if df.empty:
    df = fetch_data()
    save_data(df)

df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
df = df.dropna(subset=["Date"]).sort_values("Date").reset_index(drop=True)

latest = df.iloc[-1]
prev = df.iloc[-2] if len(df) > 1 else latest

thai_date = latest["Date"].strftime("%d/%m/%y")

st.info("""
### 🌍 Dashboard Tracking

## Greenhouse Gases Emission
""")

st.caption(f"ข้อมูลล่าสุด : {thai_date}")

# ---------------- SAFE KPI ----------------
def kpi(col, symbol, name=None):
    now_raw = latest.get(col, 0)
    old_raw = prev.get(col, 0)

    try:
        now = float(now_raw) if pd.notna(now_raw) else 0
    except:
        now = 0

    try:
        old = float(old_raw) if pd.notna(old_raw) else 0
    except:
        old = 0

    diff = now - old

    arrow = "↑" if diff > 0 else "↓" if diff < 0 else "→"

    label = f"{symbol} ({name})" if name else symbol

    return now, f"{arrow} {diff:.2f}", label


# ---------------- KPI ----------------
c1, c2, c3, c4, c5, c6 = st.columns(6)

v, d, label = kpi("CO2", "CO₂", "Carbon Dioxide")
c1.metric(label, f"{v:.2f}", d)

v, d, label = kpi("CH4", "CH₄", "Methane")
c2.metric(label, f"{v:.2f}", d)

v, d, label = kpi("NO2", "NO₂", "Nitrogen Dioxide")
c3.metric(label, f"{v:.2f}", d)

v, d, label = kpi("PM25", "PM2.5")
c4.metric(label, f"{v:.2f}", d)

v, d, label = kpi("Temp", "Temperature")
c5.metric(label, f"{v:.2f}", d)

v, d, label = kpi("Humidity", "Humidity")
c6.metric(label, f"{v:.2f}", d)

st.markdown("---")

# ---------------- PERIOD ----------------
period = st.selectbox(
    "ช่วงการแสดงผล",
    ["Daily", "Weekly", "Monthly", "Annual"]
)

if period == "Daily":
    df_plot = df.tail(24)
elif period == "Weekly":
    df_plot = df.tail(24 * 7)
elif period == "Monthly":
    df_plot = df.tail(24 * 30)
else:
    df_plot = df

# ---------------- LAYOUT ----------------
center, right = st.columns([4, 1.2])

# ===================== GRAPH FIXED =====================
with center:

    st.subheader("📈 Graph")

    graph_mode = st.radio(
        "Mode",
        ["Actual", "Compare"],
        horizontal=True
    )

    # ✔ ใช้ชื่อจริงตรง dataframe (สำคัญมาก)
    selected = st.multiselect(
        "Select data",
        ["CO2", "CH4", "NO2", "PM25", "Temp", "Humidity"],
        default=["CO2"]
    )

    plot_df = df_plot.copy()

    # ---------------- COMPARE MODE ----------------
    if graph_mode == "Compare":

        scale = {
            "CO2": 1000,
            "CH4": 100,
            "NO2": 100,
            "PM25": 100,
            "Temp": 50,
            "Humidity": 100
        }

        for col in selected:
            plot_df[col] = pd.to_numeric(plot_df[col], errors="coerce").fillna(0)
            plot_df[col] = (plot_df[col] / scale[col]) * 100

    # ---------------- TIME ----------------
    plot_df["Date"] = pd.to_datetime(plot_df["Date"], errors="coerce")
    plot_df = plot_df.sort_values("Date")

    # ---------------- PLOT ----------------
    fig = px.line(
        plot_df,
        x="Date",
        y=selected,
        markers=True,
        template="plotly_dark"
    )

    color_map = {
        "CO2": "#DC2626",
        "CH4": "#F97316",
        "NO2": "#7C3AED",
        "PM25": "#EAB308",
        "Temp": "#22C55E",
        "Humidity": "#2563EB"
    }

    for t in fig.data:
        k = t.name
        t.line.color = color_map.get(k, "#ffffff")
        t.line.width = 3

    st.plotly_chart(fig, use_container_width=True)

# ---------------- RIGHT INSIGHT (UNCHANGED) ----------------
with right:

    st.subheader("📌 Insight")

    selected_cols = selected if selected else ["CO2"]

    for col in selected_cols:

        if col not in df.columns:
            continue

        avg = df[col].mean()
        mx = df[col].max()
        mn = df[col].min()
        last = df[col].iloc[-1]

        st.metric(
            label=col,
            value=f"{last:.2f}",
            delta=f"Avg {avg:.2f}"
        )

        st.caption(f"Max: {mx:.2f}")
        st.caption(f"Min: {mn:.2f}")
        st.markdown("---")

    st.subheader("📊 CO2 Status")

    avg_co2 = df["CO2"].mean()

    if avg_co2 < 450:
        st.success("Normal")
    elif avg_co2 < 500:
        st.warning("Warning")
    else:
        st.error("Critical")
