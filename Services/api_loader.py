import pandas as pd
import numpy as np
from datetime import datetime
import pytz
import os


DATA_FILE = "Services/sensor_data.csv"


def generate_new_record():

    tz = pytz.timezone("Asia/Bangkok")
    now = datetime.now(tz)


    data = {

        "Date": now,

        "CO2": np.random.normal(430, 8),
        "CH4": np.random.normal(1860, 15),
        "NO2": np.random.normal(42, 3),
        "PM25": np.random.normal(25, 5),
        "Temp": np.random.normal(33, 2),
        "Humidity": np.random.normal(60, 4)

    }


    return pd.DataFrame([data]).round(2)



def fetch_data():

    new_data = generate_new_record()


    # ถ้ามี database จำลองอยู่แล้ว
    if os.path.exists(DATA_FILE):

        old = pd.read_csv(DATA_FILE)

        old["Date"] = pd.to_datetime(old["Date"])

        df = pd.concat(
            [
                old,
                new_data
            ],
            ignore_index=True
        )


    else:

        # สร้างข้อมูลย้อนหลังครั้งแรก
        tz = pytz.timezone("Asia/Bangkok")

        dates = pd.date_range(
            end=datetime.now(tz),
            periods=365*24,
            freq="h"
        )


        history = pd.DataFrame({

            "Date": dates,

            "CO2":
            np.random.normal(430,8,len(dates)),

            "CH4":
            np.random.normal(1860,15,len(dates)),

            "NO2":
            np.random.normal(42,3,len(dates)),

            "PM25":
            np.random.normal(25,5,len(dates)),

            "Temp":
            np.random.normal(33,2,len(dates)),

            "Humidity":
            np.random.normal(60,4,len(dates))

        })


        df = pd.concat(
            [
                history,
                new_data
            ],
            ignore_index=True
        )


    df = df.tail(10000)


    df.to_csv(
        DATA_FILE,
        index=False
    )


    return df.round(2)
