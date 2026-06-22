import sqlite3
import pandas as pd
import os


DB_FOLDER = "Storage"
DB_PATH = os.path.join(
    DB_FOLDER,
    "GHG_Database.db"
)


def get_connection():

    os.makedirs(
        DB_FOLDER,
        exist_ok=True
    )

    return sqlite3.connect(DB_PATH)



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



def save_data(df):

    if df.empty:
        return


    conn = get_connection()


    try:

        # ตรวจว่ามี table หรือไม่
        tables = pd.read_sql(
            """
            SELECT name 
            FROM sqlite_master 
            WHERE type='table'
            """,
            conn
        )


        if "ghg_data" not in tables["name"].values:

            df.to_sql(
                "ghg_data",
                conn,
                if_exists="replace",
                index=False
            )


        else:

            df.to_sql(
                "ghg_data",
                conn,
                if_exists="append",
                index=False
            )


        conn.commit()


    except Exception as e:

        print(
            "DATABASE ERROR:",
            e
        )


    finally:

        conn.close()
