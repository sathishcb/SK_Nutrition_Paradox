import streamlit as st
import pandas as pd
import pymysql
import plotly.express as px
from src.db_settings import HOST, PORT, USER, PASSWORD, DB, SSL

st.set_page_config(page_title="Insights Dashboard", layout="wide")

@st.cache_resource
def get_conn():
    return pymysql.connect(
        host=HOST, port=PORT, user=USER, password=PASSWORD, database=DB, ssl=SSL
    )

def query(sql):
    conn = get_conn()
    return pd.read_sql(sql, conn)

# ---------------- Load Data ----------------
df_ob = query("SELECT * FROM obesity")
df_ml = query("SELECT * FROM malnutrition")

# Determine year range
years = sorted(df_ob["Year"].dropna().unique())

# ---------------- Filters ----------------
st.title("✨ Global Nutrition – Insights Dashboard")
year = st.sidebar.selectbox("Select Year", years, index=len(years)-1)
region_filter = st.sidebar.multiselect("Region Filter", df_ob["Region"].unique())
age_filter = st.sidebar.multiselect("Age Group", df_ob["Age_Group"].unique())

def apply_filters(df):
    if region_filter:
        df = df[df["Region"].isin(region_filter)]
    if age_filter:
        df = df[df["Age_Group"].isin(age_filter)]
    return df

# ---------------- TABS ----------------
tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["📊 Overview", "📈 Trends", "🌍 Region Map", "🧬 Age Groups", "⚠ Alerts"]
)

# ---------------- TAB 1 – Overview ----------------
with tab1:
    st.header("📊 High-Level Overview")

    k1, k2, k3 = st.columns(3)
    k1.metric("Obesity Rows", len(df_ob))
    k2.metric("Malnutrition Rows", len(df_ml))
    k3.metric("Years", f"{years[0]} – {years[-1]}")

    st.subheader("Top 10 Countries – Highest Obesity (Latest Year)")
    top = query(f"""
        SELECT Country, AVG(Mean_Estimate) AS value
        FROM obesity
        WHERE Year = {year}
        GROUP BY Country
        ORDER BY value DESC LIMIT 10
    """)
    fig = px.bar(top, x="Country", y="value")
    st.plotly_chart(fig, use_container_width=True)

# ---------------- TAB 2 – Trends ----------------
with tab2:
    st.header("📈 Obesity & Malnutrition – Time Trends")

    india_ob = query("SELECT Year, AVG(Mean_Estimate) AS v FROM obesity WHERE Country='India' GROUP BY Year")
    world_ob = query("SELECT Year, AVG(Mean_Estimate) AS v FROM obesity GROUP BY Year")
    world_ml = query("SELECT Year, AVG(Mean_Estimate) AS v FROM malnutrition GROUP BY Year")

    c1, c2 = st.columns(2)

    with c1:
        st.subheader("India – Obesity Trend")
        st.plotly_chart(px.line(india_ob, x="Year", y="v", markers=True), use_container_width=True)

    with c2:
        st.subheader("Global Obesity Trend")
        st.plotly_chart(px.line(world_ob, x="Year", y="v", markers=True), use_container_width=True)

    st.subheader("Global Malnutrition Trend")
    st.plotly_chart(px.line(world_ml, x="Year", y="v", markers=True), use_container_width=True)

# ---------------- TAB 3 – Region Map ----------------
with tab3:
    st.header("🌍 Obesity Map – Latest Year")

    world = query(f"""
        SELECT Country, AVG(Mean_Estimate) AS value
        FROM obesity
        WHERE Year = {year}
        GROUP BY Country
    """)
    # iso-country conversion
    world["iso"] = world["Country"].str[:3]
    fig = px.choropleth(world, locations="iso", color="value", hover_name="Country")
    st.plotly_chart(fig, use_container_width=True)

# ---------------- TAB 4 – Age Groups ----------------
with tab4:
    st.header("🧬 Adult vs Child – Comparison")

    age_compare = query("""
        SELECT Age_Group, AVG(Mean_Estimate) AS value
        FROM obesity
        GROUP BY Age_Group
    """)
    fig = px.bar(age_compare, x="Age_Group", y="value", color="Age_Group")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Trend Over Years")
    age_trend = query("""
        SELECT Year, Age_Group, AVG(Mean_Estimate) AS value
        FROM obesity
        GROUP BY Year, Age_Group
        ORDER BY Year
    """)
    fig = px.line(age_trend, x="Year", y="value", color="Age_Group", markers=True)
    st.plotly_chart(fig, use_container_width=True)

# ---------------- TAB 5 – Alerts ----------------
with tab5:
    st.header("⚠ High-Risk Alerts – CI Width > 5")

    ci = query("""
        SELECT Country, AVG(CI_Width) AS ci
        FROM obesity
        GROUP BY Country
        HAVING AVG(CI_Width) > 5
        ORDER BY ci DESC
    """)
    st.dataframe(ci, use_container_width=True)

    st.subheader("Countries Where Malnutrition Increased Over Time")
    inc = query("""
        SELECT Country,
               MIN(Mean_Estimate) AS min_v,
               MAX(Mean_Estimate) AS max_v,
               MAX(Mean_Estimate) - MIN(Mean_Estimate) AS diff
        FROM malnutrition
        GROUP BY Country
        HAVING diff > 0
        ORDER BY diff DESC
        LIMIT 20
    """)
    st.dataframe(inc, use_container_width=True)
