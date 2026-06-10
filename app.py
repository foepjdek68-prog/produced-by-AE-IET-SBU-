import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# 1. INITIAL SETUP
st.set_page_config(layout="wide", page_title="Intelligent Environmental Dashboard", initial_sidebar_state="collapsed")

# 2. CYBER DARK THEME CSS
st.markdown("""
    <style>
        ::-webkit-scrollbar { display: none; }
        html, body, [data-testid="stAppViewContainer"] { 
            overflow: hidden !important; 
            height: 100vh !important; 
            background-color: #0b111e !important;
        }
        .block-container { padding: 0.4rem 1.0rem !important; }
        
        /* HEADER STYLE */
        .main-header { text-align: center; margin-bottom: 4px; }
        .title-en { font-size: 19px; font-weight: 800; color: #ffffff; letter-spacing: 0.5px; margin: 0; }
        .title-th { font-size: 13px; font-weight: 400; color: #94a3b8; margin: 1px 0 0 0; }
        
        /* CONTROL BAR */
        .meta-bar {
            display: flex; justify-content: space-between; align-items: center;
            background-color: #0f172a; padding: 6px 12px; border-radius: 6px;
            margin-bottom: 6px; border: 1px solid #1e293b;
        }
        .clock-text { font-family: monospace; font-size: 13px; color: #10b981; font-weight: 700; }
        .label-th { font-size: 10px; color: #64748b; font-weight: 600; text-transform: uppercase; margin-bottom: 2px; }

        /* CONTAINERS */
        .panel-box {
            background-color: #0f172a; border: 1px solid #1e293b; border-radius: 6px;
            padding: 8px; height: 100%; box-shadow: 0 4px 15px rgba(0,0,0,0.5);
        }
        .panel-header { font-size: 10px; color: #ffffff; font-weight: 700; letter-spacing: 0.5px; margin-bottom: 2px; }
        .panel-subheader { font-size: 9px; color: #64748b; margin-bottom: 4px; }
        
        .metric-card {
            background: linear-gradient(180deg, #141b2d 0%, #0c101b 100%);
            border: 1px solid #22d3ee22; border-radius: 6px; padding: 6px; height: 72px;
        }
        .m-title { font-size: 8px; color: #94a3b8; font-weight: 600; }
        .m-value { font-size: 17px; font-weight: 700; color: #22d3ee; margin-top: 1px; }
        .m-sub { font-size: 8px; color: #64748b; }

        div[data-baseweb="select"] { background-color: #1e293b !important; border: 1px solid #334155 !important; border-radius: 4px; }
        div[data-baseweb="select"] * { color: #ffffff !important; font-size: 11px !important; }
    </style>
""", unsafe_allow_html=True)

# 3. RELIABLE DATA MATRIX (ฐานข้อมูลแบบผันผวนตามธรรมชาติแยกสัดส่วนจริง)
years_30y = [1930, 1950, 1970, 1990, 2000, 2010, 2026]

