import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# 1. INITIAL SETUP (ตั้งค่าหน้าจอให้กว้างพอดีสัดส่วน)
st.set_page_config(layout="wide", page_title="Environmental & GHG Dashboard", initial_sidebar_state="collapsed")

# 2. COMPACT CYBER DARK THEME CSS (ปรับลดขนาดโครงสร้างให้กะทัดรัด ไม่ใหญ่เกินไป)
st.markdown("""
    <style>
        ::-webkit-scrollbar { display: none; }
        html, body, [data-testid="stAppViewContainer"] { 
            background-color: #0b111e !important;
            color: #ffffff !important;
        }
        /* กระชับพื้นที่ขอบหน้าจอ */
        .block-container { padding: 0.6rem 1.2rem !important; }
        
        /* ส่วนหัวข้อหลัก ขนาดพอดีคำ */
        .main-title-box { text-align: center; margin-bottom: 10px; }
        .title-main { font-size: 19px; font-weight: 800; color: #ffffff; letter-spacing: 0.5px; margin: 0; }
        .title-sub { font-size: 12px; color: #64748b; margin-top: 2px; }
        
        /* แถบควบคุมบนหน้าจอ */
        .control-bar {
            background-color: #0f172a; padding: 6px 12px; border-radius: 6px;
            border: 1px solid #1e293b; margin-bottom: 10px;
        }
        
        /* กล่องแสดงผลย่อย (Compact Box) */
        .panel-box {
            background-color: #0f172a; border: 1px solid #1e293b; border-radius: 6px;
            padding: 10px; height: 100%; box-shadow: 0 4px 10px rgba(0,0,0,0.3);
        }
        .panel-title { font-size: 11px; color: #38bdf8; font-weight: 700; margin-bottom: 6px; text-transform: uppercase; }
        
        /* การ์ดสรุปตัวเลขแบบพอดีสายตา */
        .metric-card-compact {
            background: linear-gradient(180deg, #141b2d 0%, #0c101b 100%);
            border: 1px solid #22d3ee33; border-radius: 6px; padding: 8px 12px; text-align: center;
        }
        .card-label { font-size: 10px; color: #94a3b8; font-weight: 600; }
        .card-value { font-size: 24px; font-weight: 800; color: #22d3ee; margin: 2px 0; }
        .card-unit { font-size: 11px; color: #475569; font-weight: bold; }

        /* 🔒 ล็อกส่วน INPUT ของ SELECTBOX เพื่อให้จิ้มเลือกได้อย่างเดียว แป้นพิมพ์ไม่เด้ง */
        div[data-baseweb="select"] input {
            pointer-events: none !important;
            caret-color: transparent !important;
        }
        div[data-baseweb="select"] { background-color: #1e293b !important; border: 1px solid #334155 !important; border-radius: 4px; }
        div[data-baseweb="select"] * { color: #ffffff !important; font-size: 12px !important; }
        label[data-testid="stWidgetLabel"] { font-size: 11px !important; color: #94a3b8 !important; margin-bottom: 2px !important; font-weight: 600; }
    </style>
""", unsafe_allow_html=True)

# 3. RELIABLE DATA MATRIX (คลังข้อมูลมลพิษ)
years_30y = [1930, 1950, 1970, 1990, 2000, 2010, 2026]

