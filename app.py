import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

# ==========================================
# 1. PAGE CONFIGURATION & THEME MATCHING
# ==========================================
st.set_page_config(layout="wide", page_title="Intelligent Environmental Dashboard", page_icon="🌍")

# ฝัง Ultra-Compact CSS เพื่อคุม Layout ให้กระชับอยู่ในหน้าเดียว และล็อกช่อง Selectbox ไม่ให้คีย์บอร์ดเด้ง
st.markdown("""
    <style>
        /* ซ่อน Scrollbar ส่วนเกินให้หน้าจอดูกระชับแบบแดชบอร์ดระดับมืออาชีพ */
        ::-webkit-scrollbar { display: none; }
        
        html, body, [data-testid="stAppViewContainer"] { 
            background-color: #020617 !important;
            color: #f8fafc !important;
            font-family: 'Inter', 'Sarabun', sans-serif;
        }
        .block-container { padding: 1rem 2rem !important; }
        
        /* สไตล์กล่องหัวข้อหลัก (Header Area) */
        .header-container { text-align: center; margin-bottom: 12px; }
        .main-title { font-size: 24px; font-weight: 800; color: #ffffff; letter-spacing: 0.5px; margin: 0; }
        .sub-title { font-size: 14px; color: #94a3b8; margin-top: 2px; font-weight: 500; }
        
        /* แถบควบคุม (Control Strip) */
        .control-strip {
            background-color: #1e293b; padding: 6px 16px; border-radius: 8px;
            border: 1px solid #334155; margin-bottom: 16px;
        }
        
        /* กล่องวิดเจ็ตการ์ดแสดงผล (Dashboard Component Cards) */
        .widget-card {
            background-color: #1e293b; border: 1px solid #334155; border-radius: 8px;
            padding: 12px; height: 100%; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
        }
        .widget-header { 
            font-size: 12px; color: #22d3ee; font-weight: 700; 
            margin-bottom: 8px; text-transform: uppercase; letter-spacing: 0.5px;
        }
        
        /* 🔒 ล็อกอินพุตของ Streamlit Selectbox ทั้งหมด ห้ามเปิดแป้นพิมพ์เวลาทัชใช้งาน */
        div[data-baseweb="select"] input {
            pointer-events: none !important;
            caret-color: transparent !important;
        }
        div[data-baseweb="select"] { background-color: #020617 !important; border: 1px solid #475569 !important; border-radius: 6px; }
        div[data-baseweb="select"] * { color: #f8fafc !important; font-size: 12px !important; }
        label[data-testid="stWidgetLabel"] { font-size: 11px !important; color: #94a3b8 !important; margin-bottom: 2px !important; font-weight: bold; }
        
        /* ป้ายไฟสถานะสำหรับระบบตรวจวัดคุณภาพน้ำ */
        .badge { padding: 3px 10px; border-radius: 20px; font-size: 10px; font-weight: 800; display: inline-block; text-align: center; }
        .badge-pass { background-color: #059669; color: #ffffff; }
        .badge-warn { background-color: #dc2626; color: #ffffff; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. DYNAMIC MOCK DATA ENGINE (คลังข้อมูลเชื่อมโยงภูมิภาค)
# ==========================================
years_axis = [1930, 1950, 1970, 1990, 2000, 2010, 2026]
months_axis = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

REGIONAL_DB = {
    "📌 CENTRAL (ภาคกลาง)": {
        "co2": 421.5, "co2_change": "+0.3% vs last month", "temp": 1.8, "aqi": 85, "aqi_text": "Moderate", "aqi_color": "#eab308",
        "co2_trend": [240, 320, 490, 680, 820, 990, 1420],
        "pm25_monthly": [22, 26, 35, 40, 28, 18, 15, 14, 19, 23, 25, 30],
        "temp_monthly": [26, 28, 30, 32, 31, 30, 29, 29, 28, 27, 26, 25]
    },
    "📌 NORTH (ภาคเหนือ)": {
        "co2": 412.8, "co2_change": "+0.1% vs last month", "temp": 2.4, "aqi": 165, "aqi_text": "Unhealthy", "aqi_color": "#ef4444",
        "co2_trend": [210, 270, 410, 550, 690, 840, 1150],
        "pm25_monthly": [45, 68, 95, 120, 75, 30, 22, 19, 24, 38, 48, 55],
        "temp_monthly": [20, 23, 27, 31, 30, 29, 28, 28, 27, 25, 22, 19]
    },
    "📌 SOUTH (ภาคใต้)": {
        "co2": 405.2, "co2_change": "-0.05% vs last month", "temp": 0.9, "aqi": 35, "aqi_text": "Good", "aqi_color": "#22c55e",
        "co2_trend": [200, 250, 350, 460, 580, 710, 920],
        "pm25_monthly": [15, 18, 20, 17, 14, 12, 11, 13, 15, 16, 14, 13],
        "temp_monthly": [25, 26, 28, 29, 29, 28, 28, 28, 27, 27, 26, 25]
    }
}

# ==========================================
# 3. HEADER SECTION
# ==========================================
st.markdown("""
<div class="header-container">
    <div class="main-title">INTELLIGENT ENVIRONMENTAL & GHG MONITORING DASHBOARD (THAILAND)</div>
    <div class="sub-title">แดชบอร์ดอัจฉริยะติดตามก๊าซเรือนกระจกและมลพิษทางอากาศ (ระบบคำนวณพิกัดความละเอียดสูง)</div>
</div>
""", unsafe_allow_html=True)

# ==========================================
# 4. TOP CONTROL STRIP (แถบเมนูควบคุมระดับบนสุดเรียงเป็นแถวเดียว)
# ==========================================
st.markdown('<div class="control-strip">', unsafe_allow_html=True)
c1, c2, c3, c4 = st.columns([2.5, 2.5, 2.5, 2.5])
with c1:
    current_time = datetime.now().strftime("%B %Y | %H:%M:%S")
    st.markdown(f'<div style="font-family:monospace; font-size:13px; color:#22d3ee; font-weight:700; margin-top:16px;">⏱️ {current_time.upper()}</div>', unsafe_allow_html=True)
with c2:
    selected_reg = st.selectbox("REGION (เลือกภูมิภาค)", list(REGIONAL_DB.keys()))
with c3:
    st.selectbox("DATA SOURCE (แหล่งข้อมูล)", ["ALL STATIONS (รวมทุกสถานี)", "GROUND MONITORING", "SATELLITE REMOTE SENSING"])
with c4:
    st.selectbox("TIME RANGE (ช่วงเวลาข้อมูล)", ["1 MONTH (รายเดือน)", "6 MONTHS", "1 YEAR", "30 YEARS TREND"])
st.markdown('</div>', unsafe_allow_html=True)

# ดึงชุดข้อมูลภูมิภาคที่ผู้ใช้เลือกมาคำนวณแบบพลวัต
data = REGIONAL_DB[selected_reg]

# ==========================================
# 5. TIER 1: KEY ENVIRONMENTAL METRICS (3 GAUGE CHARTS)
# ==========================================
g1, g2, g3 = st.columns(3)

# เกจวัดชุดที่ 1: CO2 Level
with g1:
    st.markdown('<div class="widget-card">', unsafe_allow_html=True)
    fig_g1 = go.Figure(go.Indicator(
        mode="gauge+number", value=data["co2"],
        title={'text': "1 🔵 ATMOSPHERIC CO₂ LEVEL", 'font': {'size': 12, 'color': '#94a3b8', 'bold': True}},
        number={'suffix': " ppm", 'font': {'size': 24, 'color': '#ffffff'}},
        gauge={
            'axis': {'range': [350, 500], 'tickwidth': 1, 'tickcolor': "#94a3b8"},
            'bar': {'color': "#22d3ee"}, 'bgcolor': "#020617",
            'steps': [{'range': [350, 420], 'color': '#0f172a'}, {'range': [420, 500], 'color': '#334155'}]
        }
    ))
    fig_g1.update_layout(height=110, margin=dict(t=25, b=5, l=25, r=25), paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig_g1, use_container_width=True, config={'displayModeBar': False})
    st.markdown(f'<div style="text-align:center; font-size:11px; color:#22d3ee; font-weight:bold; margin-top:-5px;">{data["co2_change"]}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# เกจวัดชุดที่ 2: Temperature Anomaly
with g2:
    st.markdown('<div class="widget-card">', unsafe_allow_html=True)
    fig_g2 = go.Figure(go.Indicator(
        mode="gauge+number", value=data["temp"],
        title={'text': "2 🟠 AV. TEMPERATURE ANOMALY", 'font': {'size': 12, 'color': '#94a3b8', 'bold': True}},
        number={'prefix': "+", 'suffix': " °C", 'font': {'size': 24, 'color': '#f97316'}},
        gauge={
            'axis': {'range': [0, 4], 'tickwidth': 1, 'tickcolor': "#94a3b8"},
            'bar': {'color': "#f97316"}, 'bgcolor': "#020617",
            'steps': [{'range': [0, 1.5], 'color': '#0f172a'}, {'range': [1.5, 4], 'color': '#334155'}]
        }
    ))
    fig_g2.update_layout(height=110, margin=dict(t=25, b=5, l=25, r=25), paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig_g2, use_container_width=True, config={'displayModeBar': False})
    st.markdown('<div style="text-align:center; font-size:11px; color:#f97316; font-weight:bold; margin-top:-5px;">▲ ABOVE HISTORICAL BASELINE</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# เกจวัดชุดที่ 3: AQI Index
with g3:
    st.markdown('<div class="widget-card">', unsafe_allow_html=True)
    fig_g3 = go.Figure(go.Indicator(
        mode="gauge+number", value=data["aqi"],
        title={'text': f"3 🟡 AIR QUALITY INDEX ({data['aqi_text'].upper()})", 'font': {'size': 12, 'color': '#94a3b8', 'bold': True}},
        number={'font': {'size': 24, 'color': data["aqi_color"]}},
        gauge={
            'axis': {'range': [0, 200], 'tickwidth': 1, 'tickcolor': "#94a3b8"},
            'bar': {'color': data["aqi_color"]}, 'bgcolor': "#020617",
            'steps': [
                {'range': [0, 50], 'color': 'rgba(34, 197, 94, 0.1)'},
                {'range': [50, 100], 'color': 'rgba(234, 179, 8, 0.1)'},
                {'range': [100, 200], 'color': 'rgba(239, 68, 68, 0.1)'}
            ]
        }
    ))
    fig_g3.update_layout(height=110, margin=dict(t=25, b=5, l=25, r=25), paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig_g3, use_container_width=True, config={'displayModeBar': False})
    st.markdown(f'<div style="text-align:center; font-size:11px; color:{data["aqi_color"]}; font-weight:bold; margin-top:-5px;">STATUS: {data["aqi_text"]}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<div style='margin-bottom: 12px;'></div>", unsafe_allow_html=True)

# ==========================================
# 6. TIER 2: MIDDLE SECTION (MAP & CHARTS SPLIT 50/50)
# ==========================================
mid_left, mid_right = st.columns([1.1, 1.0])

# ฝั่งซ้าย: แผนที่ความหนาแน่นมลพิษกรุงเทพฯ และปริมณฑล
with mid_left:
    st.markdown('<div class="widget-card">', unsafe_allow_html=True)
    st.markdown('<div class="widget-header">🔥 GHG & POLLUTION HOTSPOTS (BANGKOK & PERIPHERY)</div>', unsafe_allow_html=True)
    
    # พิกัดสุ่มจำลองสำหรับจุดความร้อนในพื้นที่กรุงเทพฯ
    np.random.seed(42)
    map_df = pd.DataFrame({
        'lat': [13.7563, 13.6592, 13.8124, 13.5432, 14.0204, 13.7234, 13.9122, 13.6122],
        'lon': [100.5018, 100.6024, 100.4124, 100.2642, 100.6145, 100.3245, 100.5123, 100.7421],
        'intensity': [160, 110, 145, 75, 90, 115, 130, 65]
    })
    
    fig_map = px.density_mapbox(map_df, lat='lat', lon='lon', z='intensity', radius=25,
                                center=dict(lat=13.7563, lon=100.5218), zoom=8.6,
                                mapbox_style="carto-darkmatter", color_continuous_scale="Jet")
    fig_map.update_layout(height=260, margin=dict(t=0, b=0, l=0, r=0), coloraxis_showscale=False)
    st.plotly_chart(fig_map, use_container_width=True, config={'displayModeBar': False})
    st.markdown('</div>', unsafe_allow_html=True)

# ฝั่งขวา: กราฟสถิติ 2 บล็อกวางแนวตั้งซ้อนกันแบบพิมพ์เขียว
with mid_right:
    # บล็อกบน: กราฟแนวพื้นที่สะสม 30 ปี
    st.markdown('<div class="widget-card" style="margin-bottom: 10px;">', unsafe_allow_html=True)
    st.markdown('<div class="widget-header">📈 30-YEAR CO₂ EMISSIONS TREND (KT/YR)</div>', unsafe_allow_html=True)
    trend_df = pd.DataFrame({'Year': years_axis, 'Emissions': data["co2_trend"]})
    fig_trend = px.area(trend_df, x='Year', y='Emissions', template="plotly_dark")
    fig_trend.update_traces(line=dict(color='#22d3ee', width=2), fillcolor='rgba(34, 211, 238, 0.15)')
    fig_trend.update_layout(
        height=95, margin=dict(t=5, b=5, l=15, r=15), paper_bgcolor="rgba(0,0,0,0)", 
        plot_bgcolor="rgba(0,0,0,0)", xaxis_showgrid=False, yaxis_showgrid=False
    )
    st.plotly_chart(fig_trend, use_container_width=True, config={'displayModeBar': False})
    st.markdown('</div>', unsafe_allow_html=True)
    
    # บล็อกล่าง: กราฟความสัมพันธ์รายเดือน อุณหภูมิ VS ฝุ่น
    st.markdown('<div class="widget-card">', unsafe_allow_html=True)
    st.markdown('<div class="widget-header">📊 MONTHLY TEMPERATURE VS. AIR QUALITY</div>', unsafe_allow_html=True)
    fig_combo = go.Figure()
    fig_combo.add_trace(go.Bar(x=months_axis, y=data["pm25_monthly"], name='PM2.5', marker_color='#f97316', yaxis='y1'))
    fig_combo.add_trace(go.Scatter(x=months_axis, y=data["temp_monthly"], name='Temperature', line=dict(color='#22d3ee', width=2.5), yaxis='y2'))
    fig_combo.update_layout(
        height=95, margin=dict(t=5, b=5, l=15, r=15), template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", showlegend=False,
        xaxis_showgrid=False, yaxis_showgrid=False,
        yaxis=dict(side='left', title_font=dict(size=10)), yaxis2=dict(overlaying='y', side='right', title_font=dict(size=10))
    )
    st.plotly_chart(fig_combo, use_container_width=True, config={'displayModeBar': False})
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<div style='margin-bottom: 12px;'></div>", unsafe_allow_html=True)

# ==========================================
# 7. TIER 3: BOTTOM SECTION (ANALYTICS & RIVER QUALITY STATUS)
# ==========================================
bot_left, bot_right = st.columns([1.1, 1.0])

# ฝั่งซ้าย: กราฟแท่งจำแนกประเภทสารพิษ
with bot_left:
    st.markdown('<div class="widget-card">', unsafe_allow_html=True)
    st.markdown('<div class="widget-header">📊 POLLUTION BREAKDOWN (PM2.5, NO₂, SO₂)</div>', unsafe_allow_html=True)
    pollutants = ['PM2.5', 'PM10', 'NO₂', 'O₃', 'SO₂']
    fig_stack = go.Figure(data=[
        go.Bar(name='Low (ปลอดภัย)', x=pollutants, y=[70, 85, 120, 90, 110], marker_color='#059669'),
        go.Bar(name='Moderate (ปานกลาง)', x=pollutants, y=[50, 60, 45, 55, 40], marker_color='#d97706'),
        go.Bar(name='Unhealthy (อันตราย)', x=pollutants, y=[95, 35, 50, 20, 15], marker_color='#dc2626')
    ])
    fig_stack.update_layout(barmode='stack', height=110, margin=dict(t=5, b=5, l=5, r=5), template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", showlegend=False)
    st.plotly_chart(fig_stack, use_container_width=True, config={'displayModeBar': False})
    st.markdown('</div>', unsafe_allow_html=True)

# ฝั่งขวา: ตารางตรวจวัดคุณภาพน้ำในแม่น้ำ พร้อมปุ่มดาวน์โหลดรายงานข้อมูล
with bot_right:
    st.markdown('<div class="widget-card">', unsafe_allow_html=True)
    st.markdown('<div class="widget-header">💧 WATER QUALITY MONITORING (MAJOR RIVERS)</div>', unsafe_allow_html=True)
    
    # ตารางรูปแบบ HTML คุมสีและติดป้ายไฟสถานะ เขียว-แดง ตามอินโฟกราฟิกเป้าหมาย
    html_table = """
    <table style="width:100%; border-collapse: collapse; font-size:11px; color:#ffffff; margin-bottom: 8px;">
        <tr style="border-bottom: 1px solid #334155; color:#94a3b8; font-weight:bold; text-align:left;">
            <th style="padding: 4px;">River Station</th>
            <th style="text-align:center; padding: 4px;">DO STATUS</th>
            <th style="text-align:center; padding: 4px;">COD STATUS</th>
        </tr>
        <tr style="border-bottom: 1px solid #334155;">
            <td style="padding: 5px; font-weight:700; color:#22d3ee;">🔵 Chao Phraya (⚡ Main Station)</td>
            <td style="text-align:center;"><span class="badge badge-pass">DO PASS</span></td>
            <td style="text-align:center;"><span class="badge badge-warn">COD WARN</span></td>
        </tr>
        <tr style="border-bottom: 1px solid #334155;">
            <td style="padding: 5px; font-weight:700; color:#22d3ee;">🔵 Tha Chin (Delta Area)</td>
            <td style="text-align:center;"><span class="badge badge-pass">DO PASS</span></td>
            <td style="text-align:center;"><span class="badge badge-pass">DO PASS</span></td>
        </tr>
        <tr>
            <td style="padding: 5px; font-weight:700; color:#22d3ee;">🔵 Mae Klong (Estuary)</td>
            <td style="text-align:center;"><span class="badge badge-pass">DO PASS</span></td>
            <td style="text-align:center;"><span class="badge badge-warn">COD WARN</span></td>
        </tr>
    </table>
    """
    st.markdown(html_table, unsafe_allow_html=True)
    
    # 📥 ฟังก์ชันปุ่มดาวน์โหลดไฟล์ข้อมูลจริง (.CSV)
    report_df = pd.DataFrame({
        'Metric': ['CO2 (ppm)', 'Temp Anomaly (C)', 'AQI Index'],
        'Value': [data["co2"], data["temp"], data["aqi"]],
        'Status': ['Monitored', 'Above Baseline', data["aqi_text"]],
        'Last_Sync': [datetime.now().strftime("%Y-%m-%d %H:%M:%S")] * 3
    })
    csv_bytes = report_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 DOWNLOAD REGIONAL ENVIRONMENTAL REPORT (.CSV)",
        data=csv_bytes,
        file_name=f"environmental_report_{selected_reg.split()[1].lower()}.csv",
        mime="text/csv"
    )
    st.markdown('</div>', unsafe_allow_html=True)
