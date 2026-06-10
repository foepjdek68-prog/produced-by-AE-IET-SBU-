import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# 1. PAGE INITIALIZATION (ล็อกสเกลหน้าจอระบบแดชบอร์ดความหนาแน่นสูง)
st.set_page_config(layout="wide", page_title="Intelligent Environmental Dashboard")

# 2. ADVANCED ULTRA-COMPACT CSS (คุมโทนสี สเกล และล็อกช่อง Selectbox ห้ามพิมพ์)
st.markdown("""
    <style>
        /* ซ่อน Scrollbar ส่วนเกินเพื่อให้ข้อมูลกระชับอยู่ในหน้าเดียว */
        ::-webkit-scrollbar { display: none; }
        
        html, body, [data-testid="stAppViewContainer"] { 
            background-color: #111827 !important;
            color: #ffffff !important;
            font-family: 'Inter', sans-serif;
        }
        .block-container { padding: 0.8rem 1.5rem !important; }
        
        /* หัวข้อหลักสไตล์เดียวกับอินโฟกราฟิก */
        .header-box { text-align: center; margin-bottom: 8px; }
        .hdr-title { font-size: 20px; font-weight: 800; color: #ffffff; letter-spacing: 0.8px; margin: 0; }
        .hdr-sub { font-size: 13px; color: #94a3b8; margin-top: 1px; font-weight: 500; }
        
        /* แถบเมนูควบคุม (Control Panel Layer) */
        .control-strip {
            background-color: #1f2937; padding: 4px 12px; border-radius: 6px;
            border: 1px solid #374151; margin-bottom: 12px;
        }
        
        /* กล่องคอนเทนเนอร์แยกส่วนเนื้อหา (Dashboard Widget Cards) */
        .section-card {
            background-color: #1f2937; border: 1px solid #374151; border-radius: 6px;
            padding: 10px; height: 100%; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        }
        .card-header-text { 
            font-size: 11px; color: #38bdf8; font-weight: 700; 
            margin-bottom: 8px; text-transform: uppercase; letter-spacing: 0.5px;
        }
        
        /* 🔒 [CRITICAL HACK] สั่งล็อกช่อง Input ของ Streamlit Selectbox ทั้งหมด ห้ามเปิดคีย์บอร์ดพิมพ์ */
        div[data-baseweb="select"] input {
            pointer-events: none !important;
            caret-color: transparent !important;
        }
        div[data-baseweb="select"] { background-color: #111827 !important; border: 1px solid #4b5563 !important; border-radius: 4px; }
        div[data-baseweb="select"] * { color: #ffffff !important; font-size: 11px !important; }
        label[data-testid="stWidgetLabel"] { font-size: 11px !important; color: #94a3b8 !important; margin-bottom: 1px !important; font-weight: bold; }
        
        /* ป้ายสถานะสำหรับตารางตรวจวัดคุณภาพน้ำด้านล่าง */
        .status-badge {
            padding: 2px 8px; border-radius: 12px; font-size: 10px; font-weight: bold; display: inline-block; text-align: center;
        }
        .bg-success { background-color: #059669; color: #ffffff; }
        .bg-danger { background-color: #dc2626; color: #ffffff; }
    </style>
""", unsafe_allow_html=True)

# 3. STATIC DATA DICTIONARY (คลังข้อมูลสำหรับเชื่อมโยงสเกลภูมิภาค)
years_x = [1930, 1950, 1970, 1990, 2000, 2010, 2026]
months_x = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

