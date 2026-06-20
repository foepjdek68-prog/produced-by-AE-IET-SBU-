import streamlit as st
import pandas as pd
import base64

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

except:
    pass


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

df["Date"] = pd.to_datetime(df["Date"])

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
        <h1>📥 Data Download Center</h1>
        <p>
            Download greenhouse gas monitoring data
            <br>
            Last Update : {latest_date}
        </p>
    </div>
    """,
    unsafe_allow_html=True
)


# =====================================================
# KPI
# =====================================================

c1, c2 = st.columns(2)

c1.metric(
    "Total Records",
    f"{len(df):,}"
)

c2.metric(
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
# SEARCH
# =====================================================

search = st.text_input(
    "🔎 Search Data"
)

if search:

    mask = display_df.astype(str).apply(
        lambda x: x.str.contains(
            search,
            case=False,
            na=False
        )
    ).any(axis=1)

    display_df = display_df[mask]


# =====================================================
# TABLE
# =====================================================

st.subheader("📋 Data Preview")

st.dataframe(
    display_df,
    use_container_width=True,
    height=500
)


# =====================================================
# DOWNLOAD SECTION
# =====================================================

st.markdown("---")

col1, col2 = st.columns(2)

csv = display_df.to_csv(index=False)

with col1:

    st.download_button(
        label="📥 Download CSV",
        data=csv,
        file_name="GHG_Dashboard_Data.csv",
        mime="text/csv",
        use_container_width=True
    )

with col2:

    excel_file = "GHG_Dashboard_Data.xlsx"

    with pd.ExcelWriter(excel_file) as writer:
        display_df.to_excel(
            writer,
            index=False
        )

    with open(excel_file, "rb") as f:

        st.download_button(
            label="📊 Download Excel",
            data=f,
            file_name=excel_file,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
