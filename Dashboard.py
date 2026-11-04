import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import time
from streamlit_autorefresh import st_autorefresh
from Services.database import load_data, save_data
from Services.api_loader import fetch_data

# =====================================================
# PAGE CONFIG
# =====================================================
st.set_page_config(
    page_title="Dashboard Tracking GHGs Concentration",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =====================================================
# REFRESH CONTROL
# =====================================================
st_autorefresh(interval=60000, key="refresh_timer")

# =====================================================
# LOAD DATA
# =====================================================
@st.cache_data(ttl=3600)
def get_data():
    df = load_data()
    if df.empty:
        df = fetch_data()
        save_data(df)
    if not df.empty:
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        df = df.dropna(subset=["Date"]).sort_values("Date").reset_index(drop=True)
    return df

df = get_data()

if df.empty:
    st.error("No data found in the system. Please check the database connection.")
    st.stop()

latest = df.iloc[-1]
prev = df.iloc[-2] if len(df) > 1 else latest
latest_str = latest["Date"].strftime("%d/%m/%Y %H:%M:%S")

# =====================================================
# SIDEBAR
# =====================================================
with st.sidebar:
    st.markdown('<div style="background:rgba(255,255,255,0.05); padding:15px; border-radius:10px; margin-bottom:20px; text-align:center;">', unsafe_allow_html=True)
    st.image("Assets/logo.png", width=250)
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("""
        <style>
        [data-testid="stSidebar"] > div:first-child { display:flex; flex-direction:column; height:90vh; }
        .sidebar-footer { border-top:1px solid #4B5563; padding-top:10px; margin-top:auto; font-size:0.75em; color:#9CA3AF; }
        </style>
        <div class="sidebar-footer">(C) Dept. Engineering SBU</div>
    """, unsafe_allow_html=True)

# =====================================================
# HEADER & REFRESH BUTTON
# =====================================================
st.markdown(f"""
<div style="background:linear-gradient(135deg,#0f172a,#1e293b); padding:20px; border-radius:12px; border:1px solid #334155; margin-bottom:20px;">
    <h1 style="margin:0; color:white;">🌍 Dashboard Tracking GHGs Concentration</h1>
    <p style="margin-top:8px; color:#cbd5e1;">🕒 Last Updated: {latest_str}</p>
</div>
""", unsafe_allow_html=True)

# =====================================================
# CSS
# =====================================================
st.markdown("""
<style>
.stApp { background:#030712; }
[data-testid="stMetric"] { background:#0f172a !important; border:1px solid #60a5fa !important; border-radius:12px !important; padding:15px !important; text-align:center; }
[data-testid="stMetricLabel"] { color:#cbd5e1 !important; font-weight:600 !important; }
[data-testid="stMetricValue"] { color:white !important; font-weight:700 !important; }
</style>
""", unsafe_allow_html=True)

# =====================================================
# KPI SECTION
# =====================================================
alerts = []
if latest.get("CO2", 0) > 500: alerts.append("🔴 CO₂ level exceeds threshold")
if latest.get("PM25", 0) > 35: alerts.append("⚠ PM2.5 concentration warning")
if latest.get("Temp", 0) > 38: alerts.append("🌡 Temperature exceeds threshold (°C)")

def kpi(col, symbol, name=None):
    now, old = float(latest.get(col, 0)), float(prev.get(col, 0))
    diff = now - old
    percent = (diff / old * 100) if old != 0 else 0
    arrow = "↑" if diff > 0 else "↓" if diff < 0 else "→"
    return now, f"{arrow} {percent:.1f}%", f"{symbol} ({name})" if name else symbol

cols = st.columns(6)
metrics = [
    ("CO2", "CO₂", "ppm"),
    ("CH4", "CH₄", "ppb"),
    ("NO2", "NO₂", "ppb"),
    ("PM25", "PM2.5", "µg/m³"),
    ("Temp", "Temperature", "°C"),
    ("Humidity", "Humidity", "%")
]

for i, (col, sym, name) in enumerate(metrics):
    val, delta, label = kpi(col, sym, name)
    cols[i].metric(label, f"{val:.2f}", delta)

if alerts:
    a_cols = st.columns(len(alerts))
    for i, a in enumerate(alerts):
        if "🔴" in a:
            a_cols[i].error(a)
        else:
            a_cols[i].warning(a)
else:
    st.success("🟢 Environment Status: Normal")

# =====================================================
# GRAPH SECTION
# =====================================================
period = st.selectbox("Select Time Range", ["Daily", "Weekly", "Monthly", "Yearly"])

if period == "Daily":
    df_plot = df.tail(24)
elif period == "Weekly":
    df_plot = df.tail(24 * 7)
elif period == "Monthly":
    df_plot = df.tail(24 * 30)
else:
    df_plot = df

center, right = st.columns([4, 1.2])

with center:
    st.subheader("📈 Data Visualization")
    graph_mode = st.radio("Display Mode", ["Actual", "Comparison"], horizontal=True)
    
    options = {
        "CO₂ (Carbon Dioxide)": "CO2", 
        "CH₄ (Methane)": "CH4", 
        "NO₂ (Nitrogen Dioxide)": "NO2", 
        "PM 2.5 (Particulate Matter)": "PM25", 
        "Temperature": "Temp", 
        "Humidity": "Humidity"
    }

    # กำหนดหน่วยวัดจริงตามมาตรฐานสากล
    unit_map = {
        "CO2": "ppm",
        "CH4": "ppb",
        "NO2": "ppb",
        "PM25": "µg/m³",
        "Temp": "°C",
        "Humidity": "%"
    }
    
    plot_df = df_plot.copy()

    if graph_mode == "Actual":
        sel = st.selectbox("Select Parameter to Display", list(options.keys()))
        selected = [options[sel]]
        
        fig = px.line(plot_df, x="Date", y=selected, markers=True, template="plotly_dark")
        fig.update_layout(
            height=550, 
            hovermode="x unified", 
            paper_bgcolor="#030712", 
            plot_bgcolor="#030712",
            yaxis_title=f"Unit: {unit_map[selected[0]]}"
        )
        # บังคับแกนเริ่มจาก 0
        fig.update_yaxes(rangemode="tozero")
        
        st.plotly_chart(fig, use_container_width=True)

    else:
        sel = st.multiselect("Select Parameters to Compare", list(options.keys()), default=[list(options.keys())[0], list(options.keys())[1]])
        selected = [options[x] for x in sel]
        
        if len(selected) == 0 or len(selected) == 1:
            st.warning("Please select at least 2 parameters to compare.")
            
        elif len(selected) == 2:
            # โหมด 2 แกน (Dual Y-axis)
            var1, var2 = selected[0], selected[1]
            unit1, unit2 = unit_map[var1], unit_map[var2]
            
            fig = make_subplots(specs=[[{"secondary_y": True}]])
            
            # เส้นที่ 1 (แกนซ้าย)
            fig.add_trace(
                go.Scatter(x=plot_df["Date"], y=plot_df[var1], name=sel[0], mode='lines+markers', line=dict(color="#60a5fa")),
                secondary_y=False,
            )
            
            # เส้นที่ 2 (แกนขวา)
            fig.add_trace(
                go.Scatter(x=plot_df["Date"], y=plot_df[var2], name=sel[1], mode='lines+markers', line=dict(color="#f87171")),
                secondary_y=True,
            )
            
            fig.update_layout(
                height=550,
                hovermode="x unified",
                paper_bgcolor="#030712",
                plot_bgcolor="#030712",
                template="plotly_dark",
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            
            # ตั้งชื่อและสีของแกนให้ตรงกับเส้นกราฟ พร้อมบังคับเริ่มจาก 0 ทั้งสองแกน
            fig.update_yaxes(title_text=f"{var1} ({unit1})", secondary_y=False, color="#60a5fa", rangemode="tozero")
            fig.update_yaxes(title_text=f"{var2} ({unit2})", secondary_y=True, color="#f87171", rangemode="tozero")
            
            st.plotly_chart(fig, use_container_width=True)
            
        else:
            # โหมดปรับฐาน 0-100% (กรณีเลือก 3 ตัวแปรขึ้นไป)
            st.info("💡 Selecting more than 2 parameters applies a Normalized Scale (0-100%) for comparison.")
            for col in selected:
                s = pd.to_numeric(plot_df[col], errors="coerce")
                if s.max() - s.min() != 0: 
                    plot_df[col] = (s - s.min()) / (s.max() - s.min()) * 100
                else: 
                    plot_df[col] = 0

            fig = px.line(plot_df, x="Date", y=selected, markers=True, template="plotly_dark")
            fig.update_layout(
                height=550, 
                hovermode="x unified", 
                paper_bgcolor="#030712", 
                plot_bgcolor="#030712",
                yaxis_title="Unit: % (Normalized Scale)"
            )
            # บังคับแกนเริ่มจาก 0
            fig.update_yaxes(rangemode="tozero")
            
            st.plotly_chart(fig, use_container_width=True)

with right:
    st.subheader("📊 System Status")
    st.success("🟢 Online")
    st.metric("Total Records", len(df))
    st.metric("Last Update", latest["Date"].strftime("%H:%M:%S"))
