import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

# ==========================================
# 1. PAGE SETUP & CYBER DARK THEME
# ==========================================
st.set_page_config(layout="wide", page_title="Intelligent Environmental Dashboard")

# ควบคุม UI ให้เรียบร้อย สวยงาม และเสถียรบนทุกหน้าจอ
st.markdown("""
    <style>
        ::-webkit-scrollbar { display: none; }
        html, body, [data-testid="stAppViewContainer"] { 
            background-color: #0b1329 !important;
            color: #f8fafc !important;
            font-family: 'Inter', 'Sarabun', sans-serif;
        }
        .block-container { padding: 1.0rem 2.0rem !important; }
        
        /* สไตล์กล่อง Dropdown และ Label */
        div[data-baseweb="select"] input { pointer-events: none !important; caret-color: transparent !important; }
        div[data-baseweb="select"] { background-color: #1c2541 !important; border: 1px solid #3a506b !important; border-radius: 4px; }
        div[data-baseweb="select"] * { color: #ffffff !important; font-size: 13px !important; }
        label[data-testid="stWidgetLabel"] { font-size: 11px !important; color: #94a3b8 !important; font-weight: bold; }
        
        /* ตารางรายงานดัชนีน้ำด้านล่าง */
        .water-container { background-color: #1c2541; border: 1px solid #3a506b; border-radius: 6px; padding: 12px; height: 145px; }
        .badge { padding: 2px 8px; border-radius: 12px; font-size: 10px; font-weight: bold; display: inline-block; }
        .badge-pass { background-color: #10b981; color: #ffffff; }
        .badge-warn { background-color: #ef4444; color: #ffffff; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. CLEAN & STABLE DATA ENGINE (กัน Error)
# ==========================================
years = [1930, 1950, 1970, 1990, 2000, 2010, 2026]
months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

REGIONAL_DB = {}

# ข้อมูลภาคกลาง
REGIONAL_DB["📌 CENTRAL (ภาคกลาง)"] = {
    "co2": 421.5, "temp": 1.8, "aqi": 85, "aqi_color": "#eab308",
    "co2_trend": [240, 320, 490, 680, 820, 990, 1420],
    "pm25": [22, 26, 35, 40, 28, 18, 15, 14, 19, 23, 25, 30],
    "temp_list": [26, 28, 30, 32, 31, 30, 29, 29, 28, 27, 26, 25]
}

# ข้อมูลภาคเหนือ
REGIONAL_DB["📌 NORTH (ภาคเหนือ)"] = {
    "co2": 412.8, "temp": 2.4, "aqi": 165, "aqi_color": "#ef4444",
    "co2_trend": [210, 270, 410, 550, 690, 840, 1150],
    "pm25": [45, 68, 95, 120, 75, 30, 22, 19, 24, 38, 48, 55],
    "temp_list": [20, 23, 27, 31, 30, 29, 28, 28, 27, 25, 22, 19]
}

# ==========================================
# 3. DASHBOARD HEADER AREA
# ==========================================
st.markdown("""
<div style="text-align: center; margin-bottom: 15px;">
    <h2 style="color: #ffffff; margin: 0; font-size: 22px; font-weight: 800; letter-spacing: 0.5px;">
        INTELLIGENT ENVIRONMENTAL & GHG MONITORING DASHBOARD (THAILAND)
    </h2>
    <p style="color: #48cae4; margin: 3px 0 0 0; font-size: 13px; font-weight: 500;">
        แดชบอร์ดอัจฉริยะติดตามก๊าซเรือนกระจกและมลพิษ (ประเทศไทย)
    </p>
</div>
""", unsafe_allow_html=True)

# ==========================================
# 4. TOP INTERACTIVE NAVIGATION BAR
# ==========================================
nav_cols = st.columns([2, 3, 3, 3])
with nav_cols[0]:
    st.markdown('<div style="font-family: monospace; font-size: 12px; color: #06d6a0; font-weight: bold; margin-top: 25px;">⏱️ SYSTEM STATUS: ONLINE</div>', unsafe_allow_html=True)
with nav_cols[1]:
    sel_region = st.selectbox("REGION (ภูมิภาค)", list(REGIONAL_DB.keys()))
with nav_cols[2]:
    st.selectbox("DATA SOURCE (แหล่งข้อมูล)", ["INTEGRATED ALL STATIONS", "SATELLITE SENSORS"])
with nav_cols[3]:
    st.selectbox("TIME RANGE (ช่วงเวลา)", ["1 MONTH", "30 YEARS TREND"])

st.markdown("<div style='margin-bottom: 15px;'></div>", unsafe_allow_html=True)
data = REGIONAL_DB[sel_region]

# ==========================================
# 5. TIER 1: 3 METRIC GAUGE CHARTS
# ==========================================
m1, m2, m3 = st.columns(3)

with m1:
    fig1 = go.Figure(go.Indicator(
        mode="gauge+number", value=data["co2"],
        title={'text': "<b>1 🔵 ATMOSPHERIC CO₂ LEVEL (PPM)</b>", 'font': {'size': 11, 'color': '#00b4d8'}},
        number={'font': {'size': 22, 'color': '#ffffff'}},
        gauge={'axis': {'range': [350, 500]}, 'bar': {'color': "#00b4d8"}, 'bgcolor': "#0b1329"}
    ))
    fig1.update_layout(height=115, margin=dict(t=30, b=10, l=15, r=15), paper_bgcolor="#1c2541")
    st.plotly_chart(fig1, use_container_width=True, config={'displayModeBar': False})

with m2:
    fig2 = go.Figure(go.Indicator(
        mode="gauge+number", value=data["temp"],
        title={'text': "<b>2 🟠 AV. TEMPERATURE ANOMALY (°C)</b>", 'font': {'size': 11, 'color': '#ffb703'}},
        number={'prefix': "+", 'font': {'size': 22, 'color': '#ffb703'}},
        gauge={'axis': {'range': [0, 4]}, 'bar': {'color': "#ffb703"}, 'bgcolor': "#0b1329"}
    ))
    fig2.update_layout(height=115, margin=dict(t=30, b=10, l=15, r=15), paper_bgcolor="#1c2541")
    st.plotly_chart(fig2, use_container_width=True, config={'displayModeBar': False})

with m3:
    fig3 = go.Figure(go.Indicator(
        mode="gauge+number", value=data["aqi"],
        title={'text': "<b>3 🟡 AIR QUALITY INDEX (AQI)</b>", 'font': {'size': 11, 'color': '#eab308'}},
        number={'font': {'size': 22, 'color': data["aqi_color"]}},
        gauge={'axis': {'range': [0, 200]}, 'bar': {'color': data["aqi_color"]}, 'bgcolor': "#0b1329"}
    ))
    fig3.update_layout(height=115, margin=dict(t=30, b=10, l=15, r=15), paper_bgcolor="#1c2541")
    st.plotly_chart(fig3, use_container_width=True, config={'displayModeBar': False})

st.markdown("<div style='margin-bottom: 15px;'></div>", unsafe_allow_html=True)

# ==========================================
# 6. TIER 2: HOTSPOT MAP & TIME TRENDS
# ==========================================
col_left, col_right = st.columns([1.1, 1.0])

with col_left:
    np.random.seed(10)
    map_df = pd.DataFrame({
        'Lat_Index': np.random.randint(1, 10, 45),
        'Lon_Index': np.random.randint(1, 10, 45),
        'Density': np.random.randint(40, 190, 45)
    })
    fig_map = px.density_heatmap(map_df, x='Lat_Index', y='Lon_Index', z='Density', color_continuous_scale="Turbid")
    fig_map.update_layout(
        height=230, margin=dict(t=35, b=5, l=10, r=10), coloraxis_showscale=False,
        template="plotly_dark", paper_bgcolor="#1c2541", plot_bgcolor="#1c2541",
        title={'text': "<b>🔥 REAL-TIME GHG HOTSPOT GRID MATRIX (BANGKOK)</b>", 'font': {'size': 11, 'color': '#00b4d8'}}
    )
    st.plotly_chart(fig_map, use_container_width=True, config={'displayModeBar': False})

with col_right:
    # ส่วนบน: Area Chart
    trend_df = pd.DataFrame({'Year': years, 'CO2': data["co2_trend"]})
    fig_area = px.area(trend_df, x='Year', y='CO2', template="plotly_dark")
    fig_area.update_traces(line=dict(color='#00b4d8', width=2), fillcolor='rgba(0, 180, 216, 0.15)')
    fig_area.update_layout(
        height=100, margin=dict(t=25, b=5, l=15, r=15), paper_bgcolor="#1c2541", plot_bgcolor="#1c2541",
        title={'text': "<b>📈 30-YEAR CO₂ EMISSIONS TREND (KT/YR)</b>", 'font': {'size': 11, 'color': '#00b4d8'}},
    )
    fig_area.update_xaxes(showgrid=False); fig_area.update_yaxes(showgrid=False)
    st.plotly_chart(fig_area, use_container_width=True, config={'displayModeBar': False})
        
    st.markdown("<div style='margin-bottom: 10px;'></div>", unsafe_allow_html=True)
    
    # ส่วนล่าง: Combo Chart Bar & Line
    fig_combo = make_subplots(specs=[[{"secondary_y": True}]])
    fig_combo.add_trace(go.Bar(x=months, y=data["pm25"], name='PM2.5', marker_color='#ff7a00'), secondary_y=False)
    fig_combo.add_trace(go.Scatter(x=months, y=data["temp_list"], name='Temp', line=dict(color='#00b4d8', width=2)), secondary_y=True)
    fig_combo.update_layout(
        height=100, margin=dict(t=25, b=5, l=15, r=15), template="plotly_dark",
        paper_bgcolor="#1c2541", plot_bgcolor="#1c2541", showlegend=False,
        title={'text': "<b>📊 MONTHLY TEMPERATURE VS. AIR QUALITY</b>", 'font': {'size': 11, 'color': '#00b4d8'}},
    )
    fig_combo.update_xaxes(showgrid=False); fig_combo.update_yaxes(showgrid=False)
    st.plotly_chart(fig_combo, use_container_width=True, config={'displayModeBar': False})

st.markdown("<div style='margin-bottom: 15px;'></div>", unsafe_allow_html=True)

# ==========================================
# 7. TIER 3: POLLUTION BREAKDOWN & WATER REPORT
# ==========================================
b_left, b_right = st.columns([1.1, 1.0])

with b_left:
    pollutants = ['PM2.5', 'PM10', 'NO₂', 'SO₂']
    fig_stack = go.Figure()
    # 🔒 แก้ไขบั๊กจุดนี้เรียบร้อยแล้ว: ปิดปีกกาและซิงเกิลโควตครบถ้วน ไม่พังแน่นอน
    fig_stack.add_trace(go.Bar(name='Low', x=pollutants, y=[80, 90, 100, 110], marker_color='#10b981'))
    fig_stack.add_trace(go.Bar(name='Moderate', x=pollutants, y=[60, 50, 40, 30], marker_color='#f59e0b'))
    fig_stack.add_trace(go.Bar(name='Unhealthy', x=pollutants, y=[70, 40, 50, 20], marker_color='#ef4444'))
    
    fig_stack.update_layout(
        barmode='stack', height=145, margin=dict(t=25, b=5, l=10, r=10), template="plotly_dark", 
        paper_bgcolor="#1c2541", plot_bgcolor="#1c2541", showlegend=False,
        title={'text': "<b>📊 POLLUTION BREAKDOWN (PM2.5, NO₂, SO₂)</b>", 'font': {'size': 11, 'color': '#00b4d8'}}
    )
    st.plotly_chart(fig_stack, use_container_width=True, config={'displayModeBar': False})

with b_right:
    st.markdown('<div class="water-container">', unsafe_allow_html=True)
    st.markdown('<div style="font-size: 11px; color: #00b4d8; font-weight: bold; margin-bottom: 8px;">💧 WATER QUALITY MONITORING (MAJOR RIVERS)</div>', unsafe_allow_html=True)
    
    table_code = """
    <table style="width:100%; border-collapse: collapse; font-size:11px; color:#ffffff;">
        <tr style="border-bottom: 1px solid #3a506b; color:#94a3b8; font-weight:bold; text-align:left;">
            <th style="padding: 3px;">River Station</th>
            <th style="text-align:center; padding: 3px;">DO STATUS</th>
            <th style="text-align:center; padding: 3px;">COD STATUS</th>
        </tr>
        <tr style="border-bottom: 1px solid #3a506b;">
            <td style="padding: 5px; font-weight:bold; color:#48cae4;">Chao Phraya</td>
            <td style="text-align:center;"><span class="badge badge-pass">DO PASS</span></td>
            <td style="text-align:center;"><span class="badge badge-warn">COD WARN</span></td>
        </tr>
        <tr>
            <td style="padding: 5px; font-weight:bold; color:#48cae4;">Tha Chin</td>
            <td style="text-align:center;"><span class="badge badge-pass">DO PASS</span></td>
            <td style="text-align:center;"><span class="badge badge-pass">DO PASS</span></td>
        </tr>
    </table>
    """
    st.markdown(table_code, unsafe_allow_html=True)
    
    # ปุ่มดาวน์โหลดรายงานแบบเสถียร
    report_df = pd.DataFrame({'Metric': ['CO2', 'Temp Anomaly', 'AQI'], 'Current_Value': [data["co2"], data["temp"], data["aqi"]]})
    csv_data = report_df.to_csv(index=False).encode('utf-8')
    st.markdown("<div style='margin-top: 5px;'></div>", unsafe_allow_html=True)
    st.download_button(label="📥 DOWNLOAD EXPORT REPORT (.CSV)", data=csv_data, file_name="environmental_report.csv", mime="text/csv")
    st.markdown('</div>', unsafe_allow_html=True)
