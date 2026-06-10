import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# 1. SETUP & CONFIGURATION
st.set_page_config(layout="wide", page_title="Dashboard Tracking GHGs Emission", initial_sidebar_state="collapsed")

# 2. ADVANCED CSS (ล็อก Layout Single-Screen คุมโทนสีตามต้นฉบับ)
st.markdown("""
    <style>
        ::-webkit-scrollbar { display: none; }
        html, body, [data-testid="stAppViewContainer"] { 
            overflow: hidden !important; 
            height: 100vh !important; 
            background-color: #0b0f19 !important;
        }
        .block-container { padding: 0.8rem 1.5rem !important; }
        .top-header {
            display: flex; justify-content: space-between; align-items: center;
            padding-bottom: 8px; border-bottom: 1px solid #1e293b; margin-bottom: 12px;
        }
        .main-title { font-size: 20px; font-weight: 800; color: #ffffff; letter-spacing: 0.5px; }
        .clock-display { font-family: monospace; font-size: 16px; color: #94a3b8; font-weight: 700; }
        .selector-label { font-size: 10px; color: #64748b; font-weight: 700; text-transform: uppercase; margin-bottom: 2px; }
        .panel-box {
            background-color: #0f172a; border: 1px solid #1e293b; border-radius: 8px;
            padding: 12px; height: 100%; box-shadow: 0 4px 20px rgba(0,0,0,0.4);
        }
        .panel-header { 
            font-size: 11px; color: #94a3b8; font-weight: 700; 
            text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px; 
        }
        .metric-card {
            background: linear-gradient(180deg, #141b2d 0%, #0c101b 100%);
            border: 1px solid #22d3ee33; border-radius: 6px; padding: 10px; height: 85px;
        }
        .metric-label { font-size: 10px; color: #94a3b8; font-weight: 600; }
        .metric-value { font-size: 22px; font-weight: 700; color: #22d3ee; margin-top: 2px; }
        .metric-unit { font-size: 12px; color: #64748b; font-weight: 500; }
        .metric-sub { font-size: 10px; color: #10b981; margin-top: 1px; }

        div[data-baseweb="select"] { background-color: #1e293b !important; border: 1px solid #334155 !important; border-radius: 4px; }
        div[data-baseweb="select"] * { color: #ffffff !important; font-size: 12px !important; }
    </style>
""", unsafe_allow_html=True)

