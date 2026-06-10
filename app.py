import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

# ==========================================
# 1. PREMIUM CYBER DARK INFOGRAPHIC THEME
# ==========================================
st.set_page_config(layout="wide", page_title="Intelligent Environmental Dashboard")

# CSS ยกเครื่องหน้าตาใหม่ทั้งหมดให้ตรงปกอินโฟกราฟิก
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&family=Sarabun:wght@400;700&display=swap');
        
        ::-webkit-scrollbar { display: none; }
        
        html, body, [data-testid="stAppViewContainer"] { 
            background-color: #0d111c !important;
            color: #f8fafc !important;
            font-family: 'Inter', 'Sarabun', sans-serif;
        }
        .block-container { padding: 1.5rem 2.5rem !important; }
        
        /* 📦 การ์ดคุมกล่องข้อความและกราฟให้มีมิติ */
        .info-card {
            background-color: #151c2e;
            border: 1px solid #222f4c;
            border-radius: 6px;
            padding: 14px;
            margin-bottom: 12px;
        }
        
        .section-header {
            font-size: 11px;
            font-weight: 800;
            color: #94a3b8;
            letter-spacing: 0.8px;
            margin-bottom: 8px;
            text-transform: uppercase;
        }
        
        /* 🔒 ล็อก Dropdown ห้ามพิมพ์ตัวหนังสือหลุด */
        div[data-baseweb="select"] input { pointer-events: none !important; caret-color: transparent !important; }
        div[data-baseweb="select"] { background-color: #1c2541 !important; border: 1px solid #3a506b !important; border-radius: 4px; }
        div[data-baseweb="select"] * { color: #ffffff !important; font-size: 12px !important; }
        label[data-testid="stWidgetLabel"] { font-size: 11px !important; color: #94a3b8 !important; font-weight: bold; }
        
        /* 💧 สไตล์ Timeline ระบบตรวจสอบน้ำด้านล่างขวา */
        .water-node {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 6px 0;
            border-bottom: 1px dashed #222f4c;
        }
        .water-station { font-size: 12px; font-weight: 700; color: #38bdf8; display: flex; align-items: center; gap: 6px; }
        .badge-grid { display: flex; gap: 8px; }
        .pills { padding: 2px 10px; border-radius: 12px; font-size: 10px; font-weight: 800; text-align: center; color: white; }
        .pills-pass { background-color: #10b981; }
        .pills-warn { background-color: #ef4444; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. DATA CONFIGURATION & TIME SERIES
# ==========================================
years_axis = [1930, 1950, 1970, 1990, 2000, 2010, 2026]
months_axis = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

REGIONAL_DB = {
    "📌 CENTRAL (ภาคกลาง)": {
        "co2": 421.5, "co2_sub": "+0.3% vs. last month", "temp": 1.8, "aqi": 85, "aqi_lbl": "Moderate", "aqi_col": "#f59e0b",
        "co2_history": [250, 380, 520, 680, 850, 1050, 1420],
        "pm25_series": [12, 14, 18, 24, 30, 28, 22, 15, 13, 11, 12, 14],
        "temp_series": [18, 19, 23, 27, 30, 29, 28, 27, 26, 23, 20, 18]
    },
    "📌 NORTH (ภาคเหนือ)": {
        "co2": 412.8, "co2_sub": "+0.1% vs. last month", "temp": 2.4, "aqi": 165, "aqi_lbl": "Unhealthy", "aqi_col": "#ef4444",
        "co2_history": [210, 300, 450, 590, 720, 910, 1150],
        "pm25_series": [45, 68, 95, 120, 75, 30, 22, 19, 24, 38, 48, 55],
        "temp_series": [15, 18, 24, 29, 28, 27, 26, 25, 24, 22, 18, 15]
    }
}

# ==========================================
# 3. TOP MAIN HEADER
# ==========================================
st.markdown("""
<div style="text-align: center; margin-bottom: 20px;">
    <h1 style="color: #ffffff; font-size: 24px; font-weight: 800; margin: 0; letter-spacing: 0.5px;">INTELLIGENT ENVIRONMENTAL & GHG MONITORING DASHBOARD (THAILAND)</h1>
    <div style="color: #38bdf8; font-size: 13px; font-weight: 600; margin-top: 2px;">แดชบอร์ดอัจฉริยะติดตามก๊าซเรือนกระจกและมลพิษ (ประเทศไทย)</div>
</div>
""", unsafe_allow_html=True)

# ==========================================
# 4. FILTER BAR CONTROL
# ==========================================
ctrl_c = st.columns([2.5, 3, 3, 3])
with ctrl_c[0]:
    st.markdown('<div style="font-family: monospace; font-size: 13px; color: #10b981; font-weight: 800; margin-top: 24px;">⏱️ MARCH 2026 | 13:58:55</div>', unsafe_allow_html=True)
with ctrl_c[1]:
    selected_reg = st.selectbox("REGION:", list(REGIONAL_DB.keys()))
with ctrl_c[2]:
    st.selectbox("DATA SOURCE:", ["ALL SYSTEMS INTEGRATED", "SATELLITE ORBITAL"])
with ctrl_c[3]:
    st.selectbox("TIME:", ["1 MONTH WINDOW", "ALL TIME RECORD"])

st.markdown("<div style='margin-bottom: 15px;'></div>", unsafe_allow_html=True)
db = REGIONAL_DB[selected_reg]

# ==========================================
# 5. TIER 1: KEY ENVIRONMENTAL METRICS (GAUGES)
# ==========================================
st.markdown('<div class="section-header">📊 KEY ENVIRONMENTAL METRICS</div>', unsafe_allow_html=True)
g1, g2, g3 = st.columns(3)

# ฟังก์ชันกลางสำหรับคุมหน้าตาเกจให้เพรียวบางสไตล์อินโฟกราฟิก
def create_premium_gauge(val, min_v, max_v, title, color, suffix="", prefix=""):
    fig = go.Figure(go.Indicator(
        mode="gauge+number", value=val,
        number={'font': {'size': 26, 'color': '#ffffff', 'family': 'Inter'}, 'suffix': suffix, 'prefix': prefix},
        gauge={
            'axis': {'range': [min_v, max_v], 'visible': False},
            'bar': {'color': color, 'thickness': 0.15},
            'bgcolor': 'rgba(0,0,0,0)',
            'bordercolor': 'rgba(0,0,0,0)'
        }
    ))
    fig.update_layout(
        height=85, margin=dict(t=0, b=0, l=10, r=10),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)"
    )
    return fig

with g1:
    st.markdown(f'<div class="info-card"><div style="font-size:10px; font-weight:bold; color:#38bdf8; margin-bottom:2px;">1️⃣ ATMOSPHERIC CO₂ LEVEL</div>', unsafe_allow_html=True)
    st.plotly_chart(create_premium_gauge(db["co2"], 350, 500, "CO2", "#0284c7", " ppm"), use_container_width=True, config={'displayModeBar': False})
    st.markdown(f'<div style="text-align:center; font-size:11px; color:#ef4444; font-weight:bold; margin-top:-10px;">{db["co2_sub"]}</div></div>', unsafe_allow_html=True)

with g2:
    st.markdown(f'<div class="info-card"><div style="font-size:10px; font-weight:bold; color:#f97316; margin-bottom:2px;">2️⃣ AV. TEMPERATURE ANOMALY</div>', unsafe_allow_html=True)
    st.plotly_chart(create_premium_gauge(db["temp"], 0, 4, "TEMP", "#e11d48", "°C", "+"), use_container_width=True, config={'displayModeBar': False})
    st.markdown('<div style="text-align:center; font-size:11px; color:#94a3b8; margin-top:-10px;">Dangerous Threshold: +4.0°C</div></div>', unsafe_allow_html=True)

with g3:
    st.markdown(f'<div class="info-card"><div style="font-size:10px; font-weight:bold; color:#eab308; margin-bottom:2px;">3️⃣ AIR QUALITY INDEX (AQI)</div>', unsafe_allow_html=True)
    st.plotly_chart(create_premium_gauge(db["aqi"], 0, 200, "AQI", db["aqi_col"]), use_container_width=True, config={'displayModeBar': False})
    st.markdown(f'<div style="text-align:center; font-size:11px; color:{db["aqi_col"]}; font-weight:bold; margin-top:-10px;">{db["aqi_lbl"]}</div></div>', unsafe_allow_html=True)

# ==========================================
# 6. TIER 2: SMOOTH HOTSPOT CONTOUR & TRENDS
# ==========================================
mid_l, mid_r = st.columns([1.1, 1.0])

with mid_l:
    st.markdown('<div class="info-card" style="height: 295px;">', unsafe_allow_html=True)
    st.markdown('<div class="section-header" style="color:#38bdf8;">🔥 GHG & POLLUTION HOTSPOTS (BANGKOK & PERIPHERY)</div>', unsafe_allow_html=True)
    
    # 🌟 เทคนิคเด็ด: ใช้สูตรคณิตศาสตร์ทำคลื่นความร้อนโค้งมนแบบสากลแทนการสุ่มบล็อกหยาบๆ
    grid_res = 80
    x = np.linspace(0, 10, grid_res)
    y = np.linspace(0, 10, grid_res)
    X, Y = np.meshgrid(x, y)
    # สมมติให้จุดศูนย์กลางความร้อนอยู่ที่กรุงเทพฯ (พิกัด 5,5) แผ่ออกเป็นทรงกลมไล่ระดับความสวยงาม
    Z = np.exp(-((X - 5)**2 + (Y - 5)**2) / 6.5) * 160 + np.exp(-((X - 7)**2 + (Y - 3)**2) / 2.0) * 80
    
    fig_contour = go.Figure(data=go.Contour(
        z=Z, x=x, y=y,
        colorscale=[[0, '#10b981'], [0.4, '#f59e0b'], [1, '#7f1d1d']],
        showscale=False, line_width=0, contours=dict(coloring='heatmap', smoothing=1.3)
    ))
    # ปักหมุดจำลองชื่อจังหวัดประกอบแผนที่
    fig_contour.add_trace(go.Scatter(
        x=[5, 7.5, 2.5, 1.5], y=[5, 2.5, 3.5, 6],
        mode='markers+text',
        text=['🔴 BANGKOK', 'SAMUT PRAKAN', 'KAMAT', 'FANG'],
        textposition='top center',
        textfont=dict(size=9, color='white', family='Inter'),
        marker=dict(color='white', size=4)
    ))
    fig_contour.update_layout(
        height=225, margin=dict(t=10, b=10, l=10, r=10),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
    )
    st.plotly_chart(fig_contour, use_container_width=True, config={'displayModeBar': False})
    st.markdown('</div>', unsafe_allow_html=True)

with mid_r:
    st.markdown('<div class="info-card" style="height: 295px;">', unsafe_allow_html=True)
    st.markdown('<div class="section-header">📈 CHARTS AREA</div>', unsafe_allow_html=True)
    
    # 1. 30-Year Area Chart (เส้นสมูทเรืองแสง)
    df_trend = pd.DataFrame({'Year': years_axis, 'CO2': db["co2_history"]})
    fig_area = px.area(df_trend, x='Year', y='CO2')
    fig_area.update_traces(line=dict(color='#38bdf8', width=2, shape='spline'), fillcolor='rgba(56, 189, 248, 0.15)')
    fig_area.update_layout(
        height=100, margin=dict(t=5, b=5, l=10, r=10), template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        title={'text': "<b>30-YEAR CO₂ EMISSIONS TREND (KT/YR)</b>", 'font': {'size': 9, 'color': '#94a3b8'}},
        xaxis=dict(showgrid=False, font=dict(size=8)), yaxis=dict(showgrid=False, font=dict(size=8))
    )
    st.plotly_chart(fig_area, use_container_width=True, config={'displayModeBar': False})
    
    # 2. Combo Chart
    fig_combo = make_subplots(specs=[[{"secondary_y": True}]])
    fig_combo.add_trace(go.Bar(x=months_axis, y=db["pm25_series"], name='PM2.5', marker_color='#f97316', marker_line_width=0), secondary_y=False)
    fig_combo.add_trace(go.Scatter(x=months_axis, y=db["temp_series"], name='Temp', line=dict(color='#38bdf8', width=2, shape='spline')), secondary_y=True)
    fig_combo.update_layout(
        height=100, margin=dict(t=15, b=5, l=10, r=10), template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", showlegend=False,
        title={'text': "<b>MONTHLY TEMPERATURE VS. AIR QUALITY</b>", 'font': {'size': 9, 'color': '#94a3b8'}},
        xaxis=dict(showgrid=False, font=dict(size=8)), yaxis=dict(showgrid=False, font=dict(size=8)),
        yaxis2=dict(showgrid=False, font=dict(size=8))
    )
    st.plotly_chart(fig_combo, use_container_width=True, config={'displayModeBar': False})
    st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# 7. TIER 3: POLLUTION BREAKDOWN & WATER NODES
# ==========================================
bot_l, bot_r = st.columns([1.1, 1.0])

with bot_l:
    st.markdown('<div class="info-card" style="height: 200px;">', unsafe_allow_html=True)
    st.markdown('<div class="section-header">📊 POLLUTION BREAKDOWN (PM2.5, NO₂, SO₂)</div>', unsafe_allow_html=True)
    
    elements = ['PM2.5', 'PM10', 'NO₂', 'NOx', 'SO₂']
    fig_stack = go.Figure()
    fig_stack.add_trace(go.Bar(name='Low', x=elements, y=[40, 50, 70, 60, 80], marker_color='#10b981'))
    fig_stack.add_trace(go.Bar(name='Moderate', x=elements, y=[50, 45, 35, 40, 30], marker_color='#f59e0b'))
    fig_stack.add_trace(go.Bar(name='Unhealthy', x=elements, y=[70, 35, 45, 55, 40], marker_color='#ef4444'))
    
    fig_stack.update_layout(
        barmode='stack', height=145, margin=dict(t=5, b=5, l=5, r=5), template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", showlegend=False,
        xaxis=dict(showgrid=False, font=dict(size=9)), yaxis=dict(showgrid=False, font=dict(size=9))
    )
    st.plotly_chart(fig_stack, use_container_width=True, config={'