DASHBOARD_DATA = {
    "📌 CENTRAL": {
        "co2": 421.5, "temp": 1.8, "aqi": 85, "aqi_status": "Moderate",
        "co2_history": [240, 310, 480, 620, 780, 950, 1380],
        "monthly_temp": [12, 11, 13, 15, 18, 22, 21, 19, 14, 12, 11, 10],
        "monthly_pm25": [24, 25, 26, 28, 30, 32, 29, 27, 25, 23, 22, 24]
    },
    "📌 NORTH": {
        "co2": 412.8, "temp": 2.4, "aqi": 165, "aqi_status": "Unhealthy",
        "co2_history": [210, 280, 410, 540, 690, 810, 1120],
        "monthly_temp": [10, 12, 16, 20, 24, 26, 25, 23, 19, 15, 12, 9],
        "monthly_pm25": [45, 65, 95, 120, 80, 35, 20, 18, 25, 40, 55, 50]
    }
}

# 4. DASHBOARD HEADER TITLE
st.markdown("""
<div class="header-box">
    <div class="hdr-title">INTELLIGENT ENVIRONMENTAL & GHG MONITORING DASHBOARD (THAILAND)</div>
    <div class="hdr-sub">แดชบอร์ดอัจฉริยะติดตามก๊าซเรือนกระจกและมลพิษทางอากาศ (สเกลมาตรฐานความแม่นยำสูง)</div>
</div>
""", unsafe_allow_html=True)

# 5. CONTROL PANEL STRIP (รวมตัวเลือกไว้ในแถวเดียว กะทัดรัด ไม่ดันหน้าจอลงลึก)
st.markdown('<div class="control-strip">', unsafe_allow_html=True)
ctrl_1, ctrl_2, ctrl_3, ctrl_4 = st.columns([2.2, 2.6, 2.6, 2.6])
with ctrl_1:
    st.markdown('<div style="font-family:monospace; font-size:12px; color:#38bdf8; font-weight:700; margin-top:16px;">⏱️ MARCH 2026 | 13:58:55</div>', unsafe_allow_html=True)
with ctrl_2:
    selected_region = st.selectbox("REGION (ภูมิภาค)", list(DASHBOARD_DATA.keys()))
with ctrl_3:
    selected_source = st.selectbox("DATA SOURCE (แหล่งอ้างอิง)", ["ALL STATIONS (รวมทุกสถานี)", "GROUND STATION", "SATELLITE API"])
with ctrl_4:
    selected_time = st.selectbox("TIME FILTER (ช่วงเวลา)", ["1 MONTH", "6 MONTHS", "1 YEAR", "30 YEARS"])
st.markdown('</div>', unsafe_allow_html=True)

# ดึงชุดข้อมูลตามภูมิภาคที่จิ้มเลือกจริงมาคำนวณแบบพลวัต (Dynamic)
active_set = DASHBOARD_DATA[selected_region]

# ==========================================
# TIER 2: KEY ENVIRONMENTAL METRICS (3 GAUGE CHARTS ROW)
# ==========================================
g_col1, g_col2, g_col3 = st.columns(3)

with g_col1:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    fig_g1 = go.Figure(go.Indicator(
        mode="gauge+number", value=active_set["co2"],
        title={'text': "1. ATMOSPHERIC CO₂ LEVEL", 'font': {'size': 11, 'color': '#94a3b8', 'bold': True}},
        number={'suffix': " ppm", 'font': {'size': 22, 'color': '#ffffff'}},
        gauge={'axis': {'range': [300, 500]}, 'bar': {'color': "#22d3ee"}, 'bgcolor': "#111827"}
    ))
    fig_g1.update_layout(height=105, margin=dict(t=20, b=5, l=20, r=20), paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig_g1, use_container_width=True, config={'displayModeBar': False})
    st.markdown('</div>', unsafe_allow_html=True)

with g_col2:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    fig_g2 = go.Figure(go.Indicator(
        mode="gauge+number", value=active_set["temp"],
        title={'text': "2. AV. TEMPERATURE ANOMALY", 'font': {'size': 11, 'color': '#94a3b8', 'bold': True}},
        number={'prefix': "+", 'suffix': " °C", 'font': {'size': 22, 'color': '#f97316'}},
        gauge={'axis': {'range': [0, 4]}, 'bar': {'color': "#f97316"}, 'bgcolor': "#111827"}
    ))
    fig_g2.update_layout(height=105, margin=dict(t=20, b=5, l=20, r=20), paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig_g2, use_container_width=True, config={'displayModeBar': False})
    st.markdown('</div>', unsafe_allow_html=True)

