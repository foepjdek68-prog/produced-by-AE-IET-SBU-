import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import pytz
import os

# ===== PAGE SETTING =====

st.set_page_config(
    layout="wide",
    page_title="GHG Monitor Board",
    initial_sidebar_state="expanded"
)

# ===== CSS =====

st.markdown("""
<style>

::-webkit-scrollbar {
    display: none;
}

.stApp {
    overflow: hidden !important;
    height: 100vh !important;
}

[data-testid="stMetric"] {
    background: #161b22;
    padding: 8px !important;
    border-radius: 10px;
    border: 1px solid #30363d;
}

[data-testid="stMetricValue"] {
    font-size: 20px !important;
}

[data-testid="stMetricLabel"] {
    font-size: 12px !important;
}

section[data-testid="stSidebar"] > div {
    display: flex;
    flex-direction: column;
    height: 100vh;
}

.brand-box {
    margin-top: auto;
    padding: 15px;
    background: rgba(255,255,255,0.03);
    border-radius: 10px;
}

</style>
""", unsafe_allow_html=True)

# ===== LOAD DATA =====

DATA_FILE = "ghg_data.csv"

def get_sensor_data():

    bkk_tz = pytz.timezone("Asia/Bangkok")

    now = datetime.now(bkk_tz)

    current_hour = now.replace(
        minute=0,
        second=0,
        microsecond=0
    )

    if os.path.exists(DATA_FILE):

        df = pd.read_csv(DATA_FILE)

        df["Date"] = pd.to_datetime(df["Date"])

    else:

        df = pd.DataFrame(columns=[
            "Date",
            "CO₂ (ppm)",
            "CH₄ (ppb)",
            "NO₂ (ppb)",
            "PM 2.5 (µg/m³)",
            "Temp (°C)",
            "Humid (%)"
        ])

    return df, now, current_hour

# ===== GET CURRENT DATA =====

df, current_time, current_hour = get_sensor_data()

# ===== UPDATE DATA =====

if len(df) == 0:

    first_row = {
        "Date": current_hour,
        "CO₂ (ppm)": 415,
        "CH₄ (ppb)": 1850,
        "NO₂ (ppb)": 40,
        "PM 2.5 (µg/m³)": 25,
        "Temp (°C)": 33,
        "Humid (%)": 60
    }

    df.loc[len(df)] = first_row

else:

    last_time = pd.to_datetime(df.iloc[-1]["Date"])

    if last_time != current_hour:

        new_row = {
            "Date": current_hour,
            "CO₂ (ppm)": df.iloc[-1]["CO₂ (ppm)"],
            "CH₄ (ppb)": df.iloc[-1]["CH₄ (ppb)"],
            "NO₂ (ppb)": df.iloc[-1]["NO₂ (ppb)"],
            "PM 2.5 (µg/m³)": df.iloc[-1]["PM 2.5 (µg/m³)"],
            "Temp (°C)": df.iloc[-1]["Temp (°C)"],
            "Humid (%)": df.iloc[-1]["Humid (%)"]
        }

        df.loc[len(df)] = new_row

df.to_csv(DATA_FILE, index=False)

latest_data = df.iloc[-1]

# ===== SIDEBAR =====

with st.sidebar:

    st.markdown("### 📋 เมนูควบคุม")

    pollutants = [
        col for col in df.columns
        if col != "Date"
    ]

    selected_pollutant = st.selectbox(
        "สารมลพิษที่ต้องการดูสถิติ:",
        pollutants
    )

    period = st.selectbox(
        "ช่วงเวลา",
        [
            "24 ชั่วโมง",
            "7 วัน",
            "30 วัน",
            "90 วัน",
            "ทั้งหมด"
        ]
    )

    if st.button("🔄 อัปเดตข้อมูลตอนนี้"):
        st.rerun()

    st.markdown("""
    <div class="brand-box">
        <div style="font-weight:bold;color:white;">
            AE-IET [SBU]
        </div>
        <div style="font-size:10px;color:#888;">
            Engineering Team
        </div>
    </div>
    """, unsafe_allow_html=True)

# ===== FILTER DATA =====

if period == "24 ชั่วโมง":

    df_show = df.tail(24)

elif period == "7 วัน":

    df_show = df.tail(24 * 7)

elif period == "30 วัน":

    df_show = df.tail(24 * 30)

elif period == "90 วัน":

    df_show = df.tail(24 * 90)

else:

    df_show = df

# ===== HEADER =====

col_title, col_time = st.columns([2, 1])

with col_title:

    st.title("🌍 Tracking GHGs Emission")

with col_time:

    st.markdown(
        f"""
        <div style='text-align:right;
                    margin-top:25px;
                    color:#888;'>
        🕒 {current_time.strftime('%Y-%m-%d %H:%M:%S')}
        </div>
        """,
        unsafe_allow_html=True
    )

# ===== METRICS =====

latest_data = df_show.iloc[-1]

cols = st.columns(6)

for i, col_name in enumerate(pollutants):

    val = latest_data[col_name]

    if len(df_show) > 1:

        delta_val = round(
            val - df_show.iloc[-2][col_name],
            1
        )

    else:

        delta_val = 0

    cols[i].metric(
        label=col_name,
        value=f"{val}",
        delta=f"{delta_val}"
    )

# ===== GRAPH =====

fig = px.line(
    df_show,
    x="Date",
    y=selected_pollutant,
    title=f"แนวโน้ม {selected_pollutant}",
    template="plotly_dark",
    height=450
)

fig.update_traces(
    line_color="#00ffcc",
    line_width=3
)

fig.update_layout(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    margin=dict(
        t=40,
        b=10,
        l=10,
        r=10
    ),
    xaxis_title=None,
    yaxis_title=None
)

st.plotly_chart(
    fig,
    use_container_width=True
)