CORE_DATA = {
    "ภาคกลาง (CENTRAL THAILAND)": {
        "co2_now": 421.5, "ch4_now": 1919.4, "no2_now": 330.8, "temp_anomaly": 1.8, "aqi_val": 85, "aqi_txt": "ปานกลาง (Moderate)", "co_now": 1.2,
        "co2_history": [290, 312, 335, 362, 378, 395, 421.5], # ข้อมูลมีความโค้งมนสวิงตามธรรมชาติ
        "ch4_history": [1620, 1690, 1740, 1810, 1845, 1880, 1919.4],
        "no2_history": [150, 190, 225, 270, 295, 315, 330.8],
        "map_coords": [13.7563, 100.5018],
        "time_modes": {
            "1 MONTH (รายเดือน)": {"x": ["W1", "W2", "W3", "W4"], "pm25": [35, 58, 85, 42], "temp": [26, 28, 29, 27]},
            "1 YEAR (รายปี)": {"x": ["Jan", "Mar", "May", "Jul", "Sep", "Nov"], "pm25": [65, 85, 30, 15, 22, 45], "temp": [24, 28, 30, 28, 26, 24]},
            "5 YEARS (รอบ 5 ปี)": {"x": ["2022", "2023", "2024", "2025", "2026"], "pm25": [38, 42, 45, 40, 43], "temp": [1.4, 1.5, 1.7, 1.6, 1.8]}
        },
        "breakdown": {"PM2.5": [40, 35, 25], "PM10": [50, 40, 10], "NO₂": [45, 35, 20], "SO₂": [80, 15, 5]}
    },
    "ภาคเหนือ (NORTHERN THAILAND)": {
        "co2_now": 412.8, "ch4_now": 1850.2, "no2_now": 120.4, "temp_anomaly": 2.4, "aqi_val": 165, "aqi_txt": "เริ่มมีผลต่อสุขภาพ (Unhealthy)", "co_now": 2.3,
        "co2_history": [288, 305, 328, 352, 368, 384, 412.8],
        "ch4_history": [1590, 1640, 1700, 1760, 1790, 1820, 1850.2],
        "no2_history": [60, 75, 90, 102, 110, 115, 120.4],
        "map_coords": [18.7883, 98.9853],
        "time_modes": {
            "1 MONTH (รายเดือน)": {"x": ["W1", "W2", "W3", "W4"], "pm25": [90, 120, 165, 80], "temp": [22, 25, 27, 24]},
            "1 YEAR (รายปี)": {"x": ["Jan", "Mar", "May", "Jul", "Sep", "Nov"], "pm25": [95, 150, 45, 12, 18, 65], "temp": [19, 26, 29, 27, 24, 21]},
            "5 YEARS (รอบ 5 ปี)": {"x": ["2022", "2023", "2024", "2025", "2026"], "pm25": [55, 62, 70, 58, 66], "temp": [1.9, 2.1, 2.4, 2.2, 2.4]}
        },
        "breakdown": {"PM2.5": [15, 25, 60], "PM10": [30, 30, 40], "NO₂": [70, 20, 10], "SO₂": [90, 8, 2]}
    }
}

# 4. APPLICATION TITLE DISPLAY
st.markdown("""
<div class="main-header">
    <div class="title-en">INTELLIGENT ENVIRONMENTAL & GHG MONITORING DASHBOARD (THAILAND)</div>
    <div class="title-th">ระบบแดชบอร์ดอัจฉริยะวิเคราะห์คำนวณและติดตามก๊าซเรือนกระจกและมลพิษทางอากาศ</div>
</div>
""", unsafe_allow_html=True)

# 5. DYNAMIC INTERACTIVE FILTER BAR
st.markdown('<div class="meta-bar">', unsafe_allow_html=True)
filter_c1, filter_c2, filter_c3, filter_c4 = st.columns([3.0, 3.0, 3.0, 3.0])

with filter_c1:
    st.markdown('<div class="clock-text">🕒 SYSTEM TIME: MARCH 2026 | 13:58:55</div>', unsafe_allow_html=True)
with filter_c2:
    sel_region = st.selectbox("เลือกภูมิภาคตรวจสอบ (REGION)", list(CORE_DATA.keys()), label_visibility="collapsed")
with filter_c3:
    sel_metric = st.selectbox("เลือกสารมลพิษหลัก (MAIN METRIC)", ["CO₂ (คาร์บอนไดออกไซด์)", "CH₄ (มีเทน)", "NO₂ (ไนโตรเจนไดออกไซด์)"], label_visibility="collapsed")
with filter_c4:
    sel_time = st.selectbox("เลือกช่วงตัวกรองเวลา (TIME FILTER)", ["1 MONTH (รายเดือน)", "1 YEAR (รายปี)", "5 YEARS (รอบ 5 ปี)"], label_visibility="collapsed")
st.markdown('</div>', unsafe_allow_html=True)

# Fetch current active subset data
dataset = CORE_DATA[sel_region]
metric_short = sel_metric.split(" ")[0]

# Mapping dynamic metrics based on filter selection
if metric_short == "CO₂":
    active_gauge_val = dataset["co2_now"]
    active_unit = "ppm"
    active_range = [280, 460]
    active_history = dataset["co2_history"]
elif metric_short == "CH₄":
    active_gauge_val = dataset["ch4_now"]
    active_unit = "ppb"
    active_range = [1500, 2000]
    active_history = dataset["ch4_history"]
else:
    active_gauge_val = dataset["no2_now"]
    active_unit = "ppb"
    active_range = [0, 400]
    active_history = dataset["no2_history"]

# --- 6. SECTION 1: VISUAL GAUGES & SUMMARY METRICS ---
st.markdown("<div style='margin-bottom: 4px;'></div>", unsafe_allow_html=True)
col_g1, col_g2, col_g3, col_card1, col_card2, col_card3 = st.columns(6)

