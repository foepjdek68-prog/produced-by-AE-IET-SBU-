import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# 1. SETUP & CONFIGURATION (ล็อกจอ Single-Screen เต็มหน้าจอ)
st.set_page_config(layout="wide", page_title="Dashboard Tracking GHGs Emission", initial_sidebar_state="collapsed")

# 2. ULTRA-CYBER CSS LIGHTING (ถอดรหัสสีและดีไซน์จากภาพต้นฉบับ)
st.markdown("""
    <style>
        ::-webkit-scrollbar { display: none; }
        html, body, [data-testid="stAppViewContainer"] { 
            overflow: hidden !important; 
            height: 100vh !important; 
            background-color: #0b111e !important;
        }
        .block-container { padding: 0.6rem 1.2rem !important; }
        
        /* HEADER BAR */
        .top-header {
            display: flex; justify-content: space-between; align-items: center;
            padding-bottom: 5px; border-bottom: 1px solid #1e293b; margin-bottom: 8px;
        }
        .main-title { font-size: 18px; font-weight: 800; color: #ffffff; letter-spacing: 0.5px; }
        .clock-display { font-family: monospace; font-size: 15px; color: #94a3b8; }
        
        /* SELECTORS */
        .selector-box { display: flex; gap: 15px; margin-bottom: 8px; }
        .selector-label { font-size: 9px; color: #64748b; font-weight: 700; text-transform: uppercase; margin-bottom: 2px; }

        /* PANEL BOX CONTAINER */
        .panel-box {
            background-color: #0f172a; border: 1px solid #1e293b; border-radius: 6px;
            padding: 10px; height: 100%; box-shadow: 0 4px 15px rgba(0,0,0,0.5);
        }
        .panel-header { 
            font-size: 10px; color: #94a3b8; font-weight: 700; 
            text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 5px; 
        }
        
        /* STATIC METRIC CARD */
        .metric-card {
            background: linear-gradient(180deg, #141b2d 0%, #0c101b 100%);
            border: 1px solid #22d3ee22; border-radius: 6px; padding: 8px; height: 80px;
        }
        .metric-label { font-size: 9px; color: #94a3b8; font-weight: 600; }
        .metric-value { font-size: 20px; font-weight: 700; color: #22d3ee; margin-top: 1px; }
        .metric-unit { font-size: 11px; color: #64748b; }
        .metric-sub { font-size: 9px; color: #64748b; margin-top: 1px; }

        div[data-baseweb="select"] { background-color: #1e293b !important; border: 1px solid #334155 !important; border-radius: 4px; }
        div[data-baseweb="select"] * { color: #ffffff !important; font-size: 11px !important; }
    </style>
""", unsafe_allow_html=True)