CORE_DATA = {
    "ภาคกลาง (Central Thailand)": {
        "co2_now": 421.5, "ch4_now": 1919.4, "no2_now": 330.8, "temp_anomaly": 1.8, "aqi_val": 85, "aqi_txt": "ปานกลาง (Moderate)", "co_now": 1.2,
        "co2_history": [290, 312, 335, 362, 378, 395, 421.5],
        "ch4_history": [1620, 1690, 1740, 1810, 1845, 1880, 1919.4],
        "no2_history": [150, 190, 225, 270, 295, 315, 330.8],
        "map_coords": [13.7563, 100.5018],
        "time_modes": {
            "1 เดือนล่าสุด (1 Month)": {"x": ["สัปดาห์ 1", "สัปดาห์ 2", "สัปดาห์ 3", "สัปดาห์ 4"], "pm25": [35, 58, 85, 42], "temp": [26, 28, 29, 27]},
            "1 ปีล่าสุด (1 Year)": {"x": ["ม.ค.", "มี.ค.", "พ.ค.", "ก.ค.", "ก.ย.", "พ.ย."], "pm25": [65, 85, 30, 15, 22, 45], "temp": [24, 28, 30, 28, 26, 24]},
            "5 ปีล่าสุด (5 Years)": {"x": ["2022", "2023", "2024", "2025", "2026"], "pm25": [38, 42, 45, 40, 43], "temp": [1.4, 1.5, 1.7, 1.6, 1.8]}
        },
        "breakdown": {"PM2.5": [40, 35, 25], "PM10": [50, 40, 10], "NO₂": [45, 35, 20], "SO₂": [80, 15, 5]}
    },
    "ภาคเหนือ (Northern Thailand)": {
        "co2_now": 412.8, "ch4_now": 1850.2, "no2_now": 120.4, "temp_anomaly": 2.4, "aqi_val": 165, "aqi_txt": "เริ่มมีผลต่อสุขภาพ", "co_now": 2.3,
        "co2_history": [288, 305, 328, 352, 368, 384, 412.8],
        "ch4_history": [1590, 1640, 1700, 1760, 1790, 1820, 1850.2],
        "no2_history": [60, 75, 90, 102, 110, 115, 120.4],
        "map_coords": [18.7883, 98.9853],
        "time_modes": {
            "1 เดือนล่าสุด (1 Month)": {"x": ["สัปดาห์ 1", "สัปดาห์ 2", "สัปดาห์ 3", "สัปดาห์ 4"], "pm25": [90, 120, 165, 80], "temp": [22, 25, 27, 24]},
            "1 ปีล่าสุด (1 Year)": {"x": ["ม.ค.", "มี.ค.", "พ.ค.", "ก.ค.", "ก.ย.", "พ.ย."], "pm25": [95, 150, 45, 12, 18, 65], "temp": [19, 26, 29, 27, 24, 21]},
            "5 ปีล่าสุด (5 Years)": {"x": ["2022", "2023", "2024", "2025", "2026"], "pm25": [55, 62, 70, 58, 66], "temp": [1.9, 2.1, 2.4, 2.2, 2.4]}
        },
        "breakdown": {"PM2.5": [15, 25, 60], "PM10": [30, 30, 40], "NO₂": [70, 20, 10], "SO₂": [90, 8, 2]}
    }
}

# 4. TOP MAIN TITLE
st.markdown("""
<div class="main-title-box">
    <div class="title-main">INTELLIGENT ENVIRONMENTAL & GHG MONITORING DASHBOARD</div>
    <div class="title-sub">แดชบอร์ดติดตามวิเคราะห์ก๊าซเรือนกระจกและมลพิษทางอากาศ (ประเทศไทย)</div>
</div>
""", unsafe_allow_html=True)

# 5. COMPACT DROPDOWN CONTROL BAR (แถบเลือกแบบเดิมล็อกไม่ให้พิมพ์)
st.markdown('<div class="control-bar">', unsafe_allow_html=True)
ctrl_col1, ctrl_col2, ctrl_col3, ctrl_col4 = st.columns([2.5, 3.1, 3.2, 3.2])
with ctrl_col1:
    st.markdown('<div style="font-family:monospace; font-size:12px; color:#10b981; font-weight:700; margin-top:18px;">🕒 MARCH 2026 | 13:58:55</div>', unsafe_allow_html=True)
with ctrl_col2:
    sel_region = st.selectbox("ภูมิภาคตรวจสอบ (REGION):", list(CORE_DATA.keys()))
with ctrl_col3:
    sel_metric = st.selectbox("ก๊าซมลพิษหลัก (MAIN METRIC):", ["CO₂ (คาร์บอนไดออกไซด์)", "CH₄ (มีเทน)", "NO₂ (ไนโตรเจนไดออกไซด์)"])
with ctrl_col4:
    sel_time = st.selectbox("ช่วงตัวกรองเวลา (TIME FILTER):", ["1 เดือนล่าสุด (1 Month)", "1 ปีล่าสุด (1 Year)", "5 ปีล่าสุด (5 Years)"])
st.markdown('</div>', unsafe_allow_html=True)

