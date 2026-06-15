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

# =====================================================
# 📈 GRAPH (UNCHANGED FROM YOUR VERSION)
# =====================================================
with center:

    st.subheader("📈 Graph")

    selected = st.multiselect(
        "Select data",
        ["CO2", "CH4", "NO2", "PM25", "Temp", "Humidity"],
        default=["CO2"]
    )

    plot_df = df_plot.copy()

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

# =====================================================
# 🔥 RIGHT PANEL (DRILL-DOWN CLEAN VERSION)
# =====================================================
with right:

    st.subheader("📊 Detail View")

    selected_single = st.selectbox(
        "เลือกตัวแปร",
        ["CO2", "CH4", "NO2", "PM25", "Temp", "Humidity"]
    )

    series = pd.to_numeric(df[selected_single], errors="coerce").dropna()

    if len(series) > 0:

        last = series.iloc[-1]
        avg = series.mean()
        mx = series.max()
        mn = series.min()

        trend = series.iloc[-1] - series.iloc[-min(5, len(series))]

        st.metric("Latest", f"{last:.2f}")
        st.metric("Average", f"{avg:.2f}")
        st.metric("Max", f"{mx:.2f}")
        st.metric("Min", f"{mn:.2f}")

        st.markdown("---")

        st.markdown("### 📈 Trend (5-step)")
        st.metric("Change", f"{trend:.2f}")

        # simple status
        if selected_single == "CO2":
            if avg < 450:
                st.success("🟢 Normal")
            elif avg < 500:
                st.warning("🟡 Warning")
            else:
                st.error("🔴 Critical")

        elif selected_single == "PM25":
            if avg < 25:
                st.success("🟢 Good")
            elif avg < 50:
                st.warning("🟡 Moderate")
            else:
                st.error("🔴 Unhealthy")

        else:
            st.info("Status OK")
