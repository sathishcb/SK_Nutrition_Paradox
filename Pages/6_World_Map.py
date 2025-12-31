import streamlit as st
import pymysql
import pandas as pd
import plotly.express as px
from src.db_settings import HOST, PORT, USER, PASSWORD, DB, SSL

@st.cache_data
def fetch():
    conn = pymysql.connect(host=HOST, port=PORT, user=USER, password=PASSWORD, database=DB, ssl=SSL)
    df = pd.read_sql("SELECT Country, Year, Mean_Estimate FROM obesity", conn)
    conn.close()
    return df

st.title("🗺 Global Obesity Map")

df = fetch()
# Remove WHO-region labels (not valid ISO countries)
exclude = [
    "Africa","Europe","Americas Region","Eastern Mediterranean Region",
    "South-East Asia Region","Western Pacific Region","Global",
    "Low & Middle Income","Low Income","Upper Middle Income","High Income"
]
df = df[~df["Country"].isin(exclude)]

year = st.selectbox("Select Year", sorted(df["Year"].unique()))

d = df[df["Year"] == year]

fig = px.choropleth(
    d,
    locations="Country",
    locationmode="country names",
    color="Mean_Estimate",
    color_continuous_scale="Reds",
    title=f"World Obesity Map – {year}"
)
st.plotly_chart(fig, use_container_width=True)
