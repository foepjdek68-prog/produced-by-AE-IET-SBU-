import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

# ==========================================
# 1. PAGE CONFIGURATION & CYBER DARK THEME
# ==========================================
st.set_page_config(layout="wide", page_title="Intelligent Environmental Dashboard")

# ฉีด CSS ควบคุมโทนสีการ์ด และจัดแต่งปุ่มกดเมนู (Radio) ให้ดูโมเดิร์นคล้ายแผงควบคุม
st.markdown("""
    <style>
        ::-webkit-scrollbar { display: none; }
        html, body, [data-testid="stAppViewContainer"] { 
            background-color: #020617 !important;
            color: #f8fafc !important;
            font-family: 'Inter', 'Sarabun', sans-serif;
        }
        .block-container { padding: 0.8rem 1.5rem !important; }
        
        /* หัวเรื่องแดชบอร์ด */
        .hdr-box { text-align: center; margin-bottom: 12px; }
        .hdr-title { font-size: 20px; font-weight: 800; color: #ffffff; letter-spacing: 0.5px; margin: 0; }
        .hdr-sub { font-size: 12px; color: #94a3b8; margin-top: 2px; }
        
        /* 🛠️ ปรับแต่งปุ่มกด Radio แนวนอนให้ดูเหมือนปุ่มกดสไตล์แผงควบคุมระดับสูง */
        div[data-testid="stRadio"] > label {
            font-size: 11px !important; color: #22d3ee !important; font-weight: 700 !important; text-transform: uppercase;
        }
        div[data-testid="stRadio"] div[role="radiogroup"] {
            background-color: #1e293b !important; border: 1px solid #334155 !important; 
            padding: 4px !important; border-radius: 6px !important; gap: 10px !important;
        }
        div[data-testid="stRadio"] div[role="radiogroup"] label {
            background-color: #020617 !important; padding: 4px 10px !important; 
            border-radius: 4px !important; border: 1px solid #1e293b;
        }
        
        /* ตารางวิเคราะห์น้ำด้านล่าง */
        .water-card-frame {
            background-color: #1e293b; border: 1px solid #334155; 
            border-radius: 4px; padding: 12px; height: 140px;
        }
        .status-dot { padding: 2px 8px; border-radius: 12px; font-size: 10px; font-weight: 800; display: inline-block; }
        .status-pass { background-color: #059669; color: #ffffff; }
        .status-warn { background-color: #dc2626; color: #ffffff; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. STABLE DATA ENGINE (ฐานข้อมูลภูมิภาค)
# ==========================================
years_axis = [1930, 1950, 1970, 1990, 2000, 2010, 2026]
months_axis = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

REGIONAL_DB = {
    "📌 CENTRAL": {
        "co2": 421.5, "temp": 1.8, "aqi": 85, "aqi_color": "#eab308",
        "co2_history": [240, 320, 490, 680, 820, 990, 1420],
        "pm25_series": [22, 26, 35, 40, 28, 18, 15, 14, 19, 23, 25, 30],
        "temp_series": [26, 28, 30, 32, 31, 30, 29, 29, 28, 27, 26, 25]
    },
    "📌 NORTH": {
        "co2": 412.8, "temp": 2.4, "aqi": 165, "aqi_color": "#ef4444",
        "co2_history": [210, 270, 410, 550, 690, 840, 1150],
        "pm25_series": [45, 68, 95, 120, 75, 30, 22, 19, 24, 38, 48, 55],
        "temp_series": [20, 23, 27, 31, 30, 29, 28, 28, 27, 25, 22, 19]
    }
}

# ==========================================
# 3. MAIN HEADER
# ==========================================
st.markdown("""
<div class="hdr-box">
    <div class="hdr-title">INTELLIGENT ENVIRONMENTAL & GHG MONITORING DASHBOARD</div>
    <div class="hdr-sub">ระบบควบคุมแดชบอร์ดความหนาแน่นสูง ป้องกันการเปิดแป้นพิมพ์คีย์บอร์ด 100%</div>
</div>
""", unsafe_allow_html=True)

# ==========================================
# 4. TOP CONTROL BAR (เปลี่ยนเป็น st.radio แนวนอน ป้องการพิมพ์ข้อความ)
# ==========================================
ctrl_cols = st.columns([1.5, 3.5, 3.5, 3.5])
with ctrl_cols[0]:
    st.markdown(f'<div style="font-family:monospace; font-size:12px; color:#22d3ee; font-weight:700; margin-top:24px;">⏱️ MONITOR: ACTIVE</div>', unsafe_allow_html=True)
with ctrl_cols[1]:
    # เลือกภูมิภาคผ่านปุ่มกดแท็บ คีย์บอร์ดไม่เด้งแน่นอน
    selected_reg = st.radio("REGION (ภูมิภาค ตรวจสอบ)", list(REGIONAL_DB.keys()), horizontal=True)
with ctrl_cols[2]:
    st.radio("DATA SOURCE (แหล่งอ้างอิง)", ["ALL STATIONS", "SATELLITE API"], horizontal=True)
with ctrl_cols[3]:
    st.radio("TIME FILTER (ช่วงสเกลเวลา)", ["1 MONTH", "30 YEARS TREND"], horizontal=True)

st.markdown("<div style='margin-bottom: 15px;'></div>", unsafe_allow_html=True)
db = REGIONAL_DB[selected_reg]

# ==========================================
# 5. TIER 1: 3 GAUGE CHARTS
# ==========================================
g1, g2, g3 = st.columns(3)

with g1:
    fig_g1 = go.Figure(go.Indicator(
        mode="gauge+number", value=db["co2"],
        title={'text': "1 🔵 ATMOSPHERIC CO₂ LEVEL (PPM)", 'font': {'size': 11, 'color': '#22d3ee', 'bold': True}},
        number={'font': {'size': 20, 'color': '#ffffff'}},
        gauge={'axis': {'range': [350, 500]}, 'bar': {'color': "#22d3ee"}, 'bgcolor': "#020617"}
    ))
    fig_g1.update_layout(height=100, margin=dict(t=30, b=10, l=15, r=15), paper_bgcolor="#1e293b", plot_bgcolor="#1e293b")
    st.plotly_chart(fig_g1, use_container_width=True, config={'displayModeBar': False})

with g2:
    fig_g2 = go.Figure(go.Indicator(
        mode="gauge+number", value=db["temp"],
        title={'text': "2 🟠 AV. TEMPERATURE ANOMALY (°C)", 'font': {'size': 11, 'color': '#f97316', 'bold': True}},
        number={'prefix': "+", 'font': {'size': 20, 'color': '#f97316'}},
        gauge={'axis': {'range': [0, 4]}, 'bar': {'color': "#f97316"}, 'bgcolor': "#020617"}
    ))
    fig_g2.update_layout(height=100, margin=dict(t=30, b=10, l=15, r=15), paper_bgcolor="#1e293b", plot_bgcolor="#1e293b")
    st.plotly_chart(fig_g2, use_container_width=True, config={'displayModeBar': False})

with g3:
    fig_g3 = go.Figure(go.Indicator(
        mode="gauge+number", value=db["aqi"],
        title={'text': "3 🟡 AIR QUALITY INDEX (AQI)", 'font': {'size': 11, 'color': '#eab308', 'bold': True}},
        number={'font': {'size': 20, 'color': db["aqi_color"]}},
        gauge={'axis': {'range': [0, 200]}, 'bar': {'color': db["aqi_color"]}, 'bgcolor': "#020617"}
    ))
    fig_g3.update_layout(height=100, margin=dict(t=30, b=10, l=15, r=15), paper_bgcolor="#1e293b", plot_bgcolor="#1e293b")
    st.plotly_chart(fig_g3, use_container_width=True, config={'displayModeBar': False})

st.markdown("<div style='margin-bottom: 12px;'></div>", unsafe_allow_html=True)

# ==========================================
# 6. TIER 2: MIDDLE SECTION (GRID MATRIX & TRENDS)
# ==========================================
mid_left, mid_right = st.columns([1.1, 1.0])

with mid_left:
    np.random.seed(42)
    grid_data = pd.DataFrame({
        'X_Coordinate': np.random.randint(1, 10, 40),
        'Y_Coordinate': np.random.randint(1, 10, 40),
        'Pollution_Level': np.random.randint(50, 180, 40)
    })
    fig_matrix = px.density_heatmap(grid_data, x='X_Coordinate', y='Y_Coordinate', z='Pollution_Level', 
                                   color_continuous_scale="Jet", title="🔥 REAL-TIME GHG HOTSPOT GRID MATRIX")
    fig_matrix.update_layout(
        height=215, margin=dict(t=35, b=5, l=10, r=10), coloraxis_showscale=False,
        template="plotly_dark", paper_bgcolor="#1e293b", plot_bgcolor="#1e293b",
        title_font=dict(size=11, color="#22d3ee")
    )
    st.plotly_chart(fig_matrix, use_container_width=True, config={'displayModeBar': False})

with mid_right:
    # กราฟบน: 30-Year Trend
    df_30y = pd.DataFrame({'Year': years_axis, 'CO2': db["co2_history"]})
    fig_area = px.area(df_30y, x='Year', y='CO2', template="plotly_dark")
    fig_area.update_traces(line=dict(color='#22d3ee', width=2), fillcolor='rgba(34, 211, 238, 0.1)')
    fig_area.update_layout(
        height=95, margin=dict(t=25, b=5, l=15, r=15), paper_bgcolor="#1e293b", plot_bgcolor="#1e293b",
        title={'text': "📈 30-YEAR CO₂ EMISSIONS TREND (KT/YR)", 'font': {'size': 11, 'color': '#22d3ee', 'bold': True}},
        xaxis_showgrid=False, yaxis_showgrid=False
    )
    st.plotly_chart(fig_area, use_container_width=True, config={'displayModeBar': False})
        
    st.markdown("<div style='margin-bottom: 12px;'></div>", unsafe_allow_html=True)
    
    # กราฟล่าง: Monthly Bars (กราฟผสมสองแกนอย่างมั่นคง)
    fig_combo = make_subplots(specs=[[{"secondary_y": True}]])
    fig_combo.add_trace(go.Bar(x=months_axis, y=db["pm25_series"], name='PM2.5', marker_color='#f97316'), secondary_y=False)
    fig_combo.add_trace(go.Scatter(x=months_axis, y=db["temp_series"], name='Temp', line=dict(color='#22d3ee', width=2)), secondary_y=True)
    fig_combo.update_layout(
        height=95, margin=dict(t=25, b=5, l=15, r=15), template="plotly_dark",
        paper_bgcolor="#1e293b", plot_bgcolor="#1e293b", showlegend=False,
        title={'text': "📊 MONTHLY TEMPERATURE VS. AIR QUALITY", 'font': {'size': 11, 'color': '#22d3ee', 'bold': True}},
        xaxis_showgrid=False, yaxis_showgrid=False
    )
    st.plotly_chart(fig_combo, use_container_width=True, config={'displayModeBar': False})

st.markdown("<div style='margin-bottom: 12px;'></div>", unsafe_allow_html=True)

# ==========================================
# 7. TIER 3: BOTTOM ANALYSIS & WATER TABLE
# ==========================================
bot_left, bot_right = st.columns([1.1, 1.0])

with bot_left:
    elements = ['PM2.5', 'PM10', 'NO₂', 'SO₂']
    fig_stack = go.Figure(data=[
        go.Bar(name='Low', x=elements, y=[75, 85, 110, 120], marker_color='#059669'),
        go.Bar(name='Moderate', x=elements, y=[55, 65, 45, 35], marker_color='#d97706'),
        go.Bar(name='Unhealthy', x=elements, y=[90, 30, 45, 15], marker_color='#dc2626')
    ])
    fig_stack.update_layout(
        barmode='stack', height=140, margin=dict(t=25, b=5, l=10, r=10), template="plotly_dark", 
        paper_bgcolor="#1e293b", plot_bgcolor="#1e293b", showlegend=False,
        title={'text': "📊 POLLUTION BREAKDOWN (PM2.5, NO₂, SO₂)", 'font': {'size': 11, 'color': '#22d3ee', 'bold': True}}
    )
    st.plotly_chart(fig_stack, use_container_width=True, config={'displayModeBar': False})

with bot_right:
    # ตารางคุณภาพน้ำ HTML ล็อกการดาวน์โหลดรายงาน
    st.markdown('<div class="water-card-frame">', unsafe_allow_html=True)
    st.markdown('<div style="font-size: 11px; color: #22d3ee; font-weight: 700; margin-bottom: 6px;">💧 WATER QUALITY MONITORING & EXPORT REPORT</div>', unsafe_allow_html=True)
    
    html_table = """
    <table style="width:100%; border-collapse: collapse; font-size:11px; color:#ffffff; margin-bottom: 6px;">
        <tr style="border-bottom: 1px solid #334155; color:#94a3b8; font-weight:bold; text-align:left;">
            <th style="padding: 2px;">River Station</th>
            <th style="text-align:center; padding: 2px;">DO STATUS</th>
            <th style="text-align:center; padding: 2px;">COD STATUS</th>
        </tr>
        <tr style="border-bottom: 1px solid #334155;">
            <td style="padding: 4px; font-weight:700; color:#22d3ee;">🔵 Chao Phraya (Main)</td>
            <td style="text-align:center;"><span class="status-dot status-pass">DO PASS</span></td>
            <td style="text-align:center;"><span class="status-dot status-warn">COD WARN</span></td>
        </tr>
        <tr>
            <td style="padding: 4px; font-weight:700; color:#22d3ee;">🔵 Tha Chin (Delta)</td>
            <td style="text-align:center;"><span class="status-dot status-pass">DO PASS</span></td>
            <td style="text-align:center;"><span class="status-dot status-pass">DO PASS</span></td>
        </tr>
    </table>
    """
    st.markdown(html_table, unsafe_allow_html=True)
    
    # ปุ่มดาวน์โหลดรายงานวิเคราะห์ไฟล์
    dl_df = pd.DataFrame({'Parameter': ['CO2', 'Temp', 'AQI'], 'Value': [db["co2"], db["temp"], db["aqi"]]})
    csv_bytes = dl_df.to_csv(index=False).encode('utf-8')
    st.download_button(label="📥 DOWNLOAD REPORT (.CSV)", data=csv_bytes, file_name="env_report.csv", mime="text/csv")
    st.markdown('</div>', unsafe_allow_html=True)
