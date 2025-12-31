import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import streamlit as st
import pymysql
from src.db_settings import HOST, PORT, USER, PASSWORD, DB, SSL
from src.fetch_data import fetch_who_data
from src.clean_transform import clean_all

def table_is_empty(table_name):
    conn = pymysql.connect(host=HOST, port=PORT, user=USER, password=PASSWORD, database=DB, ssl=SSL)
    cur = conn.cursor()
    cur.execute(f"SELECT COUNT(*) FROM {table_name}")
    count = cur.fetchone()[0]
    conn.close()
    return count == 0

def insert_df(table_name, df):
    conn = pymysql.connect(host=HOST, port=PORT, user=USER, password=PASSWORD, database=DB, ssl=SSL)
    cur = conn.cursor()

    cols = ",".join(df.columns)
    placeholders = ",".join(["%s"] * len(df.columns))
    sql = f"INSERT INTO {table_name} ({cols}) VALUES ({placeholders})"

    rows = [tuple(x) for x in df.to_numpy()]
    cur.executemany(sql, rows)

    conn.commit()
    conn.close()
    print(f"✔ Inserted {len(df)} rows into {table_name}")


def load_data():
    print("📡 CHECKPOINT 1: Fetching WHO...")
    raw = fetch_who_data()
    print("📡 CHECKPOINT 2: Raw fetch complete")

    cleaned = clean_all(raw)
    print("📡 CHECKPOINT 3: Clean complete")

    if table_is_empty("obesity"):
        print("📡 CHECKPOINT 4: Inserting obesity")
        insert_df("obesity", cleaned["obesity"])

    if table_is_empty("malnutrition"):
        print("📡 CHECKPOINT 5: Inserting malnutrition")
        insert_df("malnutrition", cleaned["malnutrition"])

    print("🎉 DONE")
    return cleaned


if __name__ == "__main__":
    load_data()