# 3. COMPLETE DATA BANK WITH HISTORICAL TRENDS (เชื่อมโยงสถิติรายก๊าซ)
DATA_BANK = {
    "ภาคกลาง (Bangkok & Periphery)": {
        "metrics": {
            "CO₂": {"val": 421.5, "sub": "+0.3% vs last month", "unit": "ppm", "history": [310, 335, 360, 385, 405, 421.5]},
            "CH₄": {"val": 1919.4, "sub": "from station 1", "unit": "ppb", "history": [1650, 1710, 1780, 1840, 1890, 1919.4]},
            "NO₂": {"val": 330.8, "sub": "traffic emissions", "unit": "ppb", "history": [190, 220, 255, 280, 310, 330.8]},
            "Temp Anomaly": {"val": 1.8, "sub": "Above baseline", "unit": "°C"},
            "AQI": {"val": 85, "sub": "Moderate", "unit": ""},
            "Humidity": {"val": 64, "sub": "Relative", "unit": "%"}
        },
        "map_center": [13.7563, 100.5018],
        "stack_data": {'PM2.5': [50, 30, 20], 'PM10': [60, 25, 15], 'NO₂': [40, 35, 25], 'SO₂': [70, 15, 15], 'O₃': [55, 30, 15]},
        "river_do": ["4.2 mg/L", "2.1 mg/L", "5.5 mg/L"],
        "river_status": ["🟢 Normal", "🔴 Unhealthy", "🟢 Normal"]
    },
    "ภาคเหนือ (Chiang Mai & Upper North)": {
        "metrics": {
            "CO₂": {"val": 415.2, "sub": "+0.1% vs last month", "unit": "ppm", "history": [305, 328, 352, 378, 398, 415.2]},
            "CH₄": {"val": 1850.2, "sub": "biomass burn", "unit": "ppb", "history": [1610, 1660, 1720, 1770, 1810, 1850.2]},
            "NO₂": {"val": 120.4, "sub": "agricultural", "unit": "ppb", "history": [60, 75, 90, 105, 115, 120.4]},
            "Temp Anomaly": {"val": 2.4, "sub": "Critical Warm", "unit": "°C"},
            "AQI": {"val": 165, "sub": "Unhealthy", "unit": ""},
            "Humidity": {"val": 42, "sub": "Dry Season", "unit": "%"}
        },
        "map_center": [18.7883, 98.9853],
        "stack_data": {'PM2.5': [20, 30, 80], 'PM10': [30, 40, 50], 'NO₂': [70, 20, 10], 'SO₂': [85, 10, 5], 'O₃': [40, 40, 20]},
        "river_do": ["5.8 mg/L", "4.5 mg/L", "6.1 mg/L"],
        "river_status": ["🟢 Normal", "🟢 Normal", "🟢 Normal"]
    },
    "ภาคใต้ (Phuket & Coastal Zone)": {
        "metrics": {
            "CO₂": {"val": 408.9, "sub": "-0.2% vs last month", "unit": "ppm", "history": [300, 320, 345, 370, 390, 408.9]},
            "CH₄": {"val": 1795.7, "sub": "marine source", "unit": "ppb", "history": [1580, 1620, 1670, 1710, 1760, 1795.7]},
            "NO₂": {"val": 45.1, "sub": "low industrial", "unit": "ppb", "history": [20, 25, 30, 35, 40, 45.1]},
            "Temp Anomaly": {"val": 0.9, "sub": "Stable Coast", "unit": "°C"},
            "AQI": {"val": 32, "sub": "Good", "unit": ""},
            "Humidity": {"val": 82, "sub": "Monsoon Influenced", "unit": "%"}
        },
        "map_center": [7.8804, 98.3923],
        "stack_data": {'PM2.5': [85, 10, 5], 'PM10': [90, 8, 2], 'NO₂': [95, 4, 1], 'SO₂': [90, 8, 2], 'O₃': [80, 15, 5]},
        "river_do": ["6.5 mg/L", "5.9 mg/L", "6.2 mg/L"],
        "river_status": ["🟢 Normal", "🟢 Normal", "🟢 Normal"]
    }
}

# 4. TOP BAR INTERFACE
st.markdown("""
<div class="top-header">
    <div class="main-title">DASHBOARD “TRACKING GHGs EMISSION”</div>
    <div class="clock-display">MARCH 2026 | 13:58:55</div>
</div>
""", unsafe_allow_html=True)

col_sel1, col_sel2, col_sel_blank = st.columns([3.0, 2.5, 6.5])
with col_sel1:
    st.markdown('<div class="selector-label">REGION (เลือกภูมิภาคเรียกดูข้อมูล)</div>', unsafe_allow_html=True)
    selected_region = st.selectbox("Region", list(DATA_BANK.keys()), label_visibility="collapsed")
with col_sel2:
    st.markdown('<div class="selector-label">MAIN METRIC HIGHLIGHT (คัดเลือกสารเพื่อเปลี่ยนกราฟแนวโน้ม)</div>', unsafe_allow_html=True)
    # คีย์ตรงนี้ต้องแมปให้ตรงกับคีย์ในฐานข้อมูล เพื่อใช้เรียกค่าประวัติได้ทันที
    selected_metric = st.selectbox("Metric", ["CO₂", "CH₄", "NO₂"], label_visibility="collapsed")

current_data = DATA_BANK[selected_region]
m_store = current_data["metrics"]

