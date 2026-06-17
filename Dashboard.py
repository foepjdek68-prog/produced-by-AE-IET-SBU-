from PIL import Image
import streamlit as st
import plotly.express as px
import pandas as pd

from Services.database import load_data, save_data
from Services.api_loader import fetch_data

st.set_page_config(
    page_title="Dashboard Tracking Greenhouse Gases Emission",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================
# LOGO
# =========================

logo = Image.open("Assets/logo.png")

with st.sidebar:

    st.markdown(
        """
        <div style="margin-top:40px;"></div>
        """,
        unsafe_allow_html=True
    )

    st.image(
        logo,
        use_container_width=True
    )

    st.markdown(
        """
        <div style="
            text-align:center;
            color:#9ca3af;
            font-size:12px;
            margin-top:-5px;
            margin-bottom:10px;
        ">
            SBU • DTI
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("---")

# =========================
# STYLE
# =========================

st.markdown("""
<style>

[data-testid="stMetric"]{
    background:#111827;
    border-left:4px solid #F5B335;
    border-top:1px solid #374151;
    border-right:1px solid #374151;
    border-bottom:1px solid #374151;
    padding:15px;
    border-radius:12px;
}

.block-container{
    padding-top:1rem;
}

</style>
""", unsafe_allow_html=True)
