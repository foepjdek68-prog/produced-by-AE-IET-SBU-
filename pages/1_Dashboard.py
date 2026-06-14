import streamlit as st
import plotly.express as px
from datetime import datetime

from Services.database import load_data, save_data
from Services.api_loader import fetch_data



st.title("📊 Dashboard")


df = load_data()


if df.empty:

    df = fetch_data()
    save_data(df)



latest = df.iloc[-1]



date_obj = datetime.fromisoformat(
    str(latest["Date"]).replace("Z","")
)


thai_date = (
    f"{date_obj.day:02d}/"
    f"{date_obj.month:02d}/"
    f"{(date_obj.year+543)%100:02d}"
)



st.caption(
    f"ข้อมูลล่าสุด : {thai_date}"
)



c1,c2,c3,c4,c5,c6 = st.columns(6)



c1.metric(
    "Carbon Dioxide",
    round(float(latest["CO2"]),1)
)

c2.metric(
    "Methane",
    round(float(latest["CH4"]),1)
)

c3.metric(
    "Nitrogen Dioxide",
    round(float(latest["NO2"]),1)
)

c4.metric(
    "PM2.5",
    round(float(latest["PM25"]),1)
)

c5.metric(
    "Temperature",
    round(float(latest["Temp"]),1)
)

c6.metric(
    "Humidity",
    round(float(latest["Humidity"]),1)
)



st.markdown("---")



period = st.selectbox(
    "ช่วงเวลา",
    [
        "Daily",
        "Weekly",
        "Monthly",
        "Annual"
    ]
)



if period == "Daily":

    df_plot = df.tail(24)

elif period == "Weekly":

    df_plot = df.tail(24*7)

elif period == "Monthly":

    df_plot = df.tail(24*30)

else:

    df_plot = df



options = {

    "Carbon Dioxide":"CO2",
    "Methane":"CH4",
    "Nitrogen Dioxide":"NO2",
    "PM2.5":"PM25",
    "Temperature":"Temp",
    "Humidity":"Humidity"

}



selected_label = st.selectbox(
    "เลือกข้อมูล",
    list(options.keys())
)


selected = options[selected_label]



fig = px.line(
    df_plot,
    x="Date",
    y=selected,
    template="plotly_dark"
)



st.plotly_chart(
    fig,
    use_container_width=True
)



st.info(
    f"ค่าเฉลี่ย {selected}: {round(df[selected].mean(),2)}"
)
