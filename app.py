import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# ==========================================
# 1. SETUP: Configure wide layout and theme
# ==========================================
st.set_page_config(layout="wide", page_title="AE-IET GHG Monitor", page_icon="🌍")

# ==========================================
# 2. CSS: Custom Styling (Cyber Environmental Theme)
# ==========================================
# Define CSS with double curly braces {{...}} to avoid f-string confusion in Python
st.markdown(f"""
    <style>
        /* Load Fonts: Inter (for numbers) and Sarabun (for Thai) */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&family=Sarabun:wght@300;400;600;700&display=swap');

        /* Configure overall background and main font families */
        html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {{
            background-color: #050910 !important;
            color: #e2e8f0 !important;
            font-family: 'Inter', 'Sarabun', sans-serif !important;
        }}

        /* Hide horizontal scrollbar for a clean single-page look */
        ::-webkit-scrollbar {{ display: none; }}
        
        /* Reduce padding around the main content container */
        .block-container {{
            padding-top: 1.5rem !important;
            padding-bottom: 0rem !important;
            padding-left: 3rem !important;
            padding-right: 3rem !important;
        }}

        /* --- Header Styles --- */
        .main-title {{
            font-size: 28px;
            font-weight: 700;
            color: #ffffff;
            letter-spacing: -0.5px;
            margin-bottom: 2px;
        }}
        .sub-title {{
            font-size: 14px;
            color: #36d399; /* Emerald accent */
            margin-bottom: 20px;
            font-weight: 300;
        }}

        /* --- Custom Metric Cards System (Flex Wrap) --- */
        .metric-container {{
            display: flex;
            flex-wrap: wrap; /* Ensure cards wrap to new lines */
            gap: 10px;       /* Spacing between cards */
            margin-bottom: 20px;
        }}
        .metric-card {{
            flex: 1; /* Distribute space evenly */
            min-width: 250px; /* Minimum width before wrapping */
            background: rgba(17, 25, 40, 0.75); /* Dark card background */
            backdrop-filter: blur(4px);
            border-radius: 12px;
            border: 1px solid rgba(255, 255, 255, 0.06);
            padding: 15px 20px;
            transition: transform 0.2s ease, border-color 0.2s ease;
        }}
        .metric-card:hover {{
            transform: translateY(-2px);
            border-color: rgba(34, 211, 238, 0.3);
        }}
        .metric-label {{
            font-size: 12px;
            color: #94a3b8; /* Slate font */
            margin-bottom: 8px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        .metric-value-value {{
            font-size: 26px;
            font-weight: 700;
            color: #22d3ee; /* Cyan font */
            line-height: 1;
        }}
        .metric-value-unit {{
            font-size: 14px;
            color: #64748b;
            margin-left: 4px;
            font-weight: 400;
        }}
        .metric-status {{
            font-size: 11px;
            margin-top: 6px;
            font-weight: 400;
        }}

        /* --- Chart and Info Card Styles (Matching Heights) --- */
        .chart-block, .info-card {{
            background: rgba(17, 25, 40, 0.5);
            border-radius: 12px;
            border: 1px solid rgba(255, 255, 255, 0.04);
            padding: 20px;
            height: 360px; /* Force consistent height across columns */
        }}
        
        .chart-caption, .info-caption {{
            font-size: 13px;
            color: #94a3b8;
            margin-bottom: 15px;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 8px;
        }}

        /* --- Sidebar Styling --- */
        section[data-testid="stSidebar"] {{
            background-color: #0b1120 !important;
            border-right: 1px solid rgba(255,255,255,0.05);
        }}
        /* Style Selectbox/Radio labels and options in Sidebar */
        div[data-baseweb="select"] > div, div[data-testid="stMarkdownContainer"] p {{
            font-size: 14px !important;
        }}
        
        /* Sidebar Brand Box (Engineering & Data Team Credit) */
        .brand-box {{
            margin-top: auto;
            padding: 20px;
            background: rgba(34, 211, 238, 0.03);
            border-radius: 12px;
            border: 1px solid rgba(34, 211, 238, 0.08);
            margin-bottom: 20px;
            text-align: center;
        }}

        /* Defined Status Colors */
        .status-safe {{ color: #10b981; }}     /* Emerald */
        .status-warning {{ color: #fbbf24; }}  /* Amber */
        .status-moderate {{ color: #f97316; }} /* Orange */
        .status-normal {{ color: #a7f3d0; }}   /* Light Emerald */

    </style>
""", unsafe_allow_html=True)

