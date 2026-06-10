import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# 1. SETUP & CONFIGURATION
st.set_page_config(layout="wide", page_title="Intelligent Environmental Dashboard", initial_sidebar_state="collapsed")

# 2. ADVANCED CYBER CSS STYLING
st.markdown("""
    <style>
        ::-webkit-scrollbar { display: none; }
        html, body, [data-testid="stAppViewContainer"] { 
            overflow: hidden !important; 
            height: 100vh !important; 
            background-color: #0b111e !important;
        }
        .block-container { padding: 0.5rem 1.0rem !important; }
        
        .top-header {
            display: flex; justify-content: space-between; align-items: center;
            padding-bottom: 5px; border-bottom: 1px solid #1e293b; margin-bottom: 6px;
        }
        .main-title { font-size: 16px; font-weight: 800; color: #ffffff; letter-spacing: 0.5px; }
        .clock-display { font-family: monospace; font-size: 13px; color: #94a3b8; }
        
        .selector-label { font-size: 9px; color: #64748b; font-weight: 700; text-transform: uppercase; margin-bottom: 2px; }

        .panel-box {
            background-color: #0f172a; border: 1px solid #1e293b; border-radius: 6px;
            padding: 8px; height: 100%; box-shadow: 0 4px 15px rgba(0,0,0,0.5);
        }
        .panel-header { 
            font-size: 9px; color: #94a3b8; font-weight: 700; 
            text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 4px; 
        }
        
        .metric-card {
            background: linear-gradient(180deg, #141b2d 0%, #0c101b 100%);
            border: 1px solid #22d3ee22; border-radius: 6px; padding: 6px; height: 75px;
        }
        .metric-label { font-size: 8px; color: #94a3b8; font-weight: 600; }
        .metric-value { font-size: 18px; font-weight: 700; color: #22d3ee; margin-top: 1px; }
        .metric-unit { font-size: 10px; color: #64748b; }
        .metric-sub { font-size: 8px; color: #64748b; margin-top: 1px; }

        div[data-baseweb="select"] { background-color: #1e293b !important; border: 1px solid #334155 !important; border-radius: 4px; }
        div[data-baseweb="select"] * { color: #ffffff !important; font-size: 11px !important; }
    </style>
""", unsafe_allow_html=True)

# 3. REALISTIC DATA BANK (ปรับปรุงข้อมูลให้มีความโค้งมนและผันผวนตามธรรมชาติ)
years_x = [1930, 1950, 1970, 1990, 2000, 2010, 2026]

DATA_BANK = {
    "CENTRAL": {
        "co2_gauge": 421.5, "temp": 1.8, "aqi": 85, "aqi_status": "Moderate",
        "ch4": 1919.4, "no2": 330.8, "humid": 64, "co": 1.2, "so2": 4.5, "o3": 35.0,
        "map_center": [13.7563, 100.5018],
        # ดัดแปลงทิศทางข้อมูลให้มีส่วนโค้งเว้า ไม่เป็นเส้นตรงทื่อ
        "co2_30y": [285, 310, 325, 354, 369, 389, 421.5], 
        "selected_trend": {
            "CO₂ (ppm)": [285, 310, 325, 354, 369, 389, 421.5],
            "CH₄ (ppb)": [1610, 1680, 1720, 1790, 1815, 1855, 1919.4],
            "NO₂ (ppb)": [140, 185, 210, 265, 290, 315, 330.8]
        },
        "stack_data": {'PM2.5': [45, 35, 20], 'PM10': [55, 30, 15], 'NO₂': [40, 35, 25], 'SO₂': [75, 15, 10], 'CO': [60, 30, 10]}
    },
    "NORTH": {
        "co2_gauge": 415.2, "temp": 2.4, "aqi": 165, "aqi_status": "Unhealthy",
        "ch4": 1850.2, "no2": 120.4, "humid": 42, "co": 2.1, "so2": 1.8, "o3": 58.0,
        "map_center": [18.7883, 98.9853],
        "co2_30y": [285, 308, 320, 348, 362, 382, 415.2],
        "selected_trend": {
            "CO₂ (ppm)": [285, 308, 320, 348, 362, 382, 415.2],
            "CH₄ (ppb)": [1580, 1630, 1690, 1740, 1770, 1810, 1850.2],
            "NO₂ (ppb)": [50, 65, 80, 95, 105, 112, 120.4]
        },
        "stack_data": {'PM2.5': [15, 25, 60], 'PM10': [25, 35, 40], 'NO₂': [65, 25, 10], 'SO₂': [85, 10, 5], 'CO': [50, 30, 20]}
    }
}

