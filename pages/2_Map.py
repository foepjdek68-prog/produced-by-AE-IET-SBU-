import streamlit as st
import pandas as pd
import pydeck as pdk

st.title("🗺️ Thailand Monitoring Map")

map_df = pd.DataFrame({
    "lat": [13.75, 18.79, 7.88],
    "lon": [100.50, 98.98, 98.39],
    "city": ["Bangkok", "Chiang Mai", "Phuket"]
})

st.pydeck_chart(
    pdk.Deck(
        initial_view_state=pdk.ViewState(
            latitude=13.75,
            longitude=100.50,
            zoom=5
        ),
        layers=[
            pdk.Layer(
                "ScatterplotLayer",
                data=map_df,
                get_position='[lon, lat]',
                get_radius=50000
            )
        ]
    )
)