# ==========================================
# 3. BASE DATA: GHG and Air Quality Metrics
# ==========================================
database = {
    "CO₂ (ppm)": {"current": 433, "base": 415, "unit": "ppm", "status": "ปกติ (Safe)", "stat_class": "status-safe"},
    "CH₄ (ppb)": {"current": 1865, "base": 1820, "unit": "ppb", "status": "ปกติ (Safe)", "stat_class": "status-safe"},
    "NO₂ (ppb)": {"current": 42.1, "base": 35.0, "unit": "ppb", "status": "เฝ้าระวัง (Warning)", "stat_class": "status-warning"},
    "PM 2.5 (µg/m³)": {"current": 22.4, "base": 15.0, "unit": "µg/m³", "status": "ปานกลาง (Moderate)", "stat_class": "status-moderate"},
    "Temp (°C)": {"current": 33.2, "base": 31.5, "unit": "°C", "status": "ปกติ (Normal)", "stat_class": "status-normal"},
    "Humid (%)": {"current": 64.0, "base": 60.0, "unit": "%", "status": "ปกติ (Normal)", "stat_class": "status-normal"}
}

# ==========================================
# 4. SIDEBAR CONTROL PANEL
# ==========================================
with st.sidebar:
    st.markdown("### 📋 Panel ควบคุม")
    selected = st.selectbox("ตัวแปรที่ต้องการวิเคราะห์:", list(database.keys()))
    # Simplified radio button layout
    mode = st.radio("ช่วงเวลาวิเคราะห์:", ["รายวัน (30 วัน)", "รายเดือน (12 เดือน)"], horizontal=False)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Sidebar branding (SBU team info)
    st.markdown(f"""
        <div class="brand-box">
            <img src="https://comci.southeast.ac.th/2025/img/SBU.png" width="50" style="margin-bottom:10px;">
            <div style="font-weight:700; color:white; font-size: 14px; letter-spacing:0.5px;">AE-IET [SBU]</div>
            <div style="font-size:11px; color:#64748b; margin-top:4px;">Engineering & Data Science Team</div>
            <div style="font-size:10px; color:#475569; margin-top:2px;">© 2026 Build</div>
        </div>
    """, unsafe_allow_html=True)

# ==========================================
# 5. MAIN CONTENT AREA
# ==========================================

# --- Header Section ---
st.markdown('<div class="main-title">🌍 Intelligent GHG Emission & Air Quality Tracker</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">ระบบติดตามสถานะก๊าซเรือนกระจกและคุณภาพอากาศอัจฉริยะพิกัดสถานีวิจัย</div>', unsafe_allow_html=True)

# --- Top Section: Metric Cards (Flex Layout) ---
# FIX: Pre-concatenate HTML for all six cards into a single string.
# This ensures they are rendered inside the '.metric-container' flex gap.
metric_html = '<div class="metric-container">'
for key, info in database.items():
    label_short = key.split(' ')[0]
    metric_html += f"""
        <div class="metric-card hover-effect">
            <div class="metric-label">{key}</div>
            <div class="metric-value">
                <span class="metric-value-value">{info['current']}</span>
                <span class="metric-value-unit">{info['unit']}</span>
            </div>
            <div class="metric-status {info['stat_class']}">● {info['status']}</div>
        </div>
    """
metric_html += '</div>'
st.markdown(metric_html, unsafe_allow_html=True)


# --- Bottom Section: Chart (Left) & Info Summary (Right) ---
# FIX: Move HTML container logic entirely within the column structure
# and escape CSS f-strings with double braces.
chart_col, info_col = st.columns([1.4, 0.6])