# 4. CONTROL PANEL
st.markdown("""
<div class="top-header">
    <div class="main-title">INTELLIGENT ENVIRONMENTAL & GHG MONITORING DASHBOARD (THAILAND)</div>
    <div class="clock-display">MARCH 2026 | 13:58:55</div>
</div>
""", unsafe_allow_html=True)

col_sel1, col_sel2, col_sel_blank = st.columns([2.0, 2.5, 7.5])
with col_sel1:
    st.markdown('<div class="selector-label">REGION (เลือกภูมิภาค)</div>', unsafe_allow_html=True)
    selected_region = st.selectbox("Region", list(DATA_BANK.keys()), label_visibility="collapsed")
with col_sel2:
    st.markdown('<div class="selector-label">DATA SOURCE METRIC (ตัวชี้วัดก๊าซหลัก)</div>', unsafe_allow_html=True)
    selected_metric = st.selectbox("Metric", ["CO₂ (ppm)", "CH₄ (ppb)", "NO₂ (ppb)"], label_visibility="collapsed")

db = DATA_BANK[selected_region]
metric_key = selected_metric.split(" ")[0]

# คำนวณหาค่า Dynamic เพื่อนำไปเปลี่ยนสเกลและตัวเลขบนหน้าจอให้สัมพันธ์กันทั้งหมด
current_gauge_val = db["ch4"] if metric_key == "CH₄" else db["no2"] if metric_key == "NO₂" else db["co2_gauge"]
gauge_max = 2000 if metric_key == "CH₄" else 400 if metric_key == "NO₂" else 450
gauge_min = 1500 if metric_key == "CH₄" else 0 if metric_key == "NO₂" else 250

# --- 5. SECTION 1: KEY ENVIRONMENTAL METRICS ---
m_col1, m_col2, m_col3, m_col4, m_col5, m_col6 = st.columns(6)

