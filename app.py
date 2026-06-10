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
        div[data-baseweb="select"] { background-color: #0f172a !important; border
