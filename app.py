import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# 1. SETUP & CONFIGURATION
st.set_page_config(layout="wide", page_title="Dashboard Tracking GHGs Emission", initial_sidebar_state="collapsed")

# 2. ADVANCED CSS: ถอดแบบโครงสร้าง Layout และดีไซน์แผงควบคุมจากรูปภาพ 100%
st.markdown("""
    <style>
        /* ซ่อนแถบเลื่อนและล็อกขนาดหน้าจอ */
        ::-webkit-scrollbar { display: none; }
        html, body, [data-testid="stAppViewContainer"] { 
            overflow: hidden !important; 
            height: 100vh !important; 
            background-color: #0b0f19 !important;
        }
        
        .block-container { padding: 0.8rem 1.5rem !important; }
        
        /* --- HEADER STYLING --- */
        .top-header {
            display: flex; justify-content: space-between; align-items: center;
            padding-bottom: 8px; border-bottom: 1px solid #1e293b; margin-bottom: 12px;
        }
        .main-title { font-size: 20px; font-weight: 800; color: #ffffff; letter-spacing: 0.5px; }
        .clock-display { font-family: monospace; font-size: 16px; color: #94a3b8; font-weight: 700; }

        /* --- CONTROL SELECTORS --- */
        .selector-label { font-size: 10px; color: #64748b; font-weight: 700; text-transform: uppercase; margin-bottom: 2px; }

        /* --- PANEL CONTAINER CARD --- */
        .panel-box {
            background-color: #0f172a; border: 1px solid #1e293b; border-radius: 8px;
            padding: 12px; height: 100%; box-shadow: 0 4px 20px rgba(0,0,0,0.4);
        }
        .panel-header { 
            font-size: 11px; color: #94a3b8; font-weight: 700; 
            text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px; 
        }
        
        /* --- SMALL METRIC CARD --- */
        .metric-card {
            background: linear-gradient(180deg, #141b2d 0%, #0c101b 100%);
            border: 1px solid #22d3ee33; border-radius: 6px; padding: 10px; height: 85px;
        }
        .metric-label { font-size: 10px; color: #94a3b8; font-weight: 600; }
        .metric-value { font-size: 22px; font-weight: 700; color: #22d3ee; margin-top: 2px; }
        .metric-unit { font-size: 12px; color: #64748b; font-weight: 500; }
        .metric-sub { font-size: 10px; color: #10b981; margin-top: 1px; }

        /* ปรับสไตล์ Dropdown ของ Streamlit ให้กลืนกับธีมมืด */
        div[data-baseweb="select"] { background-color: #1e293b !important; border: 1px solid #334155 !important; border-radius: 4px; }
        div[data-baseweb="select"] * { color: #ffffff !important; font-size: 12px !important; }
    </style>
""", unsafe_allow_html=True)

