import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime

# ==========================================
# 1. PREMIUM PRODUCTION-READY CSS STYLESHEET
# ==========================================
st.set_page_config(layout="wide", page_title="Intelligent Environmental & GHG Dashboard")

st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&family=Sarabun:wght@400;700&display=swap');
        
        html, body, [data-testid="stAppViewContainer"] {
            background-color: #0b111e !important;
            color: #f8fafc !important;
            font-family: 'Inter', 'Sarabun', sans-serif;
        }
        
        ::-webkit-scrollbar { display: none; }
        .block-container { padding: 1.5rem 2.5rem !important; }
        
        /* 📦 ตกแต่งกล่อง Container ของ Streamlit ให้พรีเมียมตามแบบฉบับ */
        div[data-testid="stVerticalBlockBorderEffect"] {
            background-color: #121826 !important;
            border: 1px solid #1e293b !important;
            border-radius: 12px !important;
            padding: 18px !important;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
        }
        
        .card-header {
            font-size: 11px;
            font-weight: 800;
            color: #94a3b8;
            letter-spacing: 1px;
            margin-bottom: 8px;
            text-transform: uppercase;
        }
        
        div[data-baseweb="select"] {
            background-color: #1a2333 !important;
            border: 1px solid #2e3c54 !important;
            border-radius: 6px;
        }
        div[data-baseweb="select"] * {
            color: #ffffff !important;
            font-size: 13px !important;
        }
        label[data-testid="stWidgetLabel"] {
            font-size: 11px !important;
            color: #94a3b8 !important;
            font-weight: 700;
            text-transform: uppercase;
        }