# 3. ฐานข้อมูลที่สอดคล้องกันอย่างสมบูรณ์ (เปลี่ยนตาม Region และ ชนิดก๊าซที่เลือก)
DATA_BANK = {
    "ภาคกลาง": {
        "co2_gauge": 421.5, "co2_sub": "+0.3% vs last month", "temp": 1.8, "aqi": 85, "aqi_status": "Moderate",
        "ch4": 1919.4, "no2": 330.8, "humid": 64,
        "map_center": [13.7563, 100.5018],
        "co2_30y": [310, 335, 360, 385, 405, 421.5],
        "selected_trend": {
            "CO₂ (ppm)": [310, 335, 360, 385, 405, 421.5],
            "CH₄ (ppb)": [1650, 1710, 1780, 1840, 1890, 1919.4],
            "NO₂ (ppb)": [190, 220, 255, 280, 310, 330.8]
        },
        "stack_data": {'PM2.5': [50, 30, 20], 'PM10': [60, 25, 15], 'NO₂': [40, 35, 25], 'SO₂': [70, 15, 15], 'O₃': [55, 30, 15]},
        "river_do": ["4.2 mg/L", "2.1 mg/L", "5.5 mg/L"], "river_status": ["🟢 Normal", "🔴 Unhealthy", "🟢 Normal"]
    },
    "ภาคเหนือ": {
        "co2_gauge": 415.2, "co2_sub": "+0.1% vs last month", "temp": 2.4, "aqi": 165, "aqi_status": "Unhealthy",
        "ch4": 1850.2, "no2": 120.4, "humid": 42,
        "map_center": [18.7883, 98.9853],
        "co2_30y": [305, 328, 352, 378, 398, 415.2],
        "selected_trend": {
            "CO₂ (ppm)": [305, 328, 352, 378, 398, 415.2],
            "CH₄ (ppb)": [1610, 1660, 1720, 1770, 1810, 1850.2],
            "NO₂ (ppb)": [60, 75, 90, 105, 115, 120.4]
        },
        "stack_data": {'PM2.5': [20, 30, 80], 'PM10': [30, 40, 50], 'NO₂': [70, 20, 10], 'SO₂': [85, 10, 5], 'O₃': [40, 40, 20]},
        "river_do": ["5.8 mg/L", "4.5 mg/L", "6.1 mg/L"], "river_status": ["🟢 Normal", "🟢 Normal", "🟢 Normal"]
    },
    "ภาคใต้": {
        "co2_gauge": 408.9, "co2_sub": "-0.2% vs last month", "temp": 0.9, "aqi": 32, "aqi_status": "Good",
        "ch4": 1795.7, "no2": 45.1, "humid": 82,
        "map_center": [7.8804, 98.3923],
        "co2_30y": [300, 320, 345, 370, 390, 408.9],
        "selected_trend": {
            "CO₂ (ppm)": [300, 320, 345, 370, 390, 408.9],
            "CH₄ (ppb)": [1580, 1620, 1670, 1710, 1760, 1795.7],
            "NO₂ (ppb)": [20, 25, 30, 35, 40, 45.1]
        },
        "stack_data": {'PM2.5': [85, 10, 5], 'PM10': [90, 8, 2], 'NO₂': [95, 4, 1], 'SO₂': [90, 8, 2], 'O₃': [80, 15, 5]},
        "river_do": ["6.5 mg/L", "5.9 mg/L", "6.2 mg/L"], "river_status": ["🟢 Normal", "🟢 Normal", "🟢 Normal"]
    }
}

# 4. TOP BAR CONTROL (แผงควบคุมด้านบนขนานกันตามรูปภาพ)
st.markdown("""
<div class="top-header">
    <div class="main-title">DASHBOARD “TRACKING GHGs EMISSION”</div>
    <div class="clock-display">MARCH 2026 | 13:58:55</div>
</div>
""", unsafe_allow_html=True)

col_sel1, col_sel2, col_sel_blank = st.columns([2.0, 2.0, 8.0])
with col_sel1:
    st.markdown('<div class="selector-label">REGION (ภูมิภาค)</div>', unsafe_allow_html=True)
    selected_region = st.selectbox("Region", list(DATA_BANK.keys()), label_visibility="collapsed")
with col_sel2:
    st.markdown('<div class="selector-label">METRIC (ตัวชี้วัดก๊าซหลักที่ต้องการตรวจสอบ)</div>', unsafe_allow_html=True)
    selected_metric = st.selectbox("Metric", ["CO₂ (ppm)", "CH₄ (ppb)", "NO₂ (ppb)"], label_visibility="collapsed")

# ดึงชุดข้อมูลที่ผูกไว้มาใช้งาน
db = DATA_BANK[selected_region]

# กำหนด Dynamic Value สำหรับเกจวัดตัวแรกสุด ให้เปลี่ยนตาม Metric ที่เลือกด้านบนจริง ๆ 
metric_key = selected_metric.split(" ")[0] # แยกเอาเฉพาะชื่อ CO2, CH4, NO2
current_gauge_val = db["ch4"] if metric_key == "CH₄" else db["no2"] if metric_key == "NO₂" else db["co2_gauge"]
gauge_max = 2000 if metric_key == "CH₄" else 400 if metric_key == "NO₂" else 450
gauge_min = 1500 if metric_key == "CH₄" else 0 if metric_key == "NO₂" else 390

# --- 5. SECTION 1: KEY ENVIRONMENTAL METRICS (แผงเกจ 3 ตัว + การ์ด 3 ตัว ด้านบน) ---
st.markdown("<div style='margin-bottom: 5px;'></div>", unsafe_allow_html=True)
m_col1, m_col2, m_col3, m_col4, m_col5, m_col6 = st.columns(6)

