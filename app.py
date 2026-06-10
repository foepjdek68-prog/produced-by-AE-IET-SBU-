import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

st.set_page_config(
page_title="Environmental Dashboard",
layout="wide"
)

# =========================

# THEME

# =========================

st.markdown("""

<style>

[data-testid="stAppViewContainer"]{
    background: linear-gradient(
        rgba(2,6,23,0.72),
        rgba(2,6,23,0.72)
    ),
    url("https://images.unsplash.com/photo-1569163139394-de4e4f43e4e3");
    background-size:cover;
    background-position:center;
    background-attachment:fixed;
}

.block-container{
    padding-top:1rem;
    padding-bottom:0.5rem;
}

.main-card{
    background:rgba(15,23,42,0.72);
    border:1px solid rgba(255,255,255,0.08);
    border-radius:14px;
    padding:12px;
}

.hdr-title{
    text-align:center;
    color:white;
    font-size:42px;
    font-weight:800;
    line-height:1.1;
}

.hdr-sub{
    text-align:center;
    color:#dbeafe;
    font-size:18px;
    margin-bottom:10px;
}

.metric-card{
    background:rgba(15,23,42,0.75);
    border-radius:12px;
    border:1px solid rgba(255,255,255,0.08);
    padding:10px;
}

</style>

""", unsafe_allow_html=True)

now = datetime.now().strftime("%B %Y | %H:%M:%S")

st.markdown(
f"""

<div class="hdr-title">
INTELLIGENT ENVIRONMENTAL & GHG<br>
MONITORING DASHBOARD (THAILAND)
</div>

<div class="hdr-sub">
แดชบอร์ดอัจฉริยะติดตามก๊าซเรือนกระจกและมลพิษ (ประเทศไทย)
</div>

<div style="color:white;font-size:24px;font-weight:700;">
{now}
</div>
""",
unsafe_allow_html=True
)
years_axis = [1930,1950,1970,1990,2000,2010,2026]

months_axis = [
"Jan","Feb","Mar","Apr",
"May","Jun","Jul","Aug",
"Sep","Oct","Nov","Dec"
]

REGIONAL_DB = {

```
"CENTRAL": {
    "co2":421.5,
    "temp":1.8,
    "aqi":85,
    "aqi_color":"#fbbf24",

    "co2_history":[
        240,320,490,680,
        820,990,1150
    ],

    "pm25_series":[
        5,8,12,18,22,28,
        34,30,16,10,14,12
    ],

    "temp_series":[
        17,17,18,19,21,22,
        23,22,21,19,19,18
    ]
}
```

}

ctrl1,ctrl2,ctrl3,ctrl4 = st.columns(4)

with ctrl1:
st.markdown(
"<div style='margin-top:35px;color:#93c5fd;font-weight:bold'>LIVE DATA</div>",
unsafe_allow_html=True
)

with ctrl2:
region = st.selectbox(
"REGION",
list(REGIONAL_DB.keys())
)

with ctrl3:
st.selectbox(
"DATA SOURCE",
["ALL","SATELLITE","GROUND"]
)

with ctrl4:
st.selectbox(
"TIME",
["1 MONTH","1 YEAR","30 YEARS"]
)

db = REGIONAL_DB[region]
st.markdown("### KEY ENVIRONMENTAL METRICS")

g1,g2,g3 = st.columns(3)

with g1:

```
fig = go.Figure(go.Indicator(
    mode="gauge+number",
    value=db["co2"],

    number={
        "suffix":" ppm",
        "font":{"size":42}
    },

    title={
        "text":"ATMOSPHERIC CO₂ LEVEL"
    },

    gauge={
        "axis":{"range":[0,500]},
        "bar":{"color":"#38bdf8"},

        "bgcolor":"#0f172a",

        "steps":[
            {"range":[0,250],"color":"#164e63"},
            {"range":[250,500],"color":"#0ea5e9"}
        ]
    }
))

fig.update_layout(
    height=250,
    paper_bgcolor="rgba(15,23,42,0.75)",
    font={"color":"white"}
)

st.plotly_chart(
    fig,
    use_container_width=True,
    config={"displayModeBar":False}
)
```

with g2:

```
fig = go.Figure(go.Indicator(
    mode="gauge+number",

    value=db["temp"],

    number={
        "prefix":"+",
        "suffix":"°C",
        "font":{"size":42}
    },

    title={
        "text":"AV. TEMPERATURE ANOMALY"
    },

    gauge={
        "axis":{"range":[0,4]},

        "bar":{
            "color":"#fb923c"
        },

        "steps":[
            {"range":[0,2],"color":"#7c2d12"},
            {"range":[2,4],"color":"#ea580c"}
        ]
    }
))

fig.update_layout(
    height=250,
    paper_bgcolor="rgba(15,23,42,0.75)",
    font={"color":"white"}
)

st.plotly_chart(
    fig,
    use_container_width=True,
    config={"displayModeBar":False}
)
```

with g3:

```
fig = go.Figure(go.Indicator(
    mode="gauge+number",

    value=db["aqi"],

    title={
        "text":"AIR QUALITY INDEX"
    },

    gauge={
        "axis":{"range":[0,200]},
        "bar":{"color":"#fbbf24"},

        "steps":[
            {"range":[0,100],"color":"#78350f"},
            {"range":[100,200],"color":"#f59e0b"}
        ]
    }
))

fig.update_layout(
    height=250,
    paper_bgcolor="rgba(15,23,42,0.75)",
    font={"color":"white"}
)

st.plotly_chart(
    fig,
    use_container_width=True,
    config={"displayModeBar":False}
)
```
left,right = st.columns([1.2,1])

