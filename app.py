import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# 1. SETUP: บังคับหน้ากว้าง (Wide) และล็อก Layout หน้าจอเดี่ยวแบบแอปพลิเคชัน
st.set_page_config(layout="wide", page_title="Dashboard Tracking GHGs Emission", initial_sidebar_state="collapsed")

# 2. CSS: ตกแต่งหน้าตาแบบ Midnight Cyber High-Contrast (ถอดดีไซน์จากรูปตัวอย่าง)
st.markdown("""
    <style>
        /* ล็อกมิติหน้าจอและซ่อน Scrollbar ของระบบ */
        ::-webkit-scrollbar { display: none; }
        html, body, [data-testid="stAppViewContainer"] { 
            overflow: hidden !important; 
            height: 100vh !important; 
            background-color: #060b13 !important;
        }
        
        /* จัดระยะห่างขอบแอปหลัก */
        .block-container { padding: 1rem 2rem !important; }

        /* --- STYLING HEADER --- */
        .header-container {
            display: flex; justify-content: space-between; align-items: center;
            margin-bottom: 15px; border-bottom: 1px solid rgba(255,255,255,0.08); padding-bottom: 10px;
        }
        .header-title-box { display: flex; align-items: center; gap: 12px; }
        .header-title { font-size: 22px; font-weight: 800; color: #ffffff; letter-spacing: 0.5px; }
        .header-time { font-family: monospace; font-size: 18px; color: #94a3b8; font-weight: bold; }

        /* --- STYLING PANEL CARD --- */
        .panel-card {
            background: linear-gradient(180deg, rgba(20, 32, 48, 0.7) 0%, rgba(10, 15, 26, 0.8) 100%);
            border: 1px solid rgba(34, 211, 238, 0.2);
            border-radius: 12px; padding: 15px; height: 100%;
            box-shadow: 0 8px 24px rgba(0,0,0,0.5);
        }
        .panel-label { font-size: 11px; color: #94a3b8; text-transform: uppercase; font-weight: 600; margin-bottom: 5px; }
        .panel-value { font-size: 28px; font-weight: 700; color: #22d3ee; margin: 2px 0; }
        .panel-sub { font-size: 11px; color: #10b981; font-weight: 500; }

        /* จัดแต่ง Component ของ Streamlit Dropdown ให้เข้าธีม */
        div[data-baseweb="select"] { background-color: #0f172a !important; border-radius: 6px; }
        div[data-baseweb="select"] * { color: white !important; font-size: 13px !important; }
    </style>
""", unsafe_allow_html=True)

# 3. MOCK DATA: คลังข้อมูลสิ่งแวดล้อมสอดคล้องกันแต่ละภูมิภาค
# ข้อมูลจะเปลี่ยนตามภูมิภาคที่เลือก เพื่อความสอดคล้อง (Consistency) ของระบบ
REGION_DATA = {
    "ภาคกลาง": {
        "co2": 421.5, "co2_sub": "+0.3% vs เดือนก่อน", "temp": 1.8, "aqi": 85, "aqi_status": "ปานกลาง (Moderate)",
        "ch4": 1919.4, "no2": 330.8, "humid": 64, "heatmap_center": [13.75, 100.50], "multiplier": 1.0
    },
    "ภาคเหนือ": {
        "co2": 418.2, "co2_sub": "-0.1% vs เดือนก่อน", "temp": 1.2, "aqi": 120, "aqi_status": "เริ่มมีผลกระทบ",
        "ch4": 1890.5, "no2": 210.4, "humid": 55, "heatmap_center": [18.78, 98.98], "multiplier": 0.8
    },
    "ภาคใต้": {
        "co2": 412.4, "co2_sub": "-0.4% vs เดือนก่อน", "temp": 0.9, "aqi": 35, "aqi_status": "ดีมาก (Good)",
        "ch4": 1850.1, "no2": 105.2, "humid": 78, "heatmap_center": [7.88, 98.39], "multiplier": 0.5
    }
}

# 4. TOP BAR: ส่วนหัวและตัวควบคุมข้อมูล (เหมือนเมนูด้านบนของภาพตัวอย่าง)
st.markdown("""
<div class="header-container">
    <div class="header-title-box">
        <span style="font-size:24px;">🌍</span>
        <div class="header-title">DASHBOARD “TRACKING GHGs EMISSION”</div>
    </div>
    <div class="header-time">MARCH 2026 | 13:58:55</div>
</div>
""", unsafe_allow_html=True)