# 3. COMPLETE MOCK DATA (แยกค่าของแต่ละภูมิภาคให้แตกต่างกันอย่างชัดเจนเพื่อให้เห็นความเปลี่ยนแปลง)
DATA_BANK = {
    "ภาคกลาง (Bangkok & Periphery)": {
        "metrics": {
            "CO₂": {"val": 421.5, "sub": "+0.3% vs last month", "unit": "ppm"},
            "Temp Anomaly": {"val": 1.8, "sub": "Above baseline", "unit": "°C"},
            "AQI": {"val": 85, "sub": "Moderate", "unit": ""},
            "CH₄": {"val": 1919.4, "sub": "from station 1", "unit": "ppb"},
            "NO₂": {"val": 330.8, "sub": "traffic emissions", "unit": "ppb"},
            "Humidity": {"val": 64, "sub": "Relative", "unit": "%"}
        },
        "map_center": [13.7563, 100.5018],
        "line_trend": [250, 450, 680, 920, 1180, 1450],
        "stack_data": {'PM2.5': [50, 30, 20], 'PM10': [60, 25, 15], 'NO₂': [40, 35, 25], 'SO₂': [70, 15, 15], 'O₃': [55, 30, 15]},
        "river_do": ["4.2 mg/L", "2.1 mg/L", "5.5 mg/L"],
        "river_status": ["🟢 Normal", "🔴 Unhealthy", "🟢 Normal"]
    },
    "ภาคเหนือ (Chiang Mai & Upper North)": {
        "metrics": {
            "CO₂": {"val": 415.2, "sub": "+0.1% vs last month", "unit": "ppm"},
            "Temp Anomaly": {"val": 2.4, "sub": "Critical Warm", "unit": "°C"},
            "AQI": {"val": 165, "sub": "Unhealthy", "unit": ""},
            "CH₄": {"val": 1850.2, "sub": "biomass burn", "unit": "ppb"},
            "NO₂": {"val": 120.4, "sub": "agricultural", "unit": "ppb"},
            "Humidity": {"val": 42, "sub": "Dry Season", "unit": "%"}
        },
        "map_center": [18.7883, 98.9853],
        "line_trend": [180, 320, 510, 780, 990, 1210],
        "stack_data": {'PM2.5': [20, 30, 80], 'PM10': [30, 40, 50], 'NO₂': [70, 20, 10], 'SO₂': [85, 10, 5], 'O₃': [40, 40, 20]},
        "river_do": ["5.8 mg/L", "4.5 mg/L", "6.1 mg/L"],
        "river_status": ["🟢 Normal", "🟢 Normal", "🟢 Normal"]
    },
    "ภาคใต้ (Phuket & Coastal Zone)": {
        "metrics": {
            "CO₂": {"val": 408.9, "sub": "-0.2% vs last month", "unit": "ppm"},
            "Temp Anomaly": {"val": 0.9, "sub": "Stable Coast", "unit": "°C"},
            "AQI": {"val": 32, "sub": "Good", "unit": ""},
            "CH₄": {"val": 1795.7, "sub": "marine source", "unit": "ppb"},
            "NO₂": {"val": 45.1, "sub": "low industrial", "unit": "ppb"},
            "Humidity": {"val": 82, "sub": "Monsoon Influenced", "unit": "%"}
        },
        "map_center": [7.8804, 98.3923],
        "line_trend": [150, 220, 390, 550, 680, 790],
        "stack_data": {'PM2.5': [85, 10, 5], 'PM10': [90, 8, 2], 'NO₂': [95, 4, 1], 'SO₂': [90, 8, 2], 'O₃': [80, 15, 5]},
        "river_do": ["6.5 mg/L", "5.9 mg/L", "6.2 mg/L"],
        "river_status": ["🟢 Normal", "🟢 Normal", "🟢 Normal"]
    }
}

# 4. TOP BAR INTERFACE (ส่วนหัวและตัวเลือกภูมิภาคขนานกันแบบแผงควบคุมระบบ)
st.markdown("""
<div class="top-header">
    <div class="main-title">DASHBOARD “TRACKING GHGs EMISSION”</div>
    <div class="clock-display">MARCH 2026 | 13:58:55</div>
</div>
""", unsafe_allow_html=True)

col_sel1, col_sel2, col_sel_blank = st.columns([2.5, 2.5, 7])
with col_sel1:
    st.markdown('<div class="selector-label">REGION (เลือกภูมิภาคเรียกดูข้อมูล)</div>', unsafe_allow_html=True)
    selected_region = st.selectbox("Region", list(DATA_BANK.keys()), label_visibility="collapsed")
with col_sel2:
    st.markdown('<div class="selector-label">MAIN METRIC HIGHLIGHT (คัดเลือกสารเพื่อวิเคราะห์)</div>', unsafe_allow_html=True)
    selected_metric = st.selectbox("Metric", ["CO₂ (Carbon Dioxide)", "CH₄ (Methane)", "NO₂ (Nitrogen Dioxide)"], label_visibility="collapsed")

# ดึงชุดข้อมูลที่ผูกไว้กับภูมิภาคที่เลือกมาทำงานทันที
current_data = DATA_BANK[selected_region]
m_store = current_data["metrics"]

# --- 5. SECTION 1: KEY ENVIRONMENTAL METRICS (แผงเกจวัด 3 ตัว และการ์ดข้อมูล 3 ตัว) ---
st.markdown("<div style='margin-bottom: 8px;'></div>", unsafe_allow_html=True)
m_col1, m_col2, m_col3, m_col4, m_col5, m_col6 = st.columns(6)