with left:

```
map_df = pd.DataFrame({
    "lat":[13.75,13.80,13.60,13.95,13.70],
    "lon":[100.50,100.60,100.45,100.70,100.30],
    "intensity":[150,130,90,80,110]
})

fig_map = px.scatter_mapbox(
    map_df,
    lat="lat",
    lon="lon",
    size="intensity",
    color="intensity",
    zoom=8,
    center={
        "lat":13.75,
        "lon":100.52
    },
    mapbox_style="carto-darkmatter",
    color_continuous_scale=[
        "green",
        "yellow",
        "red"
    ]
)

fig_map.update_layout(
    height=450,
    margin=dict(
        l=0,
        r=0,
        t=40,
        b=0
    ),
    paper_bgcolor="rgba(15,23,42,0.75)"
)

fig_map.update_coloraxes(
    showscale=False
)

st.plotly_chart(
    fig_map,
    use_container_width=True,
    config={"displayModeBar":False}
)
```

with right:

```
trend_df = pd.DataFrame({
    "Year":years_axis,
    "CO2":db["co2_history"]
})

fig_area = px.area(
    trend_df,
    x="Year",
    y="CO2"
)

fig_area.update_traces(
    line_color="#93c5fd",
    fillcolor="rgba(147,197,253,0.3)"
)

fig_area.update_layout(
    title="30-YEAR CO₂ EMISSIONS TREND",
    height=220,
    paper_bgcolor="rgba(15,23,42,0.75)",
    plot_bgcolor="rgba(15,23,42,0.75)",
    font={"color":"white"}
)

st.plotly_chart(
    fig_area,
    use_container_width=True,
    config={"displayModeBar":False}
)

combo = go.Figure()

combo.add_trace(
    go.Bar(
        x=months_axis,
        y=db["pm25_series"],
        marker_color="#f59e0b",
        name="PM2.5"
    )
)

combo.add_trace(
    go.Scatter(
        x=months_axis,
        y=db["temp_series"],
        line=dict(
            color="#e0f2fe",
            width=3
        ),
        name="Temperature",
        yaxis="y2"
    )
)

combo.update_layout(
    title="MONTHLY TEMPERATURE VS AIR QUALITY",
    height=220,
    paper_bgcolor="rgba(15,23,42,0.75)",
    plot_bgcolor="rgba(15,23,42,0.75)",
    font={"color":"white"},
    yaxis2=dict(
        overlaying="y",
        side="right"
    )
)

st.plotly_chart(
    combo,
    use_container_width=True,
    config={"displayModeBar":False}
)
```
st.markdown("---")

bottom_left,bottom_right = st.columns([1,1])

# =====================================

# POLLUTION BREAKDOWN

# =====================================

with bottom_left:

```
pollutants = [
    "PM2.5",
    "PM10",
    "NO₂",
    "SO₂"
]

fig_stack = go.Figure()

fig_stack.add_trace(
    go.Bar(
        name="LOW",
        x=pollutants,
        y=[100,120,140,130],
        marker_color="#22c55e"
    )
)

fig_stack.add_trace(
    go.Bar(
        name="MODERATE",
        x=pollutants,
        y=[60,70,50,80],
        marker_color="#f59e0b"
    )
)

fig_stack.add_trace(
    go.Bar(
        name="UNHEALTHY",
        x=pollutants,
        y=[95,65,85,75],
        marker_color="#ef4444"
    )
)

fig_stack.update_layout(
    barmode="stack",
    height=300,
    title="POLLUTION BREAKDOWN (PM2.5, NO₂, SO₂)",
    paper_bgcolor="rgba(15,23,42,0.75)",
    plot_bgcolor="rgba(15,23,42,0.75)",
    font={"color":"white"},
    legend=dict(
        orientation="h",
        y=1.1
    )
)

st.plotly_chart(
    fig_stack,
    use_container_width=True,
    config={"displayModeBar":False}
)
```

# =====================================

# WATER QUALITY

# =====================================

with bottom_right:

```
st.markdown(
    """
    <div style="
    background:rgba(15,23,42,0.75);
    padding:15px;
    border-radius:12px;
    border:1px solid rgba(255,255,255,0.1);
    ">
    <h4 style="color:white;">
    💧 WATER QUALITY MONITORING
    </h4>
    </div>
    """,
    unsafe_allow_html=True
)

water_df = pd.DataFrame({
    "River Station":[
        "Chao Phraya",
        "Tha Chin",
        "Bang Pakong"
    ],

    "DO":[
        "PASS",
        "PASS",
        "PASS"
    ],

    "COD":[
        "WARN",
        "PASS",
        "WARN"
    ]
})

st.dataframe(
    water_df,
    use_container_width=True,
    hide_index=True
)

st.markdown("### Export Report")

export_df = pd.DataFrame({

    "Parameter":[
        "CO2",
        "Temperature",
        "AQI"
    ],

    "Value":[
        db["co2"],
        db["temp"],
        db["aqi"]
    ]
})

csv = export_df.to_csv(
    index=False
).encode(
    "utf-8-sig"
)

st.download_button(
    "📥 DOWNLOAD REPORT (.CSV)",
    csv,
    file_name="environment_report.csv",
    mime="text/csv"
)
```

# =====================================

# FOOTER

# =====================================

st.markdown("<br>", unsafe_allow_html=True)

st.markdown(
""" <div style="
 text-align:center;
 color:#94a3b8;
 font-size:12px;
 padding:10px;
 ">
Intelligent Environmental & GHG Monitoring Dashboard © 2026 </div>
""",
unsafe_allow_html=True
)
