import sqlite3
import pandas as pd

DB_PATH = "data/ghg_data.db"

def get_connection():
    return sqlite3.connect(DB_PATH)

def load_data():

    conn = get_connection()

    try:
        df = pd.read_sql(
            "SELECT * FROM ghg_data",
            conn
        )

    except Exception as e:
    print("Database Error:", e)
    df = pd.DataFrame()

    conn.close()

    return df


def save_data(df):

    conn = get_connection()

    df.to_sql(
        "ghg_data",
        conn,
        if_exists="replace",
        index=False
    )

    conn.close()