# กล่องที่ 1: ATMOSPHERIC CO2 LEVEL (Gauge)
with m_col1:
    fig_g1 = go.Figure(go.Indicator(
        mode="gauge+number", value=m_store["CO₂"]["val"],
        number={'suffix': f" {m_store['CO₂']['unit']}", 'font': {'size': 18, 'color': '#ffffff'}},
        gauge={'axis': {'range': [390, 450], 'tickwidth': 1, 'tickcolor': "#475569"}, 'bar': {'color': "#22d3ee"}},
        title={'text': "1 ATMOSPHERIC CO₂ LEVEL", 'font': {'size': 9, 'color': '#94a3b8', 'weight': 'bold'}}
    ))
    fig_g1.update_layout(height=85, margin=dict(t=25, b=5, l=10, r=10), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    st.markdown('<div class="panel-box">', unsafe_allow_html=True)
    st.plotly_chart(fig_g1, use_container_width=True, config={'displayModeBar': False})
    st.markdown(f'<div style="text-align:center; font-size:10px; color:#10b981; margin-top:-5px;">{m_store["CO₂"]["sub"]}</div></div>', unsafe_allow_html=True)

# กล่องที่ 2: AV. TEMPERATURE ANOMALY (Gauge)
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

# กล่องที่ 3: AIR QUALITY INDEX (AQI Gauge)
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

# กล่องที่ 4: CH4 CONCENTRATION
with m_col4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">1 CH₄ CONCENTRATION</div>
        <div class="metric-value">{m_store["CH₄"]["val"]} <span class="metric-unit">{m_store["CH₄"]["unit"]}</span></div>
        <div class="metric-sub" style="color:#64748b;">{m_store["CH₄"]["sub"]}</div>
    </div>
    """, unsafe_allow_html=True)

# กล่องที่ 5: NO2 LEVEL
with m_col5:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">2 NO₂ LEVEL</div>
        <div class="metric-value" style="color: #60a5fa;">{m_store["NO₂"]["val"]} <span class="metric-unit">{m_store["NO₂"]["unit"]}</span></div>
        <div class="metric-sub" style="color:#64748b;">{m_store["NO₂"]["sub"]}</div>
    </div>
    """, unsafe_allow_html=True)

