import pymysql
from src.db_settings import HOST, PORT, USER, PASSWORD, DB, SSL
from src.fetch_data import load_all_data
from src.clean_transform import clean_all

def get_conn(database=None):
    return pymysql.connect(
        host=HOST, port=PORT, user=USER, password=PASSWORD,
        database=database, ssl=SSL
    )

def database_exists():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SHOW DATABASES;")
    dbs = [row[0] for row in cur.fetchall()]
    conn.close()
    return DB in dbs

def create_database():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(f"CREATE DATABASE `{DB}`;")
    conn.commit()
    conn.close()
    print("📦 Database Created")

def tables_exist():
    conn = get_conn(DB)
    cur = conn.cursor()
    cur.execute("SHOW TABLES;")
    tables = [row[0] for row in cur.fetchall()]
    conn.close()
    return "obesity" in tables and "malnutrition" in tables

def create_tables():
    conn = get_conn(DB)
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS obesity (
        id INT AUTO_INCREMENT PRIMARY KEY,
        Year INT, Gender VARCHAR(20), Mean_Estimate FLOAT,
        LowerBound FLOAT, UpperBound FLOAT, Age_Group VARCHAR(30),
        Country VARCHAR(100), Region VARCHAR(100),
        CI_Width FLOAT, Obesity_Level VARCHAR(20)
    );""")
    cur.execute("""
    CREATE TABLE IF NOT EXISTS malnutrition (
        id INT AUTO_INCREMENT PRIMARY KEY,
        Year INT, Gender VARCHAR(20), Mean_Estimate FLOAT,
        LowerBound FLOAT, UpperBound FLOAT, Age_Group VARCHAR(30),
        Country VARCHAR(100), Region VARCHAR(100),
        CI_Width FLOAT, Malnutrition_Level VARCHAR(20)
    );""")
    conn.commit()
    conn.close()
    print("📌 Tables Created")

def table_has_data():
    conn = get_conn(DB)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM obesity;")
    a = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM malnutrition;")
    b = cur.fetchone()[0]
    conn.close()
    return a > 0 and b > 0

def insert_data(ob, mal):
    conn = get_conn(DB)
    cur = conn.cursor()
    for _, r in ob.iterrows():
        cur.execute("""
            INSERT INTO obesity(Year,Gender,Mean_Estimate,LowerBound,UpperBound,
                Age_Group,Country,Region,CI_Width,Obesity_Level)
            VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, tuple(r))
    for _, r in mal.iterrows():
        cur.execute("""
            INSERT INTO malnutrition(Year,Gender,Mean_Estimate,LowerBound,UpperBound,
                Age_Group,Country,Region,CI_Width,Malnutrition_Level)
            VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, tuple(r))
    conn.commit()
    conn.close()
    print("📥 Data Inserted")

def auto_bootstrap():
    print("🚦 Bootstrapping Database...")

    # 1️⃣ Create DB if missing
    if not database_exists():
        create_database()

    # 2️⃣ Create tables if missing
    if not tables_exist():
        conn = get_conn(DB)
        conn.close()
        create_tables()

    # 3️⃣ Insert Data if empty
    if not table_has_data():
        print("🌍 Fetching WHO API... (1-time only)")
        raw = load_all_data()
        cleaned = clean_all(raw)
        insert_data(cleaned["obesity"], cleaned["malnutrition"])
    else:
        print("⏩ Tables already filled – skipping fetch")
