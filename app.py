import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime

# ==========================================
# 1. PAGE AND ASSET CONFIGURATION
# ==========================================
st.set_page_config(layout="wide", page_title="Intelligent Environmental & GHG Dashboard")

# Injection of Custom Enterprise CSS Style
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght=400;600;700;800&family=Sarabun:wght=400;700&display=swap');
        
        html, body, [data-testid="stAppViewContainer"] {
            background-color: #0b111e !important;
            color: #f8fafc !important;
            font-family: 'Inter', 'Sarabun', sans-serif;
        }
        
        ::-webkit-scrollbar { display: none; }
        .block-container { padding: 1.5rem 2.5rem !important; }
        
        .stElementContainer div[data-testid="stVerticalBlockBorderEffect"] {
            background-color: #121826 !important;
            border: 1px solid #1e293b !important;
            border-radius: 12px !important;
            padding: 20px !important;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
        }
        
        .card-header {
            font-size: 11px;
            font-weight: 800;
            color: #94a3b8;
            letter-spacing: 1px;
            margin-bottom: 12px;
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
        
        .river-table { width: 100%; border-collapse: collapse; margin-top: 5px; }
        .river-row { height: 45px; border-bottom: 1px solid #1e293b; }
        .river-name { font-size: 13px; font-weight: 700; color: #38bdf8; width: 30%; }
        .river-wave { width: 40%; text-align: center; }
        .river-badges { width: 30%; text-align: right; display: flex; justify-content: flex-end; gap: 8px; align-items: center; height: 45px; }
        .status-badge {
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 10px;
            font-weight: 800;
            color: #ffffff;
            letter-spacing: 0.5px;