# --- 5. SECTION 1: ENVIRONMENTAL METRICS (แผงเกจวัดและการ์ดข้อมูลด้านบน) ---
st.markdown("<div style='margin-bottom: 8px;'></div>", unsafe_allow_html=True)
m_col1, m_col2, m_col3, m_col4, m_col5, m_col6 = st.columns(6)

# 1. CO2 Level
with m_col1:
    fig_g1 = go.Figure(go.Indicator(
        mode="gauge+number", value=m_store["CO₂"]["val"],
        number={'suffix': f" {m_store['CO₂']['unit']}", 'font': {'size': 18, 'color': '#ffffff'}},
        gauge={'axis': {'range': [390, 450], 'tickwidth': 1}, 'bar': {'color': "#22d3ee"}},
        title={'text': "1 ATMOSPHERIC CO₂ LEVEL", 'font': {'size': 9, 'color': '#94a3b8', 'weight': 'bold'}}
    ))
    fig_g1.update_layout(height=85, margin=dict(t=25, b=5, l=10, r=10), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    st.markdown('<div class="panel-box">', unsafe_allow_html=True)
    st.plotly_chart(fig_g1, use_container_width=True, config={'displayModeBar': False})
    st.markdown(f'<div style="text-align:center; font-size:10px; color:#10b981; margin-top:-5px;">{m_store["CO₂"]["sub"]}</div></div>', unsafe_allow_html=True)

# 2. Temp Anomaly
with m_col2:
    fig_g2 = go.Figure(go.Indicator(
        mode="gauge+number", value=m_store["Temp Anomaly"]["val"],
        number={'prefix': "+", 'suffix': f" {m_store['Temp Anomaly']['unit']}", 'font': {'size': 18, 'color': '#f97316'}},
        gauge={'axis': {'range': [0, 4], 'tickwidth': 1}, 'bar': {'color': "#f97316"}},
        title={'text': "2 AV. TEMPERATURE ANOMALY", 'font': {'size': 9, 'color': '#94a3b8', 'weight': 'bold'}}
    ))
    fig_g2.update_layout(height=85, margin=dict(t=25, b=5, l=10, r=10), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    st.markdown('<div class="panel-box">', unsafe_allow_html=True)
    st.plotly_chart(fig_g2, use_container_width=True, config={'displayModeBar': False})
    st.markdown(f'<div style="text-align:center; font-size:10px; color:#f97316; margin-top:-5px;">{m_store["Temp Anomaly"]["sub"]}</div></div>', unsafe_allow_html=True)

# 3. AQI
with m_col3:
    aqi_color = "#10b981" if m_store["AQI"]["val"] < 50 else "#eab308" if m_store["AQI"]["val"] <= 100 else "#ef4444"
    fig_g3 = go.Figure(go.Indicator(
        mode="gauge+number", value=m_store["AQI"]["val"],
        number={'font': {'size': 18, 'color': aqi_color}},
        gauge={'axis': {'range': [0, 200], 'tickwidth': 1}, 'bar': {'color': aqi_color}},
        title={'text': "3 AIR QUALITY INDEX (AQI)", 'font': {'size': 9, 'color': '#94a3b8', 'weight': 'bold'}}
    ))
    fig_g3.update_layout(height=85, margin=dict(t=25, b=5, l=10, r=10), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    st.markdown('<div class="panel-box">', unsafe_allow_html=True)
    st.plotly_chart(fig_g3, use_container_width=True, config={'displayModeBar': False})
    st.markdown(f'<div style="text-align:center; font-size:10px; color:{aqi_color}; margin-top:-5px;">{m_store["AQI"]["sub"]}</div></div>', unsafe_allow_html=True)

# 4. CH4 Card
with m_col4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">1 CH₄ CONCENTRATION</div>
        <div class="metric-value">{m_store["CH₄"]["val"]} <span class="metric-unit">{m_store["CH₄"]["unit"]}</span></div>
        <div class="metric-sub" style="color:#64748b;">{m_store["CH₄"]["sub"]}</div>
    </div>
    """, unsafe_allow_html=True)

# 5. NO2 Card
with m_col5:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">2 NO₂ LEVEL</div>
        <div class="metric-value" style="color: #60a5fa;">{m_store["NO₂"]["val"]} <span class="metric-unit">{m_store["NO₂"]["unit"]}</span></div>
        <div class="metric-sub" style="color:#64748b;">{m_store["NO₂"]["sub"]}</div>
    </div>
    """, unsafe_allow_html=True)

# 6. Humidity Card
with m_col6:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">3 HUMIDITY</div>
        <div class="metric-value" style="color: #f43f5e;">{m_store["Humidity"]["val"]}<span class="metric-unit">{m_store["Humidity"]["unit"]}</span></div>
        <div class="metric-sub" style="color:#64748b;">{m_store["Humidity"]["sub"]}</div>
    </div>
    """, unsafe_allow_html=True)


# --- 6. SECTION 2: MIDDLE VISUALIZATION (ปรับแก้โค้ดกราฟวิเคราะห์ตรงนี้ให้เปลี่ยนตามเลือก) ---
st.markdown("<div style='margin-bottom: 10px;'></div>", unsafe_allow_html=True)
layout_col1, layout_col2, layout_col3 = st.columns([1.1, 0.9, 1.0])

# ฝั่งซ้าย: แผนที่ความร้อนระบุพิกัดมลพิษสะสม
with layout_col1:
    st.markdown('<div class="panel-box">', unsafe_allow_html=True)
    st.markdown("<div class='panel-header'>GHG & POLLUTION HOTSPOTS (REGIONAL ANALYSIS)</div>", unsafe_allow_html=True)
    np.random.seed(42)
    center_lat, center_lon = current_data["map_center"]
    map_df = pd.DataFrame({
        'lat': [center_lat + np.random.uniform(-0.06, 0.06) for _ in range(12)],
        'lon': [center_lon + np.random.uniform(-0.06, 0.06) for _ in range(12)],
        'intensity': np.random.randint(60, 140, 12)
    })
    fig_map = px.density_mapbox(map_df, lat='lat', lon='lon', z='intensity', radius=28,
                                center=dict(lat=center_lat, lon=center_lon), zoom=9,
                                mapbox_style="carto-darkmatter")
    fig_map.update_layout(height=250, margin=dict(t=0, b=0, l=0, r=0), paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig_map, use_container_width=True, config={'displayModeBar': False})
    st.markdown('</div>', unsafe_allow_html=True)

# 🛠️ ฝั่งกลาง: แก้ไขให้ผูกค่าตาม 'selected_metric' ดึงประวัติก๊าซแต่ละตัวมาพล็อตแบบ Dynamic
with layout_col2:
    st.markdown('<div class="panel-box">', unsafe_allow_html=True)
    
    # 1. เปลี่ยนชื่อหัวข้อแผงตามก๊าซที่เลือกจริง
    unit_label = m_store[selected_metric]["unit"]
    st.markdown(f"<div class='panel-header'>30-YEAR {selected_metric} EMISSIONS TREND ({unit_label.upper()}/YR)</div>", unsafe_allow_html=True)
    
    # 2. ดึงชุดประวัติย้อนหลังของก๊าซนั้น ๆ ออกจากฐานข้อมูลตรงพิกัดภูมิภาคที่เลือก
    years_x = [1930, 1950, 1970, 1990, 2010, 2026]
    historical_y = m_store[selected_metric]["history"]  # ดึงอาเรย์ค่าจริงมาใช้งานตรงนี้!
    
    df_trend = pd.DataFrame({'Year': years_x, 'Emissions': historical_y})
    
    # 3. สั่งวาดกราฟพื้นที่เชื่อมโยงข้อมูลสมบูรณ์แบบ
    fig_trend = px.area(df_trend, x='Year', y='Emissions', template="plotly_dark")
    fig_trend.update_traces(line_color='#22d3ee', fillcolor='rgba(34, 211, 238, 0.08)', mode='lines+markers')
    fig_trend.update_layout(
        height=250, margin=dict(t=10, b=5, l=5, r=5), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)', title=unit_label) # กำหนดป้ายแกน Y ตามหน่วยก๊าซจริง
    )
    st.plotly_chart(fig_trend, use_container_width=True, config={'displayModeBar': False})
    st.markdown('</div>', unsafe_allow_html=True)

# ฝั่งขวา: กราฟแท่งรายเดือนเปรียบเทียบอุณหภูมิและอากาศ
with layout_col3:
    st.markdown('<div class="panel-box">', unsafe_allow_html=True)
    st.markdown("<div class='panel-header'>MONTHLY TEMPERATURE VS. AIR QUALITY</div>", unsafe_allow_html=True)
    months = ['Jan', 'Mar', 'May', 'Jul', 'Sep', 'Nov']
    base_aqi = m_store["AQI"]["val"]
    monthly_aqi = [max(10, v) for v in [base_aqi + 20, base_aqi, base_aqi - 30, base_aqi - 40, base_aqi - 10, base_aqi + 15]]
    
    fig_bar = px.bar(x=months, y=monthly_aqi, template="plotly_dark")
    fig_bar.update_traces(marker_color='#f97316', opacity=0.85)
    fig_bar.update_layout(height=250, margin=dict(t=10, b=5, l=5, r=5), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                          xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)'))
    st.plotly_chart(fig_bar, use_container_width=True, config={'displayModeBar': False})
    st.markdown('</div>', unsafe_allow_html=True)


# --- 7. SECTION 3: BOTTOM ANALYSIS PANELS ---
st.markdown("<div style='margin-bottom: 10px;'></div>", unsafe_allow_html=True)
bottom_col1, bottom_col2 = st.columns([1.1, 0.9])

# ด้านล่างซ้าย: POLLUTION BREAKDOWN
with bottom_col1:
    st.markdown('<div class="panel-box">', unsafe_allow_html=True)
    st.markdown("<div class='panel-header'>POLLUTION BREAKDOWN (GHGs & PARTICULATE MATTER CRITERIA)</div>", unsafe_allow_html=True)
    s_data = current_data["stack_data"]
    comp_list = list(s_data.keys())
    fig_stack = go.Figure(data=[
        go.Bar(name='Low/Safe', x=comp_list, y=[s_data[c][0] for c in comp_list], marker_color='#10b981'),
        go.Bar(name='Moderate', x=comp_list, y=[s_data[c][1] for c in comp_list], marker_color='#eab308'),
        go.Bar(name='Unhealthy', x=comp_list, y=[s_data[c][2] for c in comp_list], marker_color='#ef4444')
    ])
    fig_stack.update_layout(barmode='stack', height=135, margin=dict(t=10, b=5, l=5, r=5), template="plotly_dark",
                            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", showlegend=False,
                            xaxis=dict(showgrid=False), yaxis=dict(showgrid=False))
    st.plotly_chart(fig_stack, use_container_width=True, config={'displayModeBar': False})
    st.markdown('</div>', unsafe_allow_html=True)

# ด้านล่างขวา: WATER QUALITY MONITORING
with bottom_col2:
    st.markdown('<div class="panel-box">', unsafe_allow_html=True)
    st.markdown("<div class='panel-header'>WATER QUALITY MONITORING (MAJOR RIVERS STATUS)</div>", unsafe_allow_html=True)
    river_df = pd.DataFrame({
        'River Station (ลุ่มน้ำหลัก)': ['Chao Phraya (แม่น้ำเจ้าพระยา)', 'Tha Chin (แม่น้ำท่าจีน)', 'Mae Klong (แม่น้ำแม่กลอง)'],
        'Dissolved Oxygen (DO)': current_data["river_do"],
        'Environmental Status': current_data["river_status"]
    })
    st.dataframe(river_df, hide_index=True, use_container_width=True, height=130)
    st.markdown('</div>', unsafe_allow_html=True)
