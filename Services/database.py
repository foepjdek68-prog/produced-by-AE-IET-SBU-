import sqlite3
import pandas as pd
import os


DB_FOLDER = "Storage"
DB_PATH = os.path.join(
    DB_FOLDER,
    "GHG_Database.db"
)


# ==========================================
# CREATE DATABASE FOLDER
# ==========================================

def init_database():

    if not os.path.exists(DB_FOLDER):
        os.makedirs(DB_FOLDER)


    conn = sqlite3.connect(DB_PATH)


    conn.execute("""
    CREATE TABLE IF NOT EXISTS ghg_data
    (
        Date TEXT,
        CO2 REAL,
        CH4 REAL,
        NO2 REAL,
        PM25 REAL,
        Temp REAL,
        Humidity REAL
    )
    """)


    conn.commit()
    conn.close()



# ==========================================
# CONNECTION
# ==========================================

def get_connection():

    init_database()

    return sqlite3.connect(DB_PATH)



# ==========================================
# LOAD DATA
# ==========================================

def load_data():

    conn = get_connection()


    try:

        df = pd.read_sql(
            """
            SELECT *
            FROM ghg_data
            ORDER BY Date ASC
            """,
            conn
        )


    except Exception:

        df = pd.DataFrame()



    conn.close()


    return df



# ==========================================
# INSERT NEW SENSOR DATA
# ==========================================

def save_data(df):

    if df.empty:
        return


    conn = get_connection()


    df.to_sql(
        "ghg_data",
        conn,
        if_exists="append",
        index=False
    )


    # จำกัดข้อมูลไม่ให้โตเกินไป
    conn.execute("""
    DELETE FROM ghg_data
    WHERE rowid NOT IN
    (
        SELECT rowid
        FROM ghg_data
        ORDER BY Date DESC
        LIMIT 20000
    )
    """)


    conn.commit()
    conn.close()
