import streamlit as st
import pandas as pd
import plotly.express as px
import pydeck as pdk
import requests

# =====================================================================
# 1. PAGE CONFIGURATION & ENTERPRISE THEME (CSS)
# =====================================================================
st.set_page_config(
    page_title="ระบบวิเคราะห์ข้อมูลสภาพภูมิอากาศและก๊าซเรือนกระจก",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# บีบระยะห่างและ Layout รอบตัวแอปให้พอดี 1 หน้าจอคอมพิวเตอร์แบบ No-Scroll
st.markdown("""
    <style>
    /* จำกัดพื้นที่หน้าจอหลักไม่ให้หลุดสกรอลล์บาร์ */
    .block-container {
        padding-top: 0.4rem !important;
        padding-bottom: 0px !important;
        padding-left: 1.5rem !important;
        padding-right: 1.5rem !important;
        height: 100vh;
        overflow: hidden;
    }
    
    /* ธีมสีพื้นหลังตามไฟล์ config ของคุณ */
    .stApp {
        background-color: #020617;
    }
    
    /* สไตล์ Dropdown ล็อกไม่ให้เปิดพิมพ์ */
    div[data-baseweb="select"] {
        background-color: #1e293b !important;
        border-radius: 6px !important;
        border: 1px solid #334155 !important;
    }
    div[data-baseweb="select"] input {
        caret-color: transparent !important;
        pointer-events: none !important;
    }
    
    /* บล็อกแสดงตัวเลขสรุป (Metric Cards) แบบคอมแพค */
    div[data-testid="stMetric"] {
        background: linear-gradient(135deg, #1e293b 0%, #020617 100%);
        padding: 4px 10px !important;
        border-radius: 6px;
        border: 1px solid #334155;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    div[data-testid="stMetricLabel"] {
        color: #94a3b8 !important;
        font-size: 11px !important;
        font-weight: 600 !important;
    }
    div[data-testid="stMetricValue"] {
        font-size: 17px !important;
        font-weight: 700 !important;
        color: #22d3ee !important;
    }
    
    /* ปรับแต่งตาราง HTML Table ให้สวยงามและประหยัดพื้นที่แนวตั้งสูงสุด */
    .styled-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 11px;
        color: #e2e8f0;
        margin-top: 4px;
    }
    .styled-table th {
        background-color: #0f172a;
        color: #94a3b8;
        text-align: left;
        padding: 6px 8px;
        font-weight: 600;
        border-bottom: 1px solid #334155;
    }
    .styled-table td {
        padding: 6px 8px;
        border-bottom: 1px solid #1e293b;
    }
    .styled-table tr:hover {
        background-color: #1e293b;
    }
    
    /* ซ่อนแถบเครื่องมือดั้งเดิมของเบราว์เซอร์ */
    footer {visibility: hidden; display: none !important;}
    header {visibility: hidden; display: none !important;}
    div[data-testid="stToolbar"] {visibility: hidden !important;}
    
    /* ดักซ่อนปุ่มดำ "Manage app" ของ Streamlit Cloud ไม่ให้โผล่มากวนใจ */
    div[data-testid="stConnectionStatus"] {display: none !important;}
    .stDeployButton {display: none !important;}
    iframe[title="Manage app"] {display: none !important;}
    div[class^="viewerBadge_container"] {display: none !important;}
    button[title="View source code"] {display: none !important;}
    </style>
    """, unsafe_allow_html=True)

# =====================================================================
# 2. DATA BRIDGE SYSTEM (FastAPI Ready