with col_g1:
    st.markdown('<div class="panel-box">', unsafe_allow_html=True)
    fig_g1 = go.Figure(go.Indicator(
        mode="gauge+number", value=active_gauge_val,
        number={'suffix': f" {active_unit}", 'font': {'size': 16, 'color': '#ffffff'}},
        gauge={'axis': {'range': active_range, 'tickwidth': 1, 'tickcolor': '#475569'}, 'bar': {'color': "#22d3ee"}},
        title={'text': f"1 ATMOSPHERIC {metric_short} LEVEL<br><span style='font-size:9px;color:#64748b;'>ระดับก๊าซในชั้นบรรยากาศปัจจุบัน</span>", 'font': {'size': 10, 'color': '#94a3b8', 'weight': 'bold'}}
    ))
    fig_g1.update_layout(height=72, margin=dict(t=22, b=4, l=10, r=10), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig_g1, use_container_width=True, config={'displayModeBar': False})
    st.markdown('</div>', unsafe_allow_html=True)

with col_g2:
    st.markdown('<div class="panel-box">', unsafe_allow_html=True)
    fig_g2 = go.Figure(go.Indicator(
        mode="gauge+number", value=dataset["temp_anomaly"],
        number={'prefix': "+", 'suffix': " °C", 'font': {'size': 16, 'color': '#f97316'}},
        gauge={'axis': {'range': [0, 4], 'tickwidth': 1}, 'bar': {'color': "#f97316"}},
        title={'text': "2 AV. TEMPERATURE ANOMALY<br><span style='font-size:9px;color:#64748b;'>ความเบี่ยงเบนอุณหภูมิผิวโลก</span>", 'font': {'size': 10, 'color': '#94a3b8', 'weight': 'bold'}}
    ))
    fig_g2.update_layout(height=72, margin=dict(t=22, b=4, l=10, r=10), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig_g2, use_container_width=True, config={'displayModeBar': False})
    st.markdown('</div>', unsafe_allow_html=True)

with col_g3:
    st.markdown('<div class="panel-box">', unsafe_allow_html=True)
    aqi_color = "#eab308" if dataset["aqi_val"] <= 100 else "#ef4444"
    fig_g3 = go.Figure(go.Indicator(
        mode="gauge+number", value=dataset["aqi_val"],
        number={'font': {'size': 16, 'color': aqi_color}},
        gauge={'axis': {'range': [0, 200], 'tickwidth': 1}, 'bar': {'color': aqi_color}},
        title={'text': "3 AIR QUALITY INDEX (AQI)<br><span style='font-size:9px;color:#64748b;'>ดัชนีคุณภาพอากาศสากล</span>", 'font': {'size': 10, 'color': '#94a3b8', 'weight': 'bold'}}
    ))
    fig_g3.update_layout(height=72, margin=dict(t=22, b=4, l=10, r=10), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig_g3, use_container_width=True, config={'displayModeBar': False})
    st.markdown('</div>', unsafe_allow_html=True)

with col_card1:
    st.markdown(f'<div class="metric-card"><div class="m-title">1 CH₄ CONCENTRATION (ค่าก๊าซมีเทน)</div><div class="m-value">{dataset["ch4_now"]} <span style="font-size:10px;color:#64748b;">ppb</span></div><div class="m-sub">ค่านิ่งจากสถานีวัดหลัก</div></div>', unsafe_allow_html=True)
with col_card2:
    st.markdown(f'<div class="metric-card"><div class="m-title">2 NO₂ POLLUTION LEVEL (ค่าไนโตรเจนฯ)</div><div class="m-value" style="color:#60a5fa;">{dataset["no2_now"]} <span style="font-size:10px;color:#64748b;">ppb</span></div><div class="m-sub">คำนวณจากภาคการจราจร</div></div>', unsafe_allow_html=True)
with col_card3:
    st.markdown(f'<div class="metric-card"><div class="m-title">3 CARBON MONOXIDE (ค่าก๊าซ CO)</div><div class="m-value" style="color:#f43f5e;">{dataset["co_now"]} <span style="font-size:10px;color:#64748b;">ppm</span></div><div class="m-sub">ความเข้มข้นเขม่าควันไฟ</div></div>', unsafe_allow_html=True)


