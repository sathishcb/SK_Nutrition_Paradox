import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pymysql
from src.db_settings import HOST, PORT, USER, PASSWORD, DB, SSL

def create_tables():
    conn = pymysql.connect(
        host=HOST, port=PORT, user=USER, password=PASSWORD, database=DB, ssl=SSL
    )
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS obesity (
        Year INT,
        Gender VARCHAR(10),
        Mean_Estimate FLOAT,
        LowerBound FLOAT,
        UpperBound FLOAT,
        Age_Group VARCHAR(25),
        Country VARCHAR(120),
        Region VARCHAR(120),
        CI_Width FLOAT,
        Obesity_Level VARCHAR(25)
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS malnutrition (
        Year INT,
        Gender VARCHAR(10),
        Mean_Estimate FLOAT,
        LowerBound FLOAT,
        UpperBound FLOAT,
        Age_Group VARCHAR(25),
        Country VARCHAR(120),
        Region VARCHAR(120),
        CI_Width FLOAT,
        Malnutrition_Level VARCHAR(25)
    );
    """)

    conn.commit()
    conn.close()
    print("✔ TiDB tables created (or already exist)")

if __name__ == "__main__":
    create_tables()
