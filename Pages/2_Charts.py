import streamlit as st
import pymysql
import pandas as pd
import plotly.express as px
from src.db_settings import HOST, PORT, USER, PASSWORD, DB, SSL

@st.cache_data
def fetch(table):
    conn = pymysql.connect(host=HOST, port=PORT, user=USER, password=PASSWORD, database=DB, ssl=SSL)
    df = pd.read_sql(f"SELECT * FROM {table}", conn)
    conn.close()
    return df

st.title("📈 EDA – Trends & Visual Analysis")

df_ob = fetch("obesity")
df_ml = fetch("malnutrition")

# Sidebar filters
# Sidebar filters
year = st.sidebar.selectbox("Year", sorted(df_ob["Year"].dropna().unique()))
region = st.sidebar.selectbox(
    "Region",
    sorted(df_ob["Region"].dropna().unique(), key=str)
)
country = st.sidebar.selectbox(
    "Country",
    sorted(df_ob["Country"].dropna().unique(), key=str)
)


# ------------------- Trend Line -------------------
st.subheader("📉 Obesity Trend – Selected Country")
df_c = df_ob[df_ob["Country"] == country].dropna(subset=["Country"])
fig = px.line(df_c, x="Year", y="Mean_Estimate", color="Gender")
st.plotly_chart(fig, use_container_width=True)

# ------------------- Compare Regions -------------------
st.subheader("🌍 Average Obesity by Region")
df_r = (
    df_ob[df_ob["Year"] == year]
    .dropna(subset=["Region"])
    .groupby("Region")["Mean_Estimate"]
    .mean()
    .reset_index()
)
fig2 = px.bar(df_r, x="Region", y="Mean_Estimate")
st.plotly_chart(fig2, use_container_width=True)

# ------------------- Box Plot -------------------
st.subheader("📦 Boxplot – CI Width by Region")
fig3 = px.box(df_ob.dropna(subset=["Region"]), x="Region", y="CI_Width")
st.plotly_chart(fig3, use_container_width=True)


# ------------------- Compare Obesity vs Malnutrition -------------------
st.subheader("⚖️ Obesity vs Malnutrition – Region Comparison")

ob = df_ob[df_ob["Year"] == year].groupby("Region")["Mean_Estimate"].mean().reset_index()
ml = df_ml[df_ml["Year"] == year].groupby("Region")["Mean_Estimate"].mean().reset_index()

merged = ob.merge(ml, on="Region", suffixes=("_obesity", "_malnutrition"))
fig4 = px.scatter(merged, x="Mean_Estimate_obesity", y="Mean_Estimate_malnutrition", hover_name="Region")
st.plotly_chart(fig4, use_container_width=True)

st.subheader("🔁 Compare Any 2 Countries")

c1, c2 = st.columns(2)
cA = c1.selectbox("Country A", sorted(df_ob["Country"].dropna().unique(), key=str))
cB = c2.selectbox("Country B", sorted(df_ob["Country"].dropna().unique(), key=str))

dfA = df_ob[df_ob["Country"] == cA]
dfB = df_ob[df_ob["Country"] == cB]

merged = pd.concat([dfA.assign(Source=cA), dfB.assign(Source=cB)])
fig5 = px.line(merged, x="Year", y="Mean_Estimate", color="Source")
st.plotly_chart(fig5, use_container_width=True)