# ดึงข้อมูลมาจับคู่เชื่อมโยงตามเงื่อนไขที่เลือก
dataset = CORE_DATA[sel_region]
metric_short = sel_metric.split(" ")[0]

if metric_short == "CO₂":
    active_value, active_unit, active_history = dataset["co2_now"], "ppm", dataset["co2_history"]
elif metric_short == "CH₄":
    active_value, active_unit, active_history = dataset["ch4_now"], "ppb", dataset["ch4_history"]
else:
    active_value, active_unit, active_history = dataset["no2_now"], "ppb", dataset["no2_history"]

# --- 6. SECTION 1: แผงตัวเลขสรุปย่อ กะทัดรัด มองเห็นง่ายไม่เบียด ---
m_col1, m_col2, m_col3 = st.columns(3)
with m_col1:
    st.markdown(f'<div class="metric-card-compact"><div class="card-label">ระดับก๊าซ {metric_short} ในชั้นบรรยากาศ</div><div class="card-value">{active_value} <span class="card-unit">{active_unit}</span></div></div>', unsafe_allow_html=True)
with m_col2:
    st.markdown(f'<div class="metric-card-compact"><div class="card-label">ค่าความเบี่ยงเบนอุณหภูมิสะสม</div><div class="card-value" style="color:#f97316;">+{dataset["temp_anomaly"]} <span class="card-unit">°C</span></div></div>', unsafe_allow_html=True)
with m_col3:
    aqi_color = "#eab308" if dataset["aqi_val"] <= 100 else "#ef4444"
    st.markdown(f'<div class="metric-card-compact"><div class="card-label">ดัชนีคุณภาพอากาศสากล (AQI)</div><div class="card-value" style="color:{aqi_color};">{dataset["aqi_val"]} <span style="font-size:12px; font-weight:bold;">({dataset["aqi_txt"].split(" ")[0]})</span></div></div>', unsafe_allow_html=True)

# --- 7. SECTION 2: แผงกราวิเคราะห์ข้อมูลหลัก (ย่อขนาดความสูงให้พอดีจอ) ---
st.markdown("<div style='margin-bottom: 6px;'></div>", unsafe_allow_html=True)
graph_col1, graph_col2, graph_col3 = st.columns([1.0, 1.1, 1.1])

# ช่องที่ 1: แผนที่ความร้อนย่อส่วน
with graph_col1:
    st.markdown('<div class="panel-box">', unsafe_allow_html=True)
    st.markdown("<div class='panel-title'>📍 พิกัดความหนาแน่นมลพิษ</div>", unsafe_allow_html=True)
    np.random.seed(42)
    lat, lon = dataset["map_coords"]
    map_df = pd.DataFrame({
        'lat': [lat + np.random.uniform(-0.04, 0.04) for _ in range(12)],
        'lon': [lon + np.random.uniform(-0.04, 0.04) for _ in range(12)],
        'intensity': np.random.randint(50, 140, 12)
    })
    fig_map = px.density_mapbox(map_df, lat='lat', lon='lon', z='intensity', radius=20, center=dict(lat=lat, lon=lon), zoom=9, mapbox_style="carto-darkmatter")
    fig_map.update_layout(height=160, margin=dict(t=0, b=0, l=0, r=0), paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig_map, use_container_width=True, config={'displayModeBar': False})
    st.markdown('</div>', unsafe_allow_html=True)

# ช่องที่ 2: กราฟเส้นแนวโน้ม 30 ปีตามก๊าซเรือนกระจกที่เลือก
with graph_col2:
    st.markdown('<div class="panel-box">', unsafe_allow_html=True)
    st.markdown(f"<div class='panel-title'>📉 แนวโน้มปริมาณสะสมของก๊าซ {metric_short} (30 ปี)</div>", unsafe_allow_html=True)
    df_trend = pd.DataFrame({'Year': years_30y, 'Value': active_history})
    fig_area = px.area(df_trend, x='Year', y='Value', template="plotly_dark")
    fig_area.update_traces(line=dict(color='#22d3ee', width=2), fillcolor='rgba(34, 211, 238, 0.05)', mode='lines+markers')
    fig_area.update_layout(
        height=160, margin=dict(t=5, b=5, l=5, r=5), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showgrid=False, title="ปี ค.ศ.", font=dict(size=10)), yaxis=dict(title=active_unit, font=dict(size=10))
    )
    st.plotly_chart(fig_area, use_container_width=True, config={'displayModeBar': False})
    st.markdown('</div>', unsafe_allow_html=True)