# กล่องที่ 6: HUMIDITY
with m_col6:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">3 HUMIDITY</div>
        <div class="metric-value" style="color: #f43f5e;">{m_store["Humidity"]["val"]}<span class="metric-unit">{m_store["Humidity"]["unit"]}</span></div>
        <div class="metric-sub" style="color:#64748b;">{m_store["Humidity"]["sub"]}</div>
    </div>
    """, unsafe_allow_html=True)


# --- 6. SECTION 2: MIDDLE VISUALIZATION (แบ่ง 3 คอลัมน์ตามรูปภาพต้นฉบับเป๊ะๆ) ---
st.markdown("<div style='margin-bottom: 10px;'></div>", unsafe_allow_html=True)
layout_col1, layout_col2, layout_col3 = st.columns([1.1, 0.9, 1.0])

# ฝั่งซ้าย: แผนที่ความร้อนระบุพิกัดมลพิษสะสม (Pollution Hotspots)
with layout_col1:
    st.markdown('<div class="panel-box">', unsafe_allow_html=True)
    st.markdown("<div class='panel-header'>GHG & POLLUTION HOTSPOTS (REGIONAL ANALYSIS)</div>", unsafe_allow_html=True)
    
    # พลอตแผนที่ความร้อนตามจุดพิกัดภูมิภาคที่สลับค่าได้จริง
    np.random.seed(42)
    center_lat, center_lon = current_data["map_center"]
    map_df = pd.DataFrame({
        'lat': [center_lat + np.random.uniform(-0.08, 0.08) for _ in range(15)],
        'lon': [center_lon + np.random.uniform(-0.08, 0.08) for _ in range(15)],
        'intensity': np.random.randint(40, 150, 15)
    })
    
    fig_map = px.density_mapbox(map_df, lat='lat', lon='lon', z='intensity', radius=30,
                                center=dict(lat=center_lat, lon=center_lon), zoom=9,
                                mapbox_style="carto-darkmatter")
    fig_map.update_layout(height=250, margin=dict(t=0, b=0, l=0, r=0), paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig_map, use_container_width=True, config={'displayModeBar': False})
    st.markdown('</div>', unsafe_allow_html=True)

# ฝั่งกลาง: กราฟเส้นแสดงสถิติย้อนหลังระยะยาวสะสม 30 ปี (ตามสไตล์รูปภาพ)
with layout_col2:
    st.markdown('<div class="panel-box">', unsafe_allow_html=True)
    st.markdown(f"<div class='panel-header'>30-YEAR {selected_metric.split(' ')[0]} EMISSIONS TREND (KT/YR)</div>", unsafe_allow_html=True)
    
    years = [1930, 1950, 1970, 1990, 2010, 2026]
    trend_vals = current_data["line_trend"]
    df_trend = pd.DataFrame({'Year': years, 'Emissions': trend_vals})
    
    fig_trend = px.area(df_trend, x='Year', y='Emissions', template="plotly_dark")
    fig_trend.update_traces(line_color='#22d3ee', fillcolor='rgba(34, 211, 238, 0.08)', mode='lines+markers')
    fig_trend.update_layout(height=250, margin=dict(t=10, b=5, l=5, r=5), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                            xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)'))
    st.plotly_chart(fig_trend, use_container_width=True, config={'displayModeBar': False})
    st.markdown('</div>', unsafe_allow_html=True)

# ฝั่งขวา: กราฟแท่งรายเดือนเปรียบเทียบอุณหภูมิและอากาศ
with layout_col3:
    st.markdown('<div class="panel-box">', unsafe_allow_html=True)
    st.markdown("<div class='panel-header'>MONTHLY TEMPERATURE VS. AIR QUALITY</div>", unsafe_allow_html=True)
    
    months = ['Jan', 'Mar', 'May', 'Jul', 'Sep', 'Nov']
    # ปรับแต่งความสูงต่ำของกราฟแท่งตามดัชนี AQI ของภูมิภาคนั้นจริง
    base_aqi = m_store["AQI"]["val"]
    monthly_aqi = [base_aqi + 20, base_aqi, base_aqi - 30, base_aqi - 40, base_aqi - 10, base_aqi + 15]
    monthly_aqi = [max(10, v) for v in monthly_aqi] # บังคับไม่ให้ติดลบ
    
    fig_bar = px.bar(x=months, y=monthly_aqi, template="plotly_dark")
    fig_bar.update_traces(marker_color='#f97316', opacity=0.85)
    fig_bar.update_layout(height=250, margin=dict(t=10, b=5, l=5, r=5), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                          xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)'))
    st.plotly_chart(fig_bar, use_container_width=True, config={'displayModeBar': False})
    st.markdown('</div>', unsafe_allow_html=True)


# --- 7. SECTION 3: BOTTOM ANALYSIS PANELS (ส่วนล่าง: สัดส่วนก๊าซเรือนกระจกครบถ้วน และดัชนีแม่น้ำ) ---
st.markdown("<div style='margin-bottom: 10px;'></div>", unsafe_allow_html=True)
bottom_col1, bottom_col2 = st.columns([1.1, 0.9])

# ด้านล่างซ้าย: POLLUTION BREAKDOWN (Stacked Bar) รวมก๊าซและมลพิษครบสเกลตามภาพ
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

# ด้านล่างขวา: WATER QUALITY MONITORING (ตารางเช็กค่าแม่น้ำสายหลัก)
with bottom_col2:
    st.markdown('<div class="panel-box">', unsafe_allow_html=True)
    st.markdown("<div class='panel-header'>WATER QUALITY MONITORING (MAJOR RIVERS STATUS)</div>", unsafe_allow_html=True)
    
    river_df = pd.DataFrame({
        'River Station (ลุ่มน้ำหลัก)': ['Chao Phraya (แม่น้ำเจ้าพระยา)', 'Tha Chin (แม่น้ำท่าจีน)', 'Mae Klong (แม่น้ำแม่กลอง)'],
        'Dissolved Oxygen (DO)': current_data["river_do"],
        'Environmental Status': current_data["river_status"]
    })
    
    # แสดงผลตารางด้วย DataFrame แบบซ่อนดัชนีให้กลืนไปกับหน้าดีไซน์แผงควบคุม
    st.dataframe(river_df, hide_index=True, use_container_width=True, height=130)
    st.markdown('</div>', unsafe_allow_html=True)
