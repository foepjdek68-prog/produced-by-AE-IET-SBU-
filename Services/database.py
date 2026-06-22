import sqlite3
import pandas as pd
import os


DB_PATH = "Storage/GHG_Database.db"


def get_connection():

    os.makedirs("Storage", exist_ok=True)

    return sqlite3.connect(DB_PATH)



def load_data():

    conn = get_connection()

    try:

        df = pd.read_sql(
            "SELECT * FROM ghg_data",
            conn
        )

    except Exception:

        df = pd.DataFrame()


    conn.close()

    return df



def save_data(df):

    if df is None or df.empty:
        return


    conn = get_connection()

    try:

        df.to_sql(
            "ghg_data",
            conn,
            if_exists="replace",
            index=False
        )

        conn.commit()

    except Exception as e:

        print("DATABASE ERROR:", e)

    finally:

        conn.close()
