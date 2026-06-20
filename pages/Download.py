import streamlit as st
import pandas as pd

from Services.database import load_data, save_data
from Services.api_loader import fetch_data

# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(
    page_title="Download Data",
    page_icon="📥",
    layout="wide"
)

# =====================================================
# SIDEBAR
# =====================================================

with st.sidebar:

    st.image(
        "Assets/logo.png",
        width=280
    )

    st.markdown("<br><br><br><br><br>",
                unsafe_allow_html=True)

    st.markdown("---")

# =====================================================
# CSS
# =====================================================

st.markdown("""
<style>

.block-container{
    padding-top:1rem;
}

[data-testid="stMetric"]{
    background:#111827;
    border:1px solid #374151;
    border-radius:16px;
    padding:15px;
    text-align:center;
}

[data-testid="stMetricValue"]{
    font-size:26px;
    font-weight:700;
}

</style>
""", unsafe_allow_html=True)

# =====================================================
# LOAD DATA
# =====================================================

df = load_data()

if df.empty:
    df = fetch_data()
    save_data(df)

df["Date"] = pd.to_datetime(
    df["Date"],
    errors="coerce"
)

df = df.dropna(subset=["Date"])

latest_date = df["Date"].max()

# =====================================================
# HEADER
# =====================================================

st.markdown(
    f"""
    <div style="
        background:linear-gradient(
            135deg,
            #111827,
            #1F2937
        );
        padding:25px;
        border-radius:20px;
        border:1px solid #374151;
        margin-bottom:20px;
    ">
        <h1>📥 Greenhouse Gas Data Center</h1>

        <p style="color:#9CA3AF;">
            Export and manage environmental monitoring records
        </p>

        <p>
            Last Update :
            {latest_date.strftime("%d/%m/%Y %H:%M")}
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

# =====================================================
# SUMMARY
# =====================================================

st.info(
    f"""
Dataset contains {len(df):,} records
from {df['Date'].min().strftime('%d/%m/%Y')}
to {df['Date'].max().strftime('%d/%m/%Y')}
"""
)

# =====================================================
# KPI
# =====================================================

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "Records",
    f"{len(df):,}"
)

c2.metric(
    "Latest CO₂",
    f"{df['CO2'].iloc[-1]:.2f}"
)

c3.metric(
    "Latest Temp",
    f"{df['Temp'].iloc[-1]:.2f} °C"
)

c4.metric(
    "Last Update",
    latest_date.strftime("%H:%M")
)

st.markdown("---")

# =====================================================
# COLUMN RENAME
# =====================================================

rename_columns = {
    "CO2": "CO₂",
    "CH4": "CH₄",
    "NO2": "NO₂",
    "PM25": "PM 2.5",
    "Temp": "Temperature",
    "Humidity": "Humidity"
}

display_df = df.rename(columns=rename_columns)

# =====================================================
# SEARCH
# =====================================================

st.subheader("🔍 Search Data")

search = st.text_input(
    "ค้นหาข้อมูล"
)

if search:

    mask = (
        display_df.astype(str)
        .apply(
            lambda x: x.str.contains(
                search,
                case=False,
                na=False
            )
        )
        .any(axis=1)
    )

    display_df = display_df[mask]

# =====================================================
# FILTER COLUMN
# =====================================================

selected_column = st.selectbox(
    "เลือกข้อมูล",
    [
        "ทั้งหมด",
        "CO₂",
        "CH₄",
        "NO₂",
        "PM 2.5",
        "Temperature",
        "Humidity"
    ]
)

if selected_column != "ทั้งหมด":

    display_df = display_df[
        ["Date", selected_column]
    ]

# =====================================================
# QUICK STATS
# =====================================================

st.subheader("📊 Quick Statistics")

stats_df = display_df.copy()

if "Date" in stats_df.columns:
    stats_df = stats_df.drop(columns=["Date"])

if len(stats_df.columns) > 0:
    st.dataframe(
        stats_df.describe(),
        use_container_width=True
    )

# =====================================================
# TABLE
# =====================================================

st.subheader("📋 Data Preview")

st.dataframe(
    display_df,
    use_container_width=True,
    height=550
)

# =====================================================
# DOWNLOAD
# =====================================================

st.markdown("---")

col1, col2 = st.columns(2)

csv = display_df.to_csv(
    index=False
)

with col1:

    st.download_button(
        label="📥 Download CSV",
        data=csv,
        file_name="GHG_Dashboard_Data.csv",
        mime="text/csv",
        use_container_width=True
    )

with col2:

    excel_data = display_df.to_csv(
        index=False
    ).encode("utf-8")

    st.download_button(
        label="📊 Export Excel Compatible",
        data=excel_data,
        file_name="GHG_Dashboard_Data.xls",
        mime="application/vnd.ms-excel",
        use_container_width=True
    )
