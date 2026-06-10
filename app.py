import requests
import sqlite3
import pandas as pd
from datetime import datetime
import pytz
import time

# ===== DB SETUP =====
conn = sqlite3.connect("ghg_data.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS air_quality (
    time TEXT,
    station TEXT,
    aqi REAL,
    pm25 REAL
)
""")

conn.commit()

# ===== FETCH API (Air4Thai) =====
def fetch_data():

    url = "http://air4thai.pcd.go.th/services/getNewAQI_JSON.php"

    res = requests.get(url, timeout=10)
    data = res.json()

    return data["stations"]

# ===== SAVE TO DB =====
def save_to_db(stations):

    tz = pytz.timezone("Asia/Bangkok")
    now = datetime.now(tz).isoformat()

    for s in stations:

        try:
            station = s["nameTH"]
            aqi = float(s["AQI"]["aqi"])

            pm25 = None
            if "PM25" in s["AQI"]:
                pm25 = float(s["AQI"]["PM25"]["value"])

            cursor.execute("""
                INSERT INTO air_quality (time, station, aqi, pm25)
                VALUES (?, ?, ?, ?)
            """, (now, station, aqi, pm25))

        except:
            continue

    conn.commit()

# ===== LOOP (REAL-TIME COLLECTOR) =====
if __name__ == "__main__":

    while True:
        try:
            stations = fetch_data()
            save_to_db(stations)

            print("✔ saved at", datetime.now())

        except Exception as e:
            print("error:", e)

        time.sleep(300)  # ทุก 5 นาที
