import streamlit as st
import pandas as pd
import base64
from io import BytesIO

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
# LOGO FUNCTION
# =====================================================

def get_base64_image(path):
    with open(path, "rb") as img:
        return base64.b64encode(img.read()).decode()


# =====================================================
# SIDEBAR
# =====================================================

try:

    sbu_logo = get_base64_image("Assets/sbu.png")
    dti_logo = get_base64_image("Assets/dti.png")

    with st.sidebar:

        st.markdown(
            f"""
            <div style="
                text-align:center;
                padding:15px;
                background:#111827;
                border-radius:15px;
                border:1px solid #374151;
            ">

                <img src="data:image/png;base64,{sbu_logo}"
                     width="150">

                <br><br>

                <img src="data:image/png;base64,{dti_logo}"
                     width="180">

                <hr>

                <h4 style="color:white;">
                    Greenhouse Gas
                    Monitoring System
                </h4>

            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown("---")

        st.caption("Data Export Center")

        st.write("📄 CSV Export")
        st.write("📊 Excel Export")
        st.write("🔎 Data Preview")

except Exception:
    st.sidebar.warning("Logo not found")


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
    border-radius:12px;
    padding:15px;
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
        background:#111827;
        padding:20px;
        border-radius:15px;
        border:1px solid #374151;
        margin-bottom:20px;
    ">
        <h1>📥 Greenhouse Gas Data Center</h1>
        <p>
            Export and manage environmental monitoring records
            <br>
            Last Update : {latest_date.strftime("%d/%m/%Y %H:%M")}
        </p>
    </div>
    """,
    unsafe_allow_html=True
)


# =====================================================
# KPI
# =====================================================

c1, c2 = st.columns(2)

with c1:
    st.metric(
        "Total Records",
        f"{len(df):,}"
    )

with c2:
    st.metric(
        "Last Update",
        latest_date.strftime("%d/%m/%Y %H:%M")
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
# FILTER
# =====================================================

st.subheader("🔎 Filter Data")

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
# TABLE
# =====================================================

st.subheader("📋 Data Preview")

st.dataframe(
    display_df,
    use_container_width=True,
    height=550
)

# =====================================================
# DOWNLOAD SECTION
# =====================================================

st.markdown("---")

col1, col2 = st.columns(2)

# ---------- CSV ----------

csv = display_df.to_csv(index=False)

with col1:

    st.download_button(
        label="📥 Download CSV",
        data=csv,
        file_name="GHG_Dashboard_Data.csv",
        mime="text/csv",
        use_container_width=True
    )

# ---------- EXCEL ----------

with col2:

    export_df = display_df.copy()

    if "Date" in export_df.columns:
        export_df["Date"] = pd.to_datetime(
            export_df["Date"]
        ).dt.tz_localize(None)

    csv_excel = export_df.to_csv(
        index=False
    ).encode("utf-8")

    st.download_button(
        label="📊 Download Excel",
        data=csv_excel,
        file_name="GHG_Dashboard_Data.xls",
        mime="application/vnd.ms-excel",
        use_container_width=True
    )