with m_col1:
    fig_g1 = go.Figure(go.Indicator(
        mode="gauge+number", value=current_gauge_val,
        number={'suffix': f" {selected_metric.split(' ')[1]}", 'font': {'size': 15, 'color': '#ffffff'}},
        gauge={'axis': {'range': [gauge_min, gauge_max], 'tickwidth': 1, 'tickcolor': '#334155'}, 'bar': {'color': "#22d3ee"}},
        title={'text': f"1 ATMOSPHERIC {metric_key} LEVEL", 'font': {'size': 8, 'color': '#94a3b8', 'weight': 'bold'}}
    ))
    fig_g1.update_layout(height=75, margin=dict(t=20, b=5, l=10, r=10), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    st.markdown('<div class="panel-box">', unsafe_allow_html=True)
    st.plotly_chart(fig_g1, use_container_width=True, config={'displayModeBar': False})
    st.markdown(f'<div style="text-align:center; font-size:8px; color:#10b981; margin-top:-6px;">+0.3% vs last month</div></div>', unsafe_allow_html=True)

with m_col2:
    fig_g2 = go.Figure(go.Indicator(
        mode="gauge+number", value=db["temp"],
        number={'prefix': "+", 'suffix': " °C", 'font': {'size': 15, 'color': '#f97316'}},
        gauge={'axis': {'range': [0, 4], 'tickwidth': 1}, 'bar': {'color': "#f97316"}},
        title={'text': "2 AV. TEMPERATURE ANOMALY", 'font': {'size': 8, 'color': '#94a3b8', 'weight': 'bold'}}
    ))
    fig_g2.update_layout(height=75, margin=dict(t=20, b=5, l=10, r=10), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    st.markdown('<div class="panel-box">', unsafe_allow_html=True)
    st.plotly_chart(fig_g2, use_container_width=True, config={'displayModeBar': False})
    st.markdown('<div style="text-align:center; font-size:8px; color:#f97316; margin-top:-6px;">Above Baseline</div></div>', unsafe_allow_html=True)

with m_col3:
    aqi_color = "#10b981" if db["aqi"] < 50 else "#eab308" if db["aqi"] <= 100 else "#ef4444"
    fig_g3 = go.Figure(go.Indicator(
        mode="gauge+number", value=db["aqi"],
        number={'font': {'size': 15, 'color': aqi_color}},
        gauge={'axis': {'range': [0, 200], 'tickwidth': 1}, 'bar': {'color': aqi_color}},
        title={'text': "3 AIR QUALITY INDEX (AQI)", 'font': {'size': 8, 'color': '#94a3b8', 'weight': 'bold'}}
    ))
    fig_g3.update_layout(height=75, margin=dict(t=20, b=5, l=10, r=10), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    st.markdown('<div class="panel-box">', unsafe_allow_html=True)
    st.plotly_chart(fig_g3, use_container_width=True, config={'displayModeBar': False})
    st.markdown(f'<div style="text-align:center; font-size:8px; color:{aqi_color}; margin-top:-6px;">{db["aqi_status"]}</div></div>', unsafe_allow_html=True)

with m_col4:
    st.markdown(f'<div class="metric-card"><div class="metric-label">1 CH₄ CONCENTRATION</div><div class="metric-value">{db["ch4"]} <span class="metric-unit">ppb</span></div><div class="metric-sub">from station 1</div></div>', unsafe_allow_html=True)
with m_col5:
    st.markdown(f'<div class="metric-card"><div class="metric-label">2 NO₂ LEVEL</div><div class="metric-value" style="color:#60a5fa;">{db["no2"]} <span class="metric-unit">ppb</span></div><div class="metric-sub">PCD Air4Thai</div></div>', unsafe_allow_html=True)
with m_col6:
    st.markdown(f'<div class="metric-card"><div class="metric-label">3 CARBON MONOXIDE (CO)</div><div class="metric-value" style="color:#f43f5e;">{db["co"]}<span class="metric-unit"> ppm</span></div><div class="metric-sub">Sensor Validation</div></div>', unsafe_allow_html=True)

# --- 6. SECTION 2: MIDDLE VISUALIZATION ---
st.markdown("<div style='margin-bottom: 6px;'></div>", unsafe_allow_html=True)
layout_col1, layout_col2, layout_col3, layout_col4 = st.columns([1.2, 0.9, 0.9, 1.0])

# แผนที่ความร้อน
with layout_col1:
    st.markdown('<div class="panel-box">', unsafe_allow_html=True)
    st.markdown("<div class='panel-header'>GHG & POLLUTION HOTSPOTS</div>", unsafe_allow_html=True)
    np.random.seed(10)
    c_lat, c_lon = db["map_center"]
    map_df = pd.DataFrame({
        'lat': [c_lat + np.random.uniform(-0.05, 0.05) for _ in range(15)],
        'lon': [c_lon + np.random.uniform(-0.05, 0.05) for _ in range(15)],
        'intensity': np.random.randint(50, 150, 15)
    })
    fig_map = px.density_mapbox(map_df, lat='lat', lon='lon', z='intensity', radius=22, center=dict(lat=c_lat, lon=c_lon), zoom=9, mapbox_style="carto-darkmatter")
    fig_map.update_layout(height=230, margin=dict(t=0, b=0, l=0, r=0), paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig_map, use_container_width=True, config={'displayModeBar': False})
    st.markdown('</div>', unsafe_allow_html=True)

# กราฟเส้นที่ 1: CO2 ยืนพื้น (ปรับแต่งเส้นกราฟให้มีความผันผวนสมจริง ไม่เป็นเส้นตรง)
with layout_col2:
    st.markdown('<div class="panel-box">', unsafe_allow_html=True)
    st.markdown("<div class='panel-header'>30-YEAR CO₂ EMISSIONS TREND (KT/YR)</div>", unsafe_allow_html=True)
    df_co2 = pd.DataFrame({'Year': years_x, 'CO2': db["co2_30y"]})
    fig_co2_trend = px.area(df_co2, x='Year', y='CO2', template="plotly_dark")
    fig_co2_trend.update_traces(line=dict(color='#22d3ee', width=2), fillcolor='rgba(34, 211, 238, 0.05)', mode='lines+markers')
    fig_co2_trend.update_layout(height=230, margin=dict(t=10, b=5, l=5, r=5), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                                xaxis=dict(showgrid=False, title="Year"), yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.03)', title="CO2 Level"))
    st.plotly_chart(fig_co2_trend, use_container_width=True, config={'displayModeBar': False})
    st.markdown('</div>', unsafe_allow_html=True)

# กราฟเส้นที่ 2: Dynamic Trend ตามที่เลือกสาร (ผันผวนสมจริง)
with layout_col3:
    st.markdown('<div class="panel-box">', unsafe_allow_html=True)
    st.markdown(f"<div class='panel-header'>30-YEAR {metric_key} DYNAMIC TREND</div>", unsafe_allow_html=True)
    dynamic_y = db["selected_trend"][selected_metric]
    df_dyn = pd.DataFrame({'Year': years_x, 'Value': dynamic_y})
    fig_dyn_trend = px.area(df_dyn, x='Year', y='Value', template="plotly_dark")
    fig_dyn_trend.update_traces(line=dict(color='#60a5fa', width=2), fillcolor='rgba(96, 165, 250, 0.05)', mode='lines+markers')
    fig_dyn_trend.update_layout(height=230, margin=dict(t=10, b=5, l=5, r=5), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                                xaxis=dict(showgrid=False, title="Year"), yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.03)', title=metric_key))
    st.plotly_chart(fig_dyn_trend, use_container_width=True, config={'displayModeBar': False})
    st.markdown('</div>', unsafe_allow_html=True)

# กราฟแท่งคู่ขนานแสดงผลครบ 12 เดือน (Temperature vs. PM2.5) แก้ไขชื่อแกน x, y ที่เพี้ยนให้ถูกต้อง
with layout_col4:
    st.markdown('<div class="panel-box">', unsafe_allow_html=True)
    st.markdown("<div class='panel-header'>MONTHLY TEMPERATURE VS. AIR QUALITY</div>", unsafe_allow_html=True)
    months_12 = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    
    # ดึงค่าจำลองสถิติที่ล้อตามค่าจริงของภูมิภาค
    temp_line = [24, 26, 29, 31, 30, 29, 28, 28, 28, 27, 26, 24] if selected_region == "CENTRAL" else [20, 23, 27, 30, 29, 28, 27, 27, 26, 25, 22, 19]
    pm25_bar = [45, 55, 65, 40, 25, 18, 15, 16, 20, 28, 35, 42] if selected_region == "CENTRAL" else [70, 95, 140, 85, 30, 15, 12, 14, 18, 22, 40, 55]

    fig_mix = go.Figure()
    fig_mix.add_trace(go.Bar(x=months_12, y=pm25_bar, name='PM2.5 (µg/m³)', marker_color='#f97316', opacity=0.85, yaxis='y1'))
    fig_mix.add_trace(go.Scatter(x=months_12, y=temp_line, name='Temp (°C)', line=dict(color='#22d3ee', width=2), yaxis='y2'))
    
    fig_mix.update_layout(
        height=230, margin=dict(t=15, b=5, l=5, r=5), template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
        xaxis=dict(showgrid=False, title="Months"),
        yaxis=dict(title="PM2.5", showgrid=True, gridcolor='rgba(255,255,255,0.03)'),
        yaxis2=dict(title="Temp (°C)", overlaying='y', side='right', showgrid=False)
    )
    st.plotly_chart(fig_mix, use_container_width=True, config={'displayModeBar': False})
    st.markdown('</div>', unsafe_allow_html=True)

# --- 7. SECTION 3: BOTTOM PANELS (สอดคล้องตามลำดับข้อตกลง Flowchart) ---
st.markdown("<div style='margin-bottom: 6px;'></div>", unsafe_allow_html=True)
bottom_col1, bottom_col2, bottom_col3 = st.columns([1.1, 0.9, 2.0])

with bottom_col1:
    st.markdown('<div class="panel-box">', unsafe_allow_html=True)
    st.markdown("<div class='panel-header'>POLLUTION BREAKDOWN (GHG & PM CRITERIA)</div>", unsafe_allow_html=True)
    s_data = db["stack_data"]
    comp_list = list(s_data.keys())
    fig_stack = go.Figure(data=[
        go.Bar(name='LOW', x=comp_list, y=[s_data[c][0] for c in comp_list], marker_color='#10b981'),
        go.Bar(name='MODERATE', x=comp_list, y=[s_data[c][1] for c in comp_list], marker_color='#eab308'),
        go.Bar(name='UNHEALTHY', x=comp_list, y=[s_data[c][2] for c in comp_list], marker_color='#ef4444')
    ])
    fig_stack.update_layout(barmode='stack', height=125, margin=dict(t=5, b=5, l=5, r=5), template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", showlegend=False, xaxis=dict(showgrid=False), yaxis=dict(showgrid=False))
    st.plotly_chart(fig_stack, use_container_width=True, config={'displayModeBar': False})
    st.markdown('</div>', unsafe_allow_html=True)

with bottom_col2:
    st.markdown('<div class="panel-box">', unsafe_allow_html=True)
    st.markdown("<div class='panel-header'>STATION CRITICAL VALIDATION</div>", unsafe_allow_html=True)
    fig_stack2 = go.Figure(data=[
        go.Bar(name='LOW', x=comp_list, y=[s_data[c][1] for c in comp_list], marker_color='#10b981'),
        go.Bar(name='MODERATE', x=comp_list, y=[s_data[c][2] for c in comp_list], marker_color='#eab308'),
        go.Bar(name='UNHEALTHY', x=comp_list, y=[s_data[c][0] for c in comp_list], marker_color='#ef4444')
    ])
    fig_stack2.update_layout(barmode='stack', height=125, margin=dict(t=5, b=5, l=5, r=5), template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", showlegend=False, xaxis=dict(showgrid=False), yaxis=dict(showgrid=False))
    st.plotly_chart(fig_stack2, use_container_width=True, config={'displayModeBar': False})
    st.markdown('</div>', unsafe_allow_html=True)

with bottom_col3:
    st.markdown('<div class="panel-box">', unsafe_allow_html=True)
    st.markdown("<div class='panel-header'>METEOROLOGICAL DATA INPUT ANALYSIS (TMD & AIR4THAI)</div>", unsafe_allow_html=True)
    river_df = pd.DataFrame({
        'Parameters Source': ['Air4Thai API (PCD)', 'TMD Meteorology', 'Sentinel-5P Satellite', 'OpenAQ Global API'],
        'CO / NO2 Level': [f"{db['co']} ppm", f"{db['no2']} ppb", "Heatmap Detected", "Backup Validated"],
        'SO2 / O3 Evaluation': [f"{db['so2']} ppb", "Wind Speed Verification", f"{db['o3']} ppb", "Cross-checked"],
        'System Status': ["🟢 Active & Syncing", "🟢 Active", "🟢 Processing", "🟡 Standby Mode"]
    })
    st.dataframe(river_df, hide_index=True, use_container_width=True, height=120)
    st.markdown('</div>', unsafe_allow_html=True)