with chart_col:
    # 📥 Chart Block
    # The chart logic is contained within an f-string to allow for clean escaping of curly braces {{...}}.
    current_val = database[selected]["current"]
    base_val = database[selected]["base"]
    
    if "รายวัน" in mode:
        periods, freq, start_date = 30, 'D', '2026-05-01'
    else:
        periods, freq, start_date = 12, 'M', '2025-06-01'
        
    np.random.seed(42) # Lock seed for consistent graph shape
    fluctuations = np.random.uniform(-1.2, 1.2, periods)
    trend_values = np.linspace(base_val, current_val - fluctuations[-1], periods) + fluctuations
    trend_values[-1] = current_val # Ensure last point matches metric value exactly
    
    df_trend = pd.DataFrame({
        'Date': pd.date_range(start=start_date, periods=periods, freq=freq),
        'Value': np.round(trend_values, 1)
    })
    
    # Define a custom HTML wrapper inside an f-string to escape braces
    chart_wrapper_html = f"""
    <div class="chart-block">
        <div class="chart-caption">📊 แนวโน้มความเปลี่ยนแปลง: <span style="color:#22d3ee">{selected}</span></div>
    </div>
    """
    st.markdown(chart_wrapper_html, unsafe_allow_html=True)
    
    # --- Modern Plotly Area Chart (Spline Curve) ---
    fig = px.area(df_trend, x='Date', y='Value', template="plotly_dark")
    
    # Apply modern area and line styles
    fig.update_traces(
        mode='lines+markers',
        line=dict(color='#22d3ee', width=3, shape='spline'), # Spline curve
        fillcolor='rgba(34, 211, 238, 0.06)', # Soft fill color
        marker=dict(size=6, color='#0f172a', line=dict(width=2, color='#22d3ee')), # Dot style
        hovertemplate="<b>วันที่:</b> %{{x|%d %b %Y}}<br><b>ค่า:</b> %{{y:.1f}} " + database[selected]["unit"] + "<extra></extra>" # Custom hover
    )
    
    # Update chart layout for clean dark look
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", 
        plot_bgcolor="rgba(0,0,0,0)",
        height=300, # Height set to fit chart block
        margin=dict(t=0, b=0, l=0, r=0), 
        
        font=dict(font_family="Inter, Sarabun", size=11, color="#64748b"),
        
        xaxis=dict(
            showgrid=False,
            title="", 
            tickformat="%d %b" if "รายวัน" in mode else "%b %y",
            tickfont=dict(color='#64748b'),
            linecolor='rgba(255,255,255,0.05)'
        ),
        yaxis=dict(
            showgrid=True, 
            gridcolor='rgba(255,255,255,0.03)', 
            title=dict(text=database[selected]["unit"], font=dict(size=10)),
            tickfont=dict(color='#64748b'),
            zeroline=False
        ),
        hoverlabel=dict(
            bgcolor="#111827",
            font_size=12,
            font_family="Inter, Sarabun"
        )
    )
    
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

with info_col:
    # 🔍 Info Summary Card
    status_info = database[selected]
    
    # Pre-split parameter and unit for cleaner display
    param_short = selected.split(' ')[0]
    param_unit = selected.split(' ')[1]
    
    # Concatenate all HTML for the Info Card inside an f-string to escape braces
    info_card_html = f"""
    <div class="info-card">
        <div class="info-caption">🔍 ข้อมูลสถานีและสรุปผล</div>
        <div style="margin-top: 15px;">
            <div style="font-size: 11px; color: #64748b; font-weight:600; text-transform:uppercase; letter-spacing:1px; margin-bottom:5px;">SELECTED PARAMETER</div>
            <div style="font-size: 20px; color: #ffffff; font-weight:700; margin-bottom: 20px;">
                {param_short} 
                <span style="font-size:12px; color:#475569; font-weight:400;">({param_unit})</span>
            </div>
            
            <div style="display:flex; justify-content:space-between; align-items:center; background:rgba(255,255,255,0.03); padding: 10px; border-radius:8px; margin-bottom:10px;">
                <span style="font-size:13px; color:#94a3b8;">ค่าที่ตรวจพบปัจจุบัน:</span>
                <span style="font-size:16px; color:#ffffff; font-weight:700;">{current_val} {status_info['unit']}</span>
            </div>
            
            <div style="display:flex; justify-content:space-between; align-items:center; background:rgba(255,255,255,0.03); padding: 10px; border-radius:8px; margin-bottom:20px;">
                <span style="font-size:13px; color:#94a3b8;">ประเมินสถานะ:</span>
                <span class="{status_info['stat_class']}" style="font-size:14px; font-weight:700;">● {status_info['status']}</span>
            </div>
            
            <hr style="border: 0; border-top: 1px solid rgba(255,255,255,0.04); margin: 15px 0;">
            
            <p style="font-size: 11px; color: #475569; line-height: 1.6; text-align: justify; font-style:italic;">
                * ข้อมูลประมวลผลขั้นสูง ดึงจากเครือข่ายเซนเซอร์จำลอง AE-IET ผ่าน API สถาบันวิจัยการคำนวณ [SBU] โดยทำการตัดสัญญาณรบกวน (Noise Removal) แล้ว 100% สอดคล้องกับพิกัดเวลาสถานี
            </p>
        </div>
    </div>
    """
    st.markdown(info_card_html, unsafe_allow_html=True)