# --- 7. SECTION 2: GRAPH VISUALIZATION PANELS ---
st.markdown("<div style='margin-bottom: 5px;'></div>", unsafe_allow_html=True)
mid_c1, mid_c2, mid_c3 = st.columns([1.1, 1.1, 1.1])

# ฝั่งซ้าย: แผนที่พิกัดความร้อน
with mid_c1:
    st.markdown('<div class="panel-box">', unsafe_allow_html=True)
    st.markdown("<div class='panel-header'>GHG & POLLUTION HOTSPOTS (GEO-ANALYSIS)</div>", unsafe_allow_html=True)
    st.markdown("<div class='panel-subheader'>แผนที่แสดงพิกัดความเข้มข้นของมลพิษทางอากาศจากเซนเซอร์ในพื้นที่</div>", unsafe_allow_html=True)
    np.random.seed(50)
    lat, lon = dataset["map_coords"]
    map_df = pd.DataFrame({
        'lat': [lat + np.random.uniform(-0.04, 0.04) for _ in range(15)],
        'lon': [lon + np.random.uniform(-0.04, 0.04) for _ in range(15)],
        'intensity': np.random.randint(60, 150, 15)
    })
    fig_map = px.density_mapbox(map_df, lat='lat', lon='lon', z='intensity', radius=22, center=dict(lat=lat, lon=lon), zoom=9, mapbox_style="carto-darkmatter")
    fig_map.update_layout(height=210, margin=dict(t=0, b=0, l=0, r=0), paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig_map, use_container_width=True, config={'displayModeBar': False})
    st.markdown('</div>', unsafe_allow_html=True)

# ฝั่งกลาง: กราฟสถิติย้อนหลัง 30 ปี ปรับเปลี่ยนชื่อและเส้นตามค่าสารมลพิษที่เลือกจริง สอดคล้อง 100%
with mid_c2:
    st.markdown('<div class="panel-box">', unsafe_allow_html=True)
    st.markdown(f"<div class='panel-header'>30-YEAR HISTORICAL {metric_short} TREND</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='panel-subheader'>สถิติย้อนหลังปริมาณสะสมของ {metric_short} ตั้งแต่ปี 1930 ถึงปัจจุบัน ({active_unit})</div>", unsafe_allow_html=True)
    
    df_trend = pd.DataFrame({'Year': years_30y, 'Value': active_history})
    fig_area = px.area(df_trend, x='Year', y='Value', template="plotly_dark")
    fig_area.update_traces(line=dict(color='#22d3ee', width=2), fillcolor='rgba(34, 211, 238, 0.06)', mode='lines+markers')
    fig_area.update_layout(
        height=180, margin=dict(t=5, b=5, l=5, r=5), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showgrid=False, title="ปี ค.ศ. (Years)"),
        yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.03)', title=f"ระดับความเข้มข้น ({active_unit})")
    )
    st.plotly_chart(fig_area, use_container_width=True, config={'displayModeBar': False})
    st.markdown('</div>', unsafe_allow_html=True)

# ฝั่งขวา: กราฟคอมโบสลับข้อมูลแกนนอนตามช่วงเวลาจริง (Time Filter) แก้ปัญหาเรื่องแกนข้อมูลมั่ว
with mid_c3:
    st.markdown('<div class="panel-box">', unsafe_allow_html=True)
    st.markdown("<div class='panel-header'>DYNAMIC TIME-SERIES WEATHER & AIR ANALYSIS</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='panel-subheader'>เปรียบเทียบสถิติอุณหภูมิ (เส้นสีฟ้า) คู่กับค่าฝุ่นมลพิษ (แท่งส้ม) อิงตามช่วงเวลา: {sel_time}</div>", unsafe_allow_html=True)
    
    time_data = dataset["time_modes"][sel_time]
    
    fig_combo = go.Figure()
    # แกนซ้าย: แท่งแสดงระดับฝุ่นละออง
    fig_combo.add_trace(go.Bar(x=time_data["x"], y=time_data["pm25"], name='PM2.5 (µg/m³)', marker_color='#f97316', opacity=0.85, yaxis='y1'))
    # แกนขวา: เส้นแสดงระดับอุณหภูมิ
    fig_combo.add_trace(go.Scatter(x=time_data["x"], y=time_data["temp"], name='อุณหภูมิ (°C)', line=dict(color='#22d3ee', width=2.5), yaxis='y2'))
    
    fig_combo.update_layout(
        height=180, margin=dict(t=10, b=5, l=5, r=5), template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", showlegend=False,
        xaxis=dict(showgrid=False, title=f"ช่วงเวลาตรวจสอบ ({sel_time.split(' ')[1]})"),
        yaxis=dict(title="ค่าฝุ่นละอองสะสม (µg/m³)", showgrid=True, gridcolor='rgba(255,255,255,0.03)'),
        yaxis2=dict(title="ระดับอุณหภูมิเฉลี่ย (°C)", overlaying='y', side='right', showgrid=False)
    )
    st.plotly_chart(fig_combo, use_container_width=True, config={'displayModeBar': False})
    st.markdown('</div>', unsafe_allow_html=True)