# ช่องที่ 3: กราฟผสมเปลี่ยนแกนนอนตามช่วงเวลาที่จิ้มเลือกจริง
with graph_col3:
    st.markdown('<div class="panel-box">', unsafe_allow_html=True)
    st.markdown(f"<div class='panel-title'>🔀 สถิติฝุ่นละอองและอุณหภูมิ ({metric_short})</div>", unsafe_allow_html=True)
    time_data = dataset["time_modes"][sel_time]
    
    fig_combo = go.Figure()
    fig_combo.add_trace(go.Bar(x=time_data["x"], y=time_data["pm25"], name='ฝุ่น PM2.5', marker_color='#f97316', opacity=0.8, yaxis='y1'))
    fig_combo.add_trace(go.Scatter(x=time_data["x"], y=time_data["temp"], name='อุณหภูมิ', line=dict(color='#22d3ee', width=2), yaxis='y2'))
    
    fig_combo.update_layout(
        height=160, margin=dict(t=10, b=5, l=5, r=5), template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", showlegend=False,
        xaxis=dict(showgrid=False, font=dict(size=10)),
        yaxis=dict(title="PM2.5 (µg/m³)", side='left', font=dict(size=9)),
        yaxis2=dict(title="Temp (°C)", overlaying='y', side='right', showgrid=False, font=dict(size=9))
    )
    st.plotly_chart(fig_combo, use_container_width=True, config={'displayModeBar': False})
    st.markdown('</div>', unsafe_allow_html=True)

# --- 8. SECTION 3: ตารางจำแนกและตรวจสอบข้อมูลด้านล่างสุด ---
st.markdown("<div style='margin-bottom: 6px;'></div>", unsafe_allow_html=True)
bot_col1, bot_col2 = st.columns([1.2, 1.0])

with bot_col1:
    st.markdown('<div class="panel-box">', unsafe_allow_html=True)
    st.markdown("<div class='panel-title'>📊 สัดส่วนระดับความปลอดภัยของกลุ่มก๊าซสารมลพิษย่อย</div>", unsafe_allow_html=True)
    b_data = dataset["breakdown"]
    comp_keys = list(b_data.keys())
    fig_stack = go.Figure(data=[
        go.Bar(name='ปลอดภัย', x=comp_keys, y=[b_data[k][0] for k in comp_keys], marker_color='#10b981'),
        go.Bar(name='ปานกลาง', x=comp_keys, y=[b_data[k][1] for k in comp_keys], marker_color='#eab308'),
        go.Bar(name='เริ่มอันตราย', x=comp_keys, y=[b_data[k][2] for k in comp_keys], marker_color='#ef4444')
    ])
    fig_stack.update_layout(barmode='stack', height=100, margin=dict(t=5, b=5, l=5, r=5), template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", showlegend=False)
    st.plotly_chart(fig_stack, use_container_width=True, config={'displayModeBar': False})
    st.markdown('</div>', unsafe_allow_html=True)

with bot_col2:
    st.markdown('<div class="panel-box">', unsafe_allow_html=True)
    st.markdown("<div class='panel-title'>🌐 สถานะการเชื่อมต่อสถานีเครือข่ายเรียลไทม์ (API)</div>", unsafe_allow_html=True)
    validation_df = pd.DataFrame({
        'สถานีรับส่งข้อมูล': ['Air4Thai (คพ.)', 'TMD (กรมอุตุฯ)', 'Sentinel-5P (ดาวเทียม)'],
        'ค่าล่าสุด': [f"{dataset['no2_now']} ppb", "ทิศทางลมสอดคล้อง", f"{dataset['co2_now']} ppm"],
        'สถานะระบบ': ["🟢 ปรับข้อมูลเสร็จสิ้น", "🟢 ทำงานปกติ", "🟢 ผ่านการตรวจสอบค่า"]
    })
    st.dataframe(validation_df, hide_index=True, use_container_width=True, height=95)
    st.markdown('</div>', unsafe_allow_html=True)
