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

st.title("🧑‍🤝‍🧑 Gender Comparison — Obesity vs Malnutrition")

countries = fetch("SELECT DISTINCT Country FROM obesity ORDER BY Country")
country_list = countries["Country"].dropna().tolist()
sel_country = st.selectbox("Select Country", country_list)

df = fetch(f"""
SELECT o.Year, o.Gender, o.Mean_Estimate AS obesity, m.Mean_Estimate AS malnutrition
FROM obesity o
JOIN malnutrition m
ON o.Year = m.Year AND o.Country = m.Country AND o.Gender = m.Gender
WHERE o.Country = '{sel_country}'
ORDER BY Year
""")

st.subheader(f"📊 Gender Trends — {sel_country}")
fig = px.line(df, x="Year", y=["obesity", "malnutrition"], color="Gender")
st.plotly_chart(fig, use_container_width=True)