with g_col3:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    aqi_color = "#eab308" if active_set["aqi"] <= 100 else "#ef4444"
    fig_g3 = go.Figure(go.Indicator(
        mode="gauge+number", value=active_set["aqi"],
        title={'text': f"3. AIR QUALITY INDEX ({active_set['aqi_status']})", 'font': {'size': 11, 'color': '#94a3b8', 'bold': True}},
        number={'font': {'size': 22, 'color': aqi_color}},
        gauge={'axis': {'range': [0, 200]}, 'bar': {'color': aqi_color}, 'bgcolor': "#111827"}
    ))
    fig_g3.update_layout(height=105, margin=dict(t=20, b=5, l=20, r=20), paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig_g3, use_container_width=True, config={'displayModeBar': False})
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<div style='margin-bottom: 10px;'></div>", unsafe_allow_html=True)

# ==========================================
# TIER 3: MIDDLE SECTION (MAP & CHARTS SPLIT 50/50)
# ==========================================
mid_left, mid_right = st.columns([1.1, 1.0])

# ฝั่งซ้าย: แผนที่ Hotspot มลพิษทางอากาศ
with mid_left:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="card-header-text">🔥 GHG & POLLUTION HOTSPOTS (BANGKOK & PERIPHERY)</div>', unsafe_allow_html=True)
    
    # สร้างจุดสุ่มจำลองค่าหนาแน่นบริเวณกรุงเทพฯ และปริมณฑล
    np.random.seed(10)
    map_data = pd.DataFrame({
        'lat': [13.7563, 13.6592, 13.8124, 13.5432, 14.0204, 13.7234, 13.9122, 13.6122],
        'lon': [100.5018, 100.6024, 100.4124, 100.2642, 100.6145, 100.3245, 100.5123, 100.7421],
        'value': [150, 120, 145, 85, 95, 110, 135, 70]
    })
    fig_map = px.density_mapbox(map_data, lat='lat', lon='lon', z='value', radius=28,
                                center=dict(lat=13.7563, lon=100.5218), zoom=8.5,
                                mapbox_style="carto-darkmatter", color_continuous_scale="Jet")
    fig_map.update_layout(height=265, margin=dict(t=0, b=0, l=0, r=0), coloraxis_showscale=False)
    st.plotly_chart(fig_map, use_container_width=True, config={'displayModeBar': False})
    st.markdown('</div>', unsafe_allow_html=True)

