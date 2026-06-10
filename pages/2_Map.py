import streamlit as st
import pandas as pd
import pydeck as pdk

st.title("🗺️ Thailand Monitoring Map")

map_df = pd.DataFrame({

    "lat":[13.7563],
    "lon":[100.5018],
    "value":[430]

})

st.pydeck_chart(
    pdk.Deck(

        initial_view_state=pdk.ViewState(
            latitude=13.7563,
            longitude=100.5018,
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
