import streamlit as st
import pandas as pd
import pymysql
import plotly.express as px
from src.db_settings import HOST, PORT, USER, PASSWORD, DB, SSL


def fetch(sql):
    conn = pymysql.connect(host=HOST, port=PORT,user=USER, password=PASSWORD,database=DB, ssl=SSL)
    df = pd.read_sql(sql, conn)
    conn.close()
    return df

st.title("🌍 Regional Analysis — Obesity & Malnutrition")

# Dropdown for Region Filter
regions = fetch("SELECT DISTINCT Region FROM obesity ORDER BY Region")
region_list = regions["Region"].dropna().tolist()
sel_region = st.selectbox("Select Region", region_list)

# Obesity
ob_df = fetch(f"""
SELECT Year, AVG(Mean_Estimate) AS avg_obesity
FROM obesity
WHERE Region = '{sel_region}'
GROUP BY Year
ORDER BY Year
""")

mal_df = fetch(f"""
SELECT Year, AVG(Mean_Estimate) AS avg_mal
FROM malnutrition
WHERE Region = '{sel_region}'
GROUP BY Year
ORDER BY Year
""")

col1, col2 = st.columns(2)
with col1:
    st.subheader(f"📈 Obesity Trend — {sel_region}")
    fig = px.line(ob_df, x="Year", y="avg_obesity")
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader(f"📉 Malnutrition Trend — {sel_region}")
    fig = px.line(mal_df, x="Year", y="avg_mal")
    st.plotly_chart(fig, use_container_width=True)
