import streamlit as st
from src.db_settings import HOST, PORT, USER, PASSWORD, DB, SSL
import pymysql
import pandas as pd
from src.load_to_tidb import load_data

st.set_page_config(page_title="Global Nutrition Dashboard", layout="wide")

@st.cache_resource
def init():
    return load_data()

# Button — reload API + refresh DB
if st.sidebar.button("🔄 Reload WHO Data (ETL)"):
    st.cache_resource.clear()
    load_data()
    st.success("WHO data reloaded – refresh page")

data = init()

st.title("🌍 Global Nutrition Dashboard")
st.write("Data Source: WHO Public API → cleaned → stored in TiDB Cloud")

# ---- KPI Cards ----
conn = pymysql.connect(host=HOST, port=PORT, user=USER, password=PASSWORD, database=DB, ssl=SSL)
ob = pd.read_sql("SELECT COUNT(*) AS c FROM obesity", conn).c.values[0]
ml = pd.read_sql("SELECT COUNT(*) AS c FROM malnutrition", conn).c.values[0]
years = pd.read_sql("SELECT DISTINCT Year FROM obesity ORDER BY Year", conn)["Year"]
conn.close()

c1, c2, c3 = st.columns(3)
c1.metric("📦 Rows – Obesity", ob)
c2.metric("🧬 Rows – Malnutrition", ml)
c3.metric("📅 Year Range", f"{years.min()} – {years.max()}")
