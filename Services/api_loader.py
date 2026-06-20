import pandas as pd
import numpy as np
from datetime import datetime
import pytz

def fetch_data():

    tz = pytz.timezone("Asia/Bangkok")

    now = datetime.now(tz)

    dates = pd.date_range(
        end=now,
        periods=365*24,
        freq="H"
    )

    df = pd.DataFrame({

        "Date": dates,

        "CO2": np.random.normal(430,8,len(dates)),

        "CH4": np.random.normal(1860,15,len(dates)),

        "NO2": np.random.normal(42,3,len(dates)),

        "PM25": np.random.normal(25,5,len(dates)),

        "Temp": np.random.normal(33,2,len(dates)),

        "Humidity": np.random.normal(60,4,len(dates))

    })

    return df.round(2)