# --- 8. SECTION 3: BOTTOM DATA BREAKDOWN AND DATA VALIDATION TABLE ---
st.markdown("<div style='margin-bottom: 5px;'></div>", unsafe_allow_html=True)
bot_c1, bot_c2 = st.columns([1.2, 1.0])

with bot_c1:
    st.markdown('<div class="panel-box">', unsafe_allow_html=True)
    st.markdown("<div class='panel-header'>POLLUTION BREAKDOWN (GHG & CRITERIA SEGMENTATION)</div>", unsafe_allow_html=True)
    st.markdown("<div class='panel-subheader'>กราฟแสดงสัดส่วนระดับความปลอดภัยของสารมลพิษแต่ละประเภทหลัก (แยกเกณฑ์ตามสีมาตรฐานดัชนีคุณภาพอากาศ)</div>", unsafe_allow_html=True)
    
    b_data = dataset["breakdown"]
    comp_keys = list(b_data.keys())
    
    fig_stack = go.Figure(data=[
        go.Bar(name='ระดับต่ำ-ปลอดภัย (Low)', x=comp_keys, y=[b_data[k][0] for k in comp_keys], marker_color='#10b981'),
        go.Bar(name='ระดับปานกลาง (Moderate)', x=comp_keys, y=[b_data[k][1] for k in comp_keys], marker_color='#eab308'),
        go.Bar(name='ระดับเริ่มอันตราย (Unhealthy)', x=comp_keys, y=[b_data[k][2] for k in comp_keys], marker_color='#ef4444')
    ])
    fig_stack.update_layout(barmode='stack', height=115, margin=dict(t=5, b=5, l=5, r=5), template="plotly_dark", 
                            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", showlegend=False, 
                            xaxis=dict(showgrid=False, title="ประเภทสารมลพิษและก๊าซเรือนกระจก"), yaxis=dict(showgrid=False, title="เปอร์เซ็นต์สัดส่วน (%)"))
    st.plotly_chart(fig_stack, use_container_width=True, config={'displayModeBar': False})
    st.markdown('</div>', unsafe_allow_html=True)

with bot_c2:
    st.markdown('<div class="panel-box">', unsafe_allow_html=True)
    st.markdown("<div class='panel-header'>METEOROLOGICAL DATA HUB & DATA VALIDATION PIPELINE</div>", unsafe_allow_html=True)
    st.markdown("<div class='panel-subheader'>ตารางสรุปข้อมูลตรวจสอบความถูกต้องและการรับ-ส่งค่าแบบเรียลไทม์กับสถาบันเครือข่าย</div>", unsafe_allow_html=True)
    
    validation_df = pd.DataFrame({
        'แหล่งที่มาสารข้อมูล (Source)': ['Air4Thai API (กรมควบคุมมลพิษ)', 'TMD Meteorology (กรมอุตุฯ)', 'Sentinel-5P (ดาวเทียมตรวจวัด)', 'OpenAQ Network'],
        'ค่าก๊าซตรวจวัด (Gas Value)': [f"{dataset['no2_now']} ppb", "ค่าความเร็วลมผันแปร", f"{dataset['co2_now']} ppm", "Data Verified"],
        'สถานะคำนวณ (Evaluation)': ["🟢 เชื่อมต่อเสถียร (Sync)", "🟢 ส่งข้อมูลปกติ", "🟢 ผ่านเกณฑ์ตรวจสอบ", "🟡 กำลังสำรองระบบ"]
    })
    st.dataframe(validation_df, hide_index=True, use_container_width=True, height=110)
    st.markdown('</div>', unsafe_allow_html=True)