# สร้าง Dropdown เลือกภูมิภาคและตัวชี้วัดหลัก ขนานกันด้านบน
ctrl_col1, ctrl_col2, ctrl_col_blank = st.columns([1.5, 1.5, 5])
with ctrl_col1:
    selected_region = st.selectbox("REGION (ภูมิภาค):", list(REGION_DATA.keys()), label_visibility="collapsed")
with ctrl_col2:
    selected_metric = st.selectbox("METRIC (ตัวชี้วัดย่อย):", ["CO₂ (ppm)", "CH₄ (ppb)", "NO₂ (ppb)"], label_visibility="collapsed")

# ดึงข้อมูลของภูมิภาคที่เลือกมาใช้งาน
data = REGION_DATA[selected_region]

# --- 5. SECTION 1: KEY ENVIRONMENTAL METRICS (กล่องเกจวัดและค่ามลพิษด้านบน) ---
m_col1, m_col2, m_col3, m_col4, m_col5, m_col6 = st.columns(6)

# 1. Atmospheric CO2 Level (สร้าง Gauge ด้วย Plotly)
with m_col1:
    fig_g1 = go.Figure(go.Indicator(
        mode = "gauge+number", value = data["co2"], number={'suffix': " ppm", 'font': {'size': 20, 'color': '#ffffff'}},
        gauge = {'axis': {'range': [380, 500], 'tickwidth': 1}, 'bar': {'color': "#22d3ee"}},
        title = {'text': "1 ATMOSPHERIC CO₂ LEVEL", 'font': {'size': 11, 'color': '#94a3b8'}}
    ))
    fig_g1.update_layout(height=120, margin=dict(t=30, b=10, l=15, r=15), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    st.markdown('<div class="panel-card">', unsafe_allow_html=True)
    st.plotly_chart(fig_g1, use_container_width=True, config={'displayModeBar': False})
    st.markdown(f'<div style="text-align:center; font-size:11px; color:#10b981; margin-top:-15px;">{data["co2_sub"]}</div></div>', unsafe_allow_html=True)

# 2. Av. Temperature Anomaly
with m_col2:
    fig_g2 = go.Figure(go.Indicator(
        mode = "gauge+number", value = data["temp"], number={'prefix': "+", 'suffix': " °C", 'font': {'size': 20, 'color': '#f97316'}},
        gauge = {'axis': {'range': [0, 5]}, 'bar': {'color': "#f97316"}},
        title = {'text': "2 AV. TEMPERATURE ANOMALY", 'font': {'size': 11, 'color': '#94a3b8'}}
    ))
    fig_g2.update_layout(height=120, margin=dict(t=30, b=10, l=15, r=15), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    st.markdown('<div class="panel-card">', unsafe_allow_html=True)
    st.plotly_chart(fig_g2, use_container_width=True, config={'displayModeBar': False})
    st.markdown('<div style="text-align:center; font-size:11px; color:#f97316; margin-top:-15px;">Above Baseline</div></div>', unsafe_allow_html=True)

# 3. Air Quality Index (AQI)
with m_col3:
    fig_g3 = go.Figure(go.Indicator(
        mode = "gauge+number", value = data["aqi"], number={'font': {'size': 20, 'color': '#eab308'}},
        gauge = {'axis': {'range': [0, 300]}, 'bar': {'color': "#eab308"}},
        title = {'text': "3 AIR QUALITY INDEX (AQI)", 'font': {'size': 11, 'color': '#94a3b8'}}
    ))
    fig_g3.update_layout(height=120, margin=dict(t=30, b=10, l=15, r=15), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    st.markdown('<div class="panel-card">', unsafe_allow_html=True)
    st.plotly_chart(fig_g3, use_container_width=True, config={'displayModeBar': False})
    st.markdown(f'<div style="text-align:center; font-size:11px; color:#eab308; margin-top:-15px;">{data["aqi_status"]}</div></div>', unsafe_allow_html=True)

# 4. CH4 Concentration (Styled Card)
with m_col4:
    st.markdown(f"""
    <div class="panel-card">
        <div class="panel-label">1 CH₄ CONCENTRATION</div>
        <div class="panel-value" style="color: #a7f3d0;">{data["ch4"]} <span style="font-size:14px; color:#94a3b8;">ppb</span></div>
        <div class="panel-sub" style="color: #64748b;">จากสถานีเครือข่ายหลัก</div>
    </div>
    """, unsafe_allow_html=True)

# 5. NO2 Level
with m_col5:
    st.markdown(f"""
    <div class="panel-card">
        <div class="panel-label">2 NO₂ LEVEL</div>
        <div class="panel-value" style="color: #38bdf8;">{data["no2"]} <span style="font-size:14px; color:#94a3b8;">ppb</span></div>
        <div class="panel-sub" style="color: #64748b;">เซนเซอร์ตรวจวัดไอเสีย</div>
    </div>
    """, unsafe_allow_html=True)

# 6. Humidity
with m_col6:
    st.markdown(f"""
    <div class="panel-card">
        <div class="panel-label">3 HUMIDITY</div>
        <div class="panel-value" style="color: #f43f5e;">{data["humid"]}%</div>
        <div class="panel-sub" style="color: #64748b;">ความชื้นสัมพัทธ์อากาศ</div>
    </div>
    """, unsafe_allow_html=True)


# --- 6. SECTION 2: MIDDLE LAYOUT (แผนที่ความร้อน และ กราฟวิเคราะห์เทรนด์เชิงลึก) ---
st.markdown("<div style='margin-bottom: 10px;'></div>", unsafe_allow_html=True)
layout_col1, layout_col2, layout_col3 = st.columns([1.1, 0.9, 1.0])

# ฝั่งซ้าย: แผนที่ความร้อนจำลอง (Pollution Hotspots) ตามแบบเป๊ะ ๆ
with layout_col1:
    st.markdown('<div class="panel-card">', unsafe_allow_html=True)
    st.markdown("<div class='panel-label'>GHG & POLLUTION HOTSPOTS (BANGKOK & PERIPHERY)</div>", unsafe_allow_html=True)
    
    # สร้าง Map จุดพิกัดความร้อนด้วย Scatter พลอตบนแผนที่โครงข่ายจำลอง
    np.random.seed(42)
    map_data = pd.DataFrame({
        'lat': [data["heatmap_center"][0] + np.random.uniform(-0.1, 0.1) for _ in range(20)],
        'lon': [data["heatmap_center"][1] + np.random.uniform(-0.1, 0.1) for _ in range(20)],
        'density': np.random.randint(50, 150, 20) * data["multiplier"]
    })
    fig_map = px.density_mapbox(map_data, lat='lat', lon='lon', z='density', radius=35,
                                center=dict(lat=data["heatmap_center"][0], lon=data["heatmap_center"][1]), zoom=9,
                                mapbox_style="carto-darkmatter")
    fig_map.update_layout(height=260, margin=dict(t=0, b=0, l=0, r=0), paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig_map, use_container_width=True, config={'displayModeBar': False})
    st.markdown('</div>', unsafe_allow_html=True)

# ฝั่งกลาง: กราฟเส้นเทรนด์วิเคราะห์ระยะยาว 30 ปี
with layout_col2:
    st.markdown('<div class="panel-card">', unsafe_allow_html=True)
    st.markdown("<div class='panel-label'>30-YEAR CO₂ EMISSIONS TREND (KT/YR)</div>", unsafe_allow_html=True)
    
    years = np.array([1930, 1950, 1970, 1990, 2010, 2026])
    values = np.array([200, 350, 580, 890, 1150, 1420]) * data["multiplier"]
    df_line = pd.DataFrame({'Year': years, 'Emissions': values})
    
    fig_line = px.area(df_line, x='Year', y='Emissions', template="plotly_dark")
    fig_line.update_traces(line_color='#22d3ee', fillcolor='rgba(34, 211, 238, 0.1)', mode='lines+markers')
    fig_line.update_layout(height=260, margin=dict(t=10, b=10, l=10, r=10), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                           xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)'))
    st.plotly_chart(fig_line, use_container_width=True, config={'displayModeBar': False})
    st.markdown('</div>', unsafe_allow_html=True)

# ฝั่งขวา: กราฟแท่งเปรียบเทียบอุณหภูมิรายเดือนกับคุณภาพอากาศ (Dual Chart)
with layout_col3:
    st.markdown('<div class="panel-card">', unsafe_allow_html=True)
    st.markdown("<div class='panel-label'>MONTHLY TEMPERATURE VS. AIR QUALITY</div>", unsafe_allow_html=True)
    
    months = ['Jan', 'Mar', 'May', 'Jul', 'Sep', 'Nov']
    temp_vals = [22, 26, 32, 34, 29, 24]
    aqi_vals = [140, 90, 60, 45, 75, 110]
    
    fig_bar = px.bar(x=months, y=aqi_vals, labels={'x': 'Month', 'y': 'AQI Index'}, template="plotly_dark")
    fig_bar.update_traces(marker_color='#f97316', opacity=0.8)
    fig_bar.update_layout(height=260, margin=dict(t=10, b=10, l=10, r=10), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                          xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)'))
    st.plotly_chart(fig_bar, use_container_width=True, config={'displayModeBar': False})
    st.markdown('</div>', unsafe_allow_html=True)


# --- 7. SECTION 3: BOTTOM LAYOUT (สัดส่วนสารมลพิษย่อย และ ตารางคุณภาพลำน้ำหลัก) ---
st.markdown("<div style='margin-bottom: 10px;'></div>", unsafe_allow_html=True)
bottom_col1, bottom_col2 = st.columns([1.1, 0.9])

# ด้านล่างซ้าย: กราฟแท่งซ้อน (Stacked Bars) แสดงสัดส่วนมลพิษแต่ละตัว
with bottom_col1:
    st.markdown('<div class="panel-card">', unsafe_allow_html=True)
    st.markdown("<div class='panel-label'>POLLUTION BREAKDOWN (PM2.5, PM10, NO₂, SO₂, O₃)</div>", unsafe_allow_html=True)
    
    components = ['PM2.5', 'PM10', 'NO₂', 'SO₂', 'O₃']
    cat_low = [50, 60, 40, 70, 55]
    cat_mod = [30, 45, 25, 15, 30]
    cat_unhealth = [20, 15, 35, 15, 15]
    
    fig_stack = go.Figure(data=[
        go.Bar(name='Low', x=components, y=cat_low, marker_color='#10b981'),
        go.Bar(name='Moderate', x=components, y=cat_mod, marker_color='#eab308'),
        go.Bar(name='Unhealthy', x=components, y=cat_unhealth, marker_color='#ef4444')
    ])
    fig_stack.update_layout(barmode='stack', height=140, margin=dict(t=10, b=10, l=10, r=10), template="plotly_dark",
                            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", showlegend=False)
    st.plotly_chart(fig_stack, use_container_width=True, config={'displayModeBar': False})
    st.markdown('</div>', unsafe_allow_html=True)

# ด้านล่างขวา: ตารางตรวจสอบคุณภาพน้ำ (Water Quality Monitoring)
with bottom_col2:
    st.markdown('<div class="panel-card">', unsafe_allow_html=True)
    st.markdown("<div class='panel-label'>WATER QUALITY MONITORING (MAJOR RIVERS)</div>", unsafe_allow_html=True)
    
    # ดึงค่าสถานะมาแปรผันตามภูมิภาคเพื่อให้ตารางสัมพันธ์กับสเปกด้านบน
    status_badge = "🟢 ผ่านเกณฑ์" if data["co2"] < 420 else "🟡 เฝ้าระวัง"
    
    water_data = pd.DataFrame({
        'River Station (ลำน้ำ)': ['Chao Phraya (เจ้าพระยา)', 'Tha Chin (ท่าจีน)', 'Mae Klong (แม่กลอง)'],
        'DO (ออกซิเจนละลาย)': ['4.2 mg/L', '2.1 mg/L', '5.5 mg/L'],
        'Status (ประเมิน)': [status_badge, '🔴 ต่ำกว่าเกณฑ์', '🟢 ผ่านเกณฑ์']
    })
    
    st.dataframe(water_data, hide_index=True, use_container_width=True, height=135)
    st.markdown('</div>', unsafe_allow_html=True)