# ฝั่งขวา: กราฟซ้อนกัน 2 ชุดตามต้นแบบเป๊ะๆ
with mid_right:
    # 1. กราฟแนวโน้ม 30 ปี (บน)
    st.markdown('<div class="section-card" style="margin-bottom: 8px;">', unsafe_allow_html=True)
    st.markdown('<div class="card-header-text">📈 30-YEAR CO₂ EMISSIONS TREND (KT/YR)</div>', unsafe_allow_html=True)
    df_30y = pd.DataFrame({'Year': years_x, 'CO2': active_set["co2_history"]})
    fig_line1 = px.area(df_30y, x='Year', y='CO2', template="plotly_dark")
    fig_line1.update_traces(line=dict(color='#38bdf8', width=2), fillcolor='rgba(56, 189, 248, 0.1)')
    fig_line1.update_layout(height=100, margin=dict(t=5, b=5, l=10, r=10), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", xaxis_showgrid=False, yaxis_showgrid=False)
    st.plotly_chart(fig_line1, use_container_width=True, config={'displayModeBar': False})
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 2. กราฟความสัมพันธ์รายเดือน (ล่าง)
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="card-header-text">📊 MONTHLY TEMPERATURE VS. AIR QUALITY</div>', unsafe_allow_html=True)
    fig_combo = go.Figure()
    fig_combo.add_trace(go.Bar(x=months_x, y=active_set["monthly_pm25"], name='PM2.5', marker_color='#f97316', yaxis='y1'))
    fig_combo.add_trace(go.Scatter(x=months_x, y=active_set["monthly_temp"], name='Temp', line=dict(color='#38bdf8', width=2), yaxis='y2'))
    fig_combo.update_layout(
        height=100, margin=dict(t=5, b=5, l=10, r=10), template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", showlegend=False,
        xaxis_showgrid=False, yaxis_showgrid=False,
        yaxis=dict(side='left'), yaxis2=dict(overlaying='y', side='right')
    )
    st.plotly_chart(fig_combo, use_container_width=True, config={'displayModeBar': False})
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<div style='margin-bottom: 10px;'></div>", unsafe_allow_html=True)

# ==========================================
# TIER 4: BOTTOM SECTION (ANALYTICS & RIVER QUALITY STATUS)
# ==========================================
bot_left, bot_right = st.columns([1.1, 1.0])

with bot_left:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="card-header-text">📊 POLLUTION BREAKDOWN (PM2.5, NO₂, SO₂)</div>', unsafe_allow_html=True)
    elements = ['PM2.5', 'PM10', 'NO₂', 'SO₂']
    fig_stack = go.Figure(data=[
        go.Bar(name='Low', x=elements, y=[80, 90, 110, 130], marker_color='#059669'),
        go.Bar(name='Moderate', x=elements, y=[60, 70, 50, 40], marker_color='#d97706'),
        go.Bar(name='Unhealthy', x=elements, y=[100, 40, 60, 20], marker_color='#dc2626')
    ])
    fig_stack.update_layout(barmode='stack', height=105, margin=dict(t=5, b=5, l=5, r=5), template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", showlegend=False)
    st.plotly_chart(fig_stack, use_container_width=True, config={'displayModeBar': False})
    st.markdown('</div>', unsafe_allow_html=True)

with bot_right:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="card-header-text">💧 WATER QUALITY MONITORING (MAJOR RIVERS)</div>', unsafe_allow_html=True)
    
    # ดึงตารางดีไซน์เลียนแบบแผงรายชื่อแม่น้ำพร้อมป้ายไฟสีเขียว/แดงตามแบบอินโฟกราฟิก
    html_table = """
    <table style="width:100%; border-collapse: collapse; font-size:11px; color:#ffffff;">
        <tr style="border-bottom: 1px solid #374151; color:#94a3b8; font-weight:bold;">
            <th style="text-align:left; padding: 4px;">River Station</th>
            <th style="text-align:center; padding: 4px;">DO STATUS</th>
            <th style="text-align:center; padding: 4px;">COD STATUS</th>
        </tr>
        <tr style="border-bottom: 1px solid #374151;">
            <td style="padding: 6px; font-weight:bold; color:#38bdf8;">🔵 Chao Phraya (⚡ Main)</td>
            <td style="text-align:center;"><span class="status-badge bg-success">DO PASS</span></td>
            <td style="text-align:center;"><span class="status-badge bg-danger">COD WARN</span></td>
        </tr>
        <tr style="border-bottom: 1px solid #374151;">
            <td style="padding: 6px; font-weight:bold; color:#38bdf8;">🔵 Tha Chin (Station A)</td>
            <td style="text-align:center;"><span class="status-badge bg-success">DO PASS</span></td>
            <td style="text-align:center;"><span class="status-badge bg-success">COD PASS</span></td>
        </tr>
        <tr>
            <td style="padding: 6px; font-weight:bold; color:#38bdf8;">🔵 Mae Klong (Delta)</td>
            <td style="text-align:center;"><span class="status-badge bg-success">DO PASS</span></td>
            <td style="text-align:center;"><span class="status-badge bg-danger">COD WARN</span></td>
        </tr>
    </table>
    """
    st.markdown(html_table, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
