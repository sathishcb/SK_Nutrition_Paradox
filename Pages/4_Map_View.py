import streamlit as st
import pandas as pd
import pymysql
import plotly.express as px
import pycountry

from src.db_settings import HOST, PORT, USER, PASSWORD, DB, SSL

def fetch(sql):
    conn = pymysql.connect(host=HOST, port=PORT,user=USER, password=PASSWORD,database=DB, ssl=SSL)
    df = pd.read_sql(sql, conn)
    conn.close()
    return df

def code3(country):
    try: return pycountry.countries.get(name=country).alpha_3
    except: return None

st.title("🗺 Global Choropleth — Obesity Levels")

df = fetch("""
SELECT Country, AVG(Mean_Estimate) AS avg_obesity
FROM obesity
GROUP BY Country
""")
df["iso3"] = df["Country"].apply(code3)
df = df.dropna(subset=["iso3"])

fig = px.choropleth(
    df, locations="iso3", color="avg_obesity",
    hover_name="Country", color_continuous_scale="Reds"
)
st.plotly_chart(fig, use_container_width=True)