# กล่องที่ 1: เปลี่ยนค่าและชื่อตัวแปรตาม Dropdown Metric ด้านบน 100%
with m_col1:
    fig_g1 = go.Figure(go.Indicator(
        mode="gauge+number", value=current_gauge_val,
        number={'suffix': f" {selected_metric.split(' ')[1]}", 'font': {'size': 16, 'color': '#ffffff'}},
        gauge={'axis': {'range': [gauge_min, gauge_max], 'tickwidth': 1}, 'bar': {'color': "#22d3ee"}},
        title={'text': f"1 ATMOSPHERIC {metric_key} LEVEL", 'font': {'size': 8, 'color': '#94a3b8', 'weight': 'bold'}}
    ))
    fig_g1.update_layout(height=80, margin=dict(t=20, b=5, l=10, r=10), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    st.markdown('<div class="panel-box">', unsafe_allow_html=True)
    st.plotly_chart(fig_g1, use_container_width=True, config={'displayModeBar': False})
    st.markdown(f'<div style="text-align:center; font-size:9px; color:#10b981; margin-top:-5px;">{db["co2_sub"]}</div></div>', unsafe_allow_html=True)

# กล่องที่ 2: Av. Temperature Anomaly
with m_col2:
    fig_g2 = go.Figure(go.Indicator(
        mode="gauge+number", value=db["temp"],
        number={'prefix': "+", 'suffix': " °C", 'font': {'size': 16, 'color': '#f97316'}},
        gauge={'axis': {'range': [0, 4], 'tickwidth': 1}, 'bar': {'color': "#f97316"}},
        title={'text': "2 AV. TEMPERATURE ANOMALY", 'font': {'size': 8, 'color': '#94a3b8', 'weight': 'bold'}}
    ))
    fig_g2.update_layout(height=80, margin=dict(t=20, b=5, l=10, r=10), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    st.markdown('<div class="panel-box">', unsafe_allow_html=True)
    st.plotly_chart(fig_g2, use_container_width=True, config={'displayModeBar': False})
    st.markdown('<div style="text-align:center; font-size:9px; color:#f97316; margin-top:-5px;">Above Baseline</div></div>', unsafe_allow_html=True)

# กล่องที่ 3: Air Quality Index (AQI)
with m_col3:
    aqi_color = "#10b981" if db["aqi"] < 50 else "#eab308" if db["aqi"] <= 100 else "#ef4444"
    fig_g3 = go.Figure(go.Indicator(
        mode="gauge+number", value=db["aqi"],
        number={'font': {'size': 16, 'color': aqi_color}},
        gauge={'axis': {'range': [0, 200], 'tickwidth': 1}, 'bar': {'color': aqi_color}},
        title={'text': "3 AIR QUALITY INDEX (AQI)", 'font': {'size': 8, 'color': '#94a3b8', 'weight': 'bold'}}
    ))
    fig_g3.update_layout(height=80, margin=dict(t=20, b=5, l=10, r=10), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    st.markdown('<div class="panel-box">', unsafe_allow_html=True)
    st.plotly_chart(fig_g3, use_container_width=True, config={'displayModeBar': False})
    st.markdown(f'<div style="text-align:center; font-size:9px; color:{aqi_color}; margin-top:-5px;">{db["aqi_status"]}</div></div>', unsafe_allow_html=True)

# กล่องที่ 4: CH4 Concentration
with m_col4:
    st.markdown(f'<div class="metric-card"><div class="metric-label">1 CH₄ CONCENTRATION</div><div class="metric-value">{db["ch4"]} <span class="metric-unit">ppb</span></div><div class="metric-sub">from station 1</div></div>', unsafe_allow_html=True)

# กล่องที่ 5: NO2 Level
with m_col5:
    st.markdown(f'<div class="metric-card"><div class="metric-label">2 NO₂ LEVEL</div><div class="metric-value" style="color:#60a5fa;">{db["no2"]} <span class="metric-unit">ppb</span></div><div class="metric-sub">traffic emissions</div></div>', unsafe_allow_html=True)

# กล่องที่ 6: Humidity
with m_col6:
    st.markdown(f'<div class="metric-card"><div class="metric-label">3 HUMIDITY</div><div class="metric-value" style="color:#f43f5e;">{db["humid"]}<span class="metric-unit">%</span></div><div class="metric-sub">Relative</div></div>', unsafe_allow_html=True)


# --- 6. SECTION 2: MIDDLE VISUALIZATION (แบ่งช่องเป็น แผนที่ | กราฟ CO2 ยืนพื้น | กราฟสลับตามตัวแกรเลือก) ---
st.markdown("<div style='margin-bottom: 8px;'></div>", unsafe_allow_html=True)
layout_col1, layout_col2, layout_col3, layout_col4 = st.columns([1.1, 0.9, 0.9, 1.1])

# ฝั่งซ้ายสุด: แผนที่ความร้อนระบุพิกัดมลพิษสะสม
with layout_col1:
    st.markdown('<div class="panel-box">', unsafe_allow_html=True)
    st.markdown("<div class='panel-header'>GHG & POLLUTION HOTSPOTS</div>", unsafe_allow_html=True)
    np.random.seed(42)
    c_lat, c_lon = db["map_center"]
    map_df = pd.DataFrame({
        'lat': [c_lat + np.random.uniform(-0.06, 0.06) for _ in range(12)],
        'lon': [c_lon + np.random.uniform(-0.06, 0.06) for _ in range(12)],
        'intensity': np.random.randint(60, 140, 12)
    })
    fig_map = px.density_mapbox(map_df, lat='lat', lon='lon', z='intensity', radius=25, center=dict(lat=c_lat, lon=c_lon), zoom=9, mapbox_style="carto-darkmatter")
    fig_map.update_layout(height=240, margin=dict(t=0, b=0, l=0, r=0), paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig_map, use_container_width=True, config={'displayModeBar': False})
    st.markdown('</div>', unsafe_allow_html=True)

# 📊 ฝั่งกลางตัวที่ 1: กราฟเส้นแสดงสถิติ CO2 ย้อนหลัง 30 ปี ยืนพื้นตายตัว (ตามแบบซ้ายมือในรูปภาพ)
with layout_col2:
    st.markdown('<div class="panel-box">', unsafe_allow_html=True)
    st.markdown("<div class='panel-header'>30-YEAR CO₂ EMISSIONS TREND (KT/YR)</div>", unsafe_allow_html=True)
    years_x = [1930, 1950, 1970, 1990, 2010, 2026]
    fig_co2_trend = px.area(pd.DataFrame({'Year': years_x, 'CO2': db["co2_30y"]}), x='Year', y='CO2', template="plotly_dark")
    fig_co2_trend.update_traces(line_color='#22d3ee', fillcolor='rgba(34, 211, 238, 0.06)', mode='lines+markers')
    fig_co2_trend.update_layout(height=240, margin=dict(t=10, b=5, l=5, r=5), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.03)'))
    st.plotly_chart(fig_co2_trend, use_container_width=True, config={'displayModeBar': False})
    st.markdown('</div>', unsafe_allow_html=True)

# 🛠️ 📊 ฝั่งกลางตัวที่ 2: กราฟเส้นที่เปลี่ยนไปตามค่าสาร Metric ที่กดเลือกด้านบน (ตามแบบขวามือในรูปภาพ)
with layout_col3:
    st.markdown('<div class="panel-box">', unsafe_allow_html=True)
    st.markdown(f"<div class='panel-header'>30-YEAR {metric_key} DYNAMIC TREND</div>", unsafe_allow_html=True)
    dynamic_y = db["selected_trend"][selected_metric] # ดึงอาร์เรย์ตามค่าก๊าซที่เลือกจริง
    fig_dyn_trend = px.area(pd.DataFrame({'Year': years_x, 'Value': dynamic_y}), x='Year', y='Value', template="plotly_dark")
    fig_dyn_trend.update_traces(line_color='#60a5fa', fillcolor='rgba(96, 165, 250, 0.06)', mode='lines+markers')
    fig_dyn_trend.update_layout(height=240, margin=dict(t=10, b=5, l=5, r=5), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.03)'))
    st.plotly_chart(fig_dyn_trend, use_container_width=True, config={'displayModeBar': False})
    st.markdown('</div>', unsafe_allow_html=True)

# ฝั่งขวาสุด: กราฟแท่งเปรียบเทียบอากาศรายเดือน
with layout_col4:
    st.markdown('<div class="panel-box">', unsafe_allow_html=True)
    st.markdown("<div class='panel-header'>MONTHLY TEMPERATURE VS. AIR QUALITY</div>", unsafe_allow_html=True)
    months = ['Jan', 'Mar', 'May', 'Jul', 'Sep', 'Nov']
    monthly_aqi = [max(10, v) for v in [db["aqi"]+20, db["aqi"], db["aqi"]-30, db["aqi"]-40, db["aqi"]-10, db["aqi"]+15]]
    fig_bar = px.bar(x=months, y=monthly_aqi, template="plotly_dark")
    fig_bar.update_traces(marker_color='#f97316', opacity=0.85)
    fig_bar.update_layout(height=240, margin=dict(t=10, b=5, l=5, r=5), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.03)'))
    st.plotly_chart(fig_bar, use_container_width=True, config={'displayModeBar': False})
    st.markdown('</div>', unsafe_allow_html=True)


# --- 7. SECTION 3: BOTTOM PANELS (สัดส่วนสารมลพิษย่อยแยกสี และ ตารางคุณภาพลุ่มน้ำ) ---
st.markdown("<div style='margin-bottom: 8px;'></div>", unsafe_allow_html=True)
bottom_col1, bottom_col2, bottom_col3 = st.columns([1.1, 0.9, 2.0])

# ด้านล่างซ้าย: POLLUTION BREAKDOWN (Stacked Bar แยกสี 3 ระดับตามภาพต้นฉบับ)
with bottom_col1:
    st.markdown('<div class="panel-box">', unsafe_allow_html=True)
    st.markdown("<div class='panel-header'>POLLUTION BREAKDOWN</div>", unsafe_allow_html=True)
    s_data = db["stack_data"]
    comp_list = list(s_data.keys())
    fig_stack = go.Figure(data=[
        go.Bar(name='Low', x=comp_list, y=[s_data[c][0] for c in comp_list], marker_color='#10b981'),
        go.Bar(name='Moderate', x=comp_list, y=[s_data[c][1] for c in comp_list], marker_color='#eab308'),
        go.Bar(name='Unhealthy', x=comp_list, y=[s_data[c][2] for c in comp_list], marker_color='#ef4444')
    ])
    fig_stack.update_layout(barmode='stack', height=130, margin=dict(t=5, b=5, l=5, r=5), template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", showlegend=False, xaxis=dict(showgrid=False), yaxis=dict(showgrid=False))
    st.plotly_chart(fig_stack, use_container_width=True, config={'displayModeBar': False})
    st.markdown('</div>', unsafe_allow_html=True)

# ด้านล่างกลาง: POLLUTION BREAKDOWN ตัวที่สองคู่ขนานกันตามรูป
with bottom_col2:
    st.markdown('<div class="panel-box">', unsafe_allow_html=True)
    st.markdown("<div class='panel-header'>POLLUTION BREAKDOWN (CRITERIA)</div>", unsafe_allow_html=True)
    fig_stack2 = go.Figure(data=[
        go.Bar(name='Low', x=comp_list, y=[s_data[c][1] for c in comp_list], marker_color='#10b981'),
        go.Bar(name='Moderate', x=comp_list, y=[s_data[c][2] for c in comp_list], marker_color='#eab308'),
        go.Bar(name='Unhealthy', x=comp_list, y=[s_data[c][0] for c in comp_list], marker_color='#ef4444')
    ])
    fig_stack2.update_layout(barmode='stack', height=130, margin=dict(t=5, b=5, l=5, r=5), template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", showlegend=False, xaxis=dict(showgrid=False), yaxis=dict(showgrid=False))
    st.plotly_chart(fig_stack2, use_container_width=True, config={'displayModeBar': False})
    st.markdown('</div>', unsafe_allow_html=True)

# ด้านล่างขวาสุด: WATER QUALITY MONITORING (ตารางแม่น้ำสายหลัก)
with bottom_col3:
    st.markdown('<div class="panel-box">', unsafe_allow_html=True)
    st.markdown("<div class='panel-header'>WATER QUALITY MONITORING (MAJOR RIVERS)</div>", unsafe_allow_html=True)
    river_df = pd.DataFrame({
        'River Station': ['Chao Phraya', 'Tha Chin', 'Mae Klong'],
        'DO Level': db["river_do"],
        'COD Level': ['🔴 High COD' if '🔴' in s else '🟢 Low COD' for s in db["river_status"]],
        'Status Evaluation': db["river_status"]
    })
    st.dataframe(river_df, hide_index=True, use_container_width=True, height=125)
    st.markdown('</div>', unsafe_allow_html=True)
