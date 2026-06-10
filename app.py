import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

# ==========================================
# 1. PREMIUM CYBER INFOGRAPHIC STYLE SHEET
# ==========================================
st.set_page_config(layout="wide", page_title="Intelligent Environmental Dashboard")

st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&family=Sarabun:wght@400;700&display=swap');
        
        ::-webkit-scrollbar { display: none; }
        
        html, body, [data-testid="stAppViewContainer"] { 
            background-color: #0b111e !important;
            color: #f8fafc !important;
            font-family: 'Inter', 'Sarabun', sans-serif;
        }
        .block-container { padding: 1.2rem 2.0rem !important; }
        
        /* 📦 กล่องการ์ดแยกชิ้นตามแบบ Infographic */
        .premium-box {
            background-color: #121826;
            border: 1px solid #1e293b;
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 12px;
        }
        
        .box-title {
            font-size: 11px;
            font-weight: 800;
            color: #94a3b8;
            letter-spacing: 0.8px;
            margin-bottom: 10px;
            text-transform: uppercase;
        }
        
        /* 🔒 ล็อก Dropdown และสไตล์ตัวเลือก */
        div[data-baseweb="select"] input { pointer-events: none !important; caret-color: transparent !important; }
        div[data-baseweb="select"] { background-color: #1a2333 !important; border: 1px solid #2e3c54 !important; border-radius: 4px; }
        div[data-baseweb="select"] * { color: #ffffff !important; font-size: 12px !important; }
        label[data-testid="stWidgetLabel"] { font-size: 11px !important; color: #94a3b8 !important; font-weight: bold; }
        
        /* 💧 ออกแบบระบบสายน้ำไหลและปุ่มสถานะ (Water Badge Engine) */
        .river-row {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 4px 0;
            height: 42px;
        }
        .river-name { font-size: 12px; font-weight: 700; color: #38bdf8; min-width: 110px; }
        .river-svg { flex-grow: 1; margin: 0 10px; height: 20px; }
        .badge-container { display: flex; gap: 6px; }
        .status-pill { padding: 3px 10px; border-radius: 12px; font-size: 9px; font-weight: 800; text-align: center; color: white; width: 65px; }
        .pill-green { background-color: #10b981; box-shadow: 0 0 8px rgba(16,185,129,0.3); }
        .pill-red { background-color: #ef4444; box-shadow: 0 0 8px rgba(239,68,68,0.3); }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. FIXED STATIC DATA REGISTRY
# ==========================================
years = [1930, 1950, 1970, 1990, 2000, 2010, 2026]
months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

DATA_SET = {
    "📌 CENTRAL (ภาคกลาง)": {
        "co2": 421.5, "co2_sub": "+0.3% vs. last month", "co2_sub_col": "#ef4444",
        "temp": 1.8, "temp_lbl": "+1.8°C", "aqi": 85, "aqi_lbl": "Moderate", "aqi_col": "#eab308",
        "co2_history": [250, 390, 510, 680, 830, 1020, 1420],
        "pm25": [12, 15, 19, 25, 32, 29, 21, 14, 12, 11, 13, 15],
        "temp_list": [18, 19, 22, 26, 29, 28, 27, 26, 25, 23, 20, 18]
    },
    "📌 NORTH (ภาคเหนือ)": {
        "co2": 412.8, "co2_sub": "+0.1% vs. last month", "co2_sub_col": "#10b981",
        "temp": 2.4, "temp_lbl": "+2.4°C", "aqi": 165, "aqi_lbl": "Unhealthy", "aqi_col": "#ef4444",
        "co2_history": [210, 310, 430, 570, 710, 890, 1150],
        "pm25": [45, 68, 95, 120, 75, 30, 22, 19, 24, 38, 48, 55],
        "temp_list": [14, 17, 23, 28, 27, 26, 25, 24, 23, 21, 17, 14]
    }
}

# ==========================================
# 3. TOP TELEMETRY TITLE HEADER
# ==========================================
st.markdown("""
<div style="text-align: center; margin-bottom: 18px;">
    <h1 style="color: #ffffff; font-size: 23px; font-weight: 800; margin: 0; letter-spacing: 0.5px;">INTELLIGENT ENVIRONMENTAL & GHG MONITORING DASHBOARD (THAILAND)</h1>
    <div style="color: #38bdf8; font-size: 13px; font-weight: 700; margin-top: 3px;">แดชบอร์ดอัจฉริยะติดตามก๊าซเรือนกระจกและมลพิษ (ประเทศไทย)</div>
</div>
""", unsafe_allow_html=True)

# ==========================================
# 4. CONTROL BAR FILTERS
# ==========================================
c_bar = st.columns([2.5, 3, 3, 3])
with c_bar[0]:
    st.markdown('<div style="font-family: monospace; font-size: 13px; color: #10b981; font-weight: 800; margin-top: 24px;">⏱️ MARCH 2026 | 13:58:55</div>', unsafe_allow_html=True)
with c_bar[1]:
    sel_reg = st.selectbox("REGION:", list(DATA_SET.keys()))
with c_bar[2]:
    st.selectbox("DATA SOURCE:", ["ALL SYSTEMS INTEGRATED", "SATELLITE BACKBONE"])
with c_bar[3]:
    st.selectbox("TIME:", ["1 MONTH WINDOW", "30 YEARS HISTORICAL"])

st.markdown("<div style='margin-bottom: 12px;'></div>", unsafe_allow_html=True)
ctx = DATA_SET[sel_reg]

# ==========================================
# 5. TIER 1: HIGH-END INFOGRAPHIC GAUGES
# ==========================================
st.markdown('<div class="box-title" style="margin-left:5px;">KEY ENVIRONMENTAL METRICS</div>', unsafe_allow_html=True)
g1, g2, g3 = st.columns(3)

def render_sleek_arc(val, min_v, max_v, arc_color):
    fig = go.Figure(go.Indicator(
        mode="gauge", value=val,
        gauge={
            'axis': {'range': [min_v, max_v], 'visible': False},
            'bar': {'color': arc_color, 'thickness': 0.28},
            'bgcolor': '#1a2333'
        }
    ))
    fig.update_layout(
        height=62, margin=dict(t=0, b=0, l=40, r=40),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)"
    )
    return fig

with g1:
    st.markdown('<div class="premium-box" style="text-align:center; height:140px;">', unsafe_allow_html=True)
    st.markdown('<div style="font-size:10px; font-weight:800; color:#38bdf8; text-align:left;">1 🔵 ATMOSPHERIC CO₂ LEVEL</div>', unsafe_allow_html=True)
    st.plotly_chart(render_sleek_arc(ctx["co2"], 350, 500, "#0284c7"), use_container_width=True, config={'displayModeBar': False})
    st.markdown(f'<div style="font-size:24px; font-weight:800; margin-top:-12px; color:#ffffff;">{ctx["co2"]} <span style="font-size:14px; color:#94a3b8;">ppm</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div style="font-size:10px; font-weight:700; color:{ctx["co2_sub_col"]}; margin-top:-2px;">{ctx["co2_sub"]}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with g2:
    st.markdown('<div class="premium-box" style="text-align:center; height:140px;">', unsafe_allow_html=True)
    st.markdown('<div style="font-size:10px; font-weight:800; color:#f97316; text-align:left;">2 🟠 AV. TEMPERATURE ANOMALY</div>', unsafe_allow_html=True)
    st.plotly_chart(render_sleek_arc(ctx["temp"], 0, 4, "#ea580c"), use_container_width=True, config={'displayModeBar': False})
    st.markdown(f'<div style="font-size:24px; font-weight:800; margin-top:-12px; color:#f97316;">{ctx["temp_lbl"]}</div>', unsafe_allow_html=True)
    st.markdown('<div style="font-size:10px; font-weight:700; color:#94a3b8; margin-top:-2px;">Anomaly Threshold</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with g3:
    st.markdown('<div class="premium-box" style="text-align:center; height:140px;">', unsafe_allow_html=True)
    st.markdown('<div style="font-size:10px; font-weight:800; color:#eab308; text-align:left;">3 🟡 AIR QUALITY INDEX (AQI)</div>', unsafe_allow_html=True)
    st.plotly_chart(render_sleek_arc(ctx["aqi"], 0, 200, ctx["aqi_col"]), use_container_width=True, config={'displayModeBar': False})
    st.markdown(f'<div style="font-size:24px; font-weight:800; margin-top:-12px; color:#ffffff;">{ctx["aqi"]}</div>', unsafe_allow_html=True)
    st.markdown(f'<div style="font-size:10px; font-weight:700; color:{ctx["aqi_col"]}; margin-top:-2px;">{ctx["aqi_lbl"]}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# 6. TIER 2: ORGANIC HEATMAP & TIMELINES
# ==========================================
m_left, m_right = st.columns([1.1, 1.0])

with m_left:
    st.markdown('<div class="premium-box" style="height:325px;">', unsafe_allow_html=True)
    st.markdown('<div class="box-title" style="color:#38bdf8;">GHG & POLLUTION HOTSPOTS (BANGKOK & PERIPHERY)</div>', unsafe_allow_html=True)
    
    grid_size = 100
    x_coords = np.linspace(0, 10, grid_size)
    y_coords = np.linspace(0, 10, grid_size)
    MX, MY = np.meshgrid(x_coords, y_coords)
    MZ = np.exp(-((MX - 5)**2 + (MY - 5)**2) / 5.5) * 170 + np.exp(-((MX - 7.5)**2 + (MY - 3.5)**2) / 1.8) * 90
    
    fig_map = go.Figure(data=go.Contour(
        z=MZ, x=x_coords, y=y_coords,
        colorscale=[[0, '#22c55e'], [0.35, '#eab308'], [0.7, '#ef4444'], [1, '#7f1d1d']],
        showscale=False, line_width=0, contours=dict(coloring='heatmap', smoothing=1.5)
    ))
    
    # ✅ FIX: แก้ไข textfont เป็นคีย์เวิร์ดสากล (family) และใช้ <b> ทำตัวหนา เพื่อกันแอปพังร้อยเปอร์เซ็นต์
    fig_map.add_trace(go.Scatter(
        x=[5, 7.5, 2.0, 1.5], y=[5, 2.5, 3.5, 6.5],
        mode='markers+text',
        text=['<b>🔴 BANGKOK</b>', '<b>SAMUT PRAKAN</b>', '<b>KAMAT</b>', '<b>FANG</b>'],
        textposition='top center',
        textfont=dict(size=9, color='white', family='Inter'),
        marker=dict(color='white', size=4)
    ))
    fig_map.update_layout(
        height=250, margin=dict(t=5, b=5, l=5, r=5),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
    )
    st.plotly_chart(fig_map, use_container_width=True, config={'displayModeBar': False})
    st.markdown('</div>', unsafe_allow_html=True)

with m_right:
    st.markdown('<div class="premium-box" style="height:325px;">', unsafe_allow_html=True)
    st.markdown('<div class="box-title">CHARTS TREND MONITORING</div>', unsafe_allow_html=True)
    
    df_a = pd.DataFrame({'Year': years, 'CO2': ctx["co2_history"]})
    fig_a = px.area(df_a, x='Year', y='CO2')
    fig_a.update_traces(line=dict(color='#38bdf8', width=2, shape='spline'), fillcolor='rgba(56, 189, 248, 0.12)')
    fig_a.update_layout(
        height=110, margin=dict(t=5, b=5, l=10, r=10), template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        title={'text': "<b>30-YEAR CO₂ EMISSIONS TREND (KT/YR)</b>", 'font': {'size': 9, 'color': '#94a3b8', 'family': 'Inter'}},
        xaxis=dict(showgrid=False, tickfont=dict(size=8, color='#64748b')),
        yaxis=dict(showgrid=False, tickfont=dict(size=8, color='#64748b'))
    )
    st.plotly_chart(fig_a, use_container_width=True, config={'displayModeBar': False})
    
    fig_c = make_subplots(specs=[[{"secondary_y": True}]])
    fig_c.add_trace(go.Bar(x=months, y=ctx["pm25"], name='PM2.5', marker_color='#f97316', marker_line_width=0), secondary_y=False)
    fig_c.add_trace(go.Scatter(x=months, y=ctx["temp_list"], name='Temp', line=dict(color='#38bdf8', width=2, shape='spline')), secondary_y=True)
    fig_c.update_layout(
        height=110, margin=dict(t=15, b=5, l=10, r=10), template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", showlegend=False,
        title={'text': "<b>MONTHLY TEMPERATURE VS. AIR QUALITY</b>", 'font': {'size': 9, 'color': '#94a3b8', 'family': 'Inter'}},
        xaxis=dict(showgrid=False, tickfont=dict(size=8, color='#64748b')),
        yaxis=dict(showgrid=False, tickfont=dict(size=8, color='#64748b')),
        yaxis2=dict(showgrid=False, tickfont=dict(size=8, color='#64748b'))
    )
    st.plotly_chart(fig_c, use_container_width=True, config={'displayModeBar': False})
    st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# 7. TIER 3: BREAKDOWN & WAVING WATER REPORTS
# ==========================================
b_left, b_right = st.columns([1.1, 1.0])

with b_left:
    st.markdown('<div class="premium-box" style="height:210px;">', unsafe_allow_html=True)
    st.markdown('<div class="box-title">POLLUTION BREAKDOWN (PM2.5, NO₂, SO₂)</div>', unsafe_allow_html=True)
    
    elems = ['PM2.5', 'PM10', 'NO₂', 'NOx', 'SO₂']
    fig_s = go.Figure()
    fig_s.add_trace(go.Bar(name='Low', x=elems, y=[80, 95, 110, 100, 125], marker_color='#10b981'))
    fig_s.add_trace(go.Bar(name='Moderate', x=elems, y=[65, 55, 45, 50, 40], marker_color='#f59e0b'))
    fig_s.add_trace(go.Bar(name='Unhealthy', x=elems, y=[75, 40, 55, 60, 35], marker_color='#ef4444'))
    
    fig_s.update_layout(
        barmode='stack', height=155, margin=dict(t=5, b=5, l=5, r=5), template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", showlegend=False,
        xaxis=dict(showgrid=False, tickfont=dict(size=9, color='#64748b')),
        yaxis=dict(showgrid=False, tickfont=dict(size=9, color='#64748b'))
    )
    st.plotly_chart(fig_s, use_container_width=True, config={'displayModeBar': False})
    st.markdown('</div>', unsafe_allow_html=True)

with b_right:
    st.markdown('<div class="premium-box" style="height:210px;">', unsafe_allow_html=True)
    st.markdown('<div class="box-title">WATER QUALITY MONITORING (MAJOR RIVERS)</div>', unsafe_allow_html=True)
    
    river_markup = """
    <div style="margin-top: 5px;">
        <div class="river-row">
            <div class="river-name">Chao Phraya</div>
            <svg class="river-svg" viewBox="0 0 100 20" preserveAspectRatio="none">
                <path d="M0,10 Q25,0 50,10 T100,10" fill="none" stroke="#38bdf8" stroke-width="2" />
            </svg>
            <div class="badge-container">
                <span class="status-pill pill-green">DO PASS</span>
                <span class="status-pill pill-red">COD WARN</span>
            </div>
        </div>
        <div class="river-row">
            <div class="river-name">Tha Chin</div>
            <svg class="river-svg" viewBox="0 0 100 20" preserveAspectRatio="none">
                <path d="M0,10 Q25,20 50,10 T100,10" fill="none" stroke="#38bdf8" stroke-width="2" />
            </svg>
            <div class="badge-container">
                <span class="status-pill pill-green">DO PASS</span>
                <span class="status-pill pill-green">DO PASS</span>
            </div>
        </div>
        <div class="river-row">
            <div class="river-name">Mae Klong</div>
            <svg class="river-svg" viewBox="0 0 100 20" preserveAspectRatio="none">
                <path d="M0,10 Q25,5 50,10 T100,10" fill="none" stroke="#38bdf8" stroke-width="2" />
            </svg>
            <div class="badge-container">
                <span class="status-pill pill-green">DO PASS</span>
                <span class="status-pill pill-red">COD WARN</span>
            </div>
        </div>
    </div>
    """
    st.markdown(river_markup, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
