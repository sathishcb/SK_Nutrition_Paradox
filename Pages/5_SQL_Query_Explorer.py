import streamlit as st
import pandas as pd
import pymysql
from src.db_settings import HOST, PORT, USER, PASSWORD, DB, SSL

st.set_page_config(page_title="SQL Explorer", layout="wide")

@st.cache_resource
def get_conn():
    return pymysql.connect(
        host=HOST, port=PORT, user=USER, password=PASSWORD, database=DB, ssl=SSL
    )

def run_query(q):
    conn = get_conn()
    return pd.read_sql(q, conn)

# ---------------- QUERIES ----------------
QUERIES = {
    "Top 5 Regions – Highest Avg Obesity (2022)":
        "SELECT Region, ROUND(AVG(Mean_Estimate),2) AS value FROM obesity WHERE Year=2022 GROUP BY Region ORDER BY value DESC LIMIT 5",

    "Top 5 Countries – Highest Obesity":
        "SELECT Country, ROUND(AVG(Mean_Estimate),2) AS value FROM obesity GROUP BY Country ORDER BY value DESC LIMIT 5",

    "India – Obesity Trend":
        "SELECT Year, ROUND(AVG(Mean_Estimate),2) AS value FROM obesity WHERE Country='India' GROUP BY Year ORDER BY Year",

    "Average Obesity by Gender":
        "SELECT Gender, ROUND(AVG(Mean_Estimate),2) AS value FROM obesity GROUP BY Gender",

    "Country count by obesity level category":
        "SELECT Obesity_Level, COUNT(*) AS value FROM obesity GROUP BY Obesity_Level",

    "Top 5 – Highest CI_Width (Least Reliable)":
        "SELECT Country, ROUND(AVG(CI_Width),2) AS value FROM obesity GROUP BY Country ORDER BY value DESC LIMIT 5",

    "Average obesity by Age Group":
        "SELECT Age_Group, ROUND(AVG(Mean_Estimate),2) AS value FROM obesity GROUP BY Age_Group",

    "Avg. Malnutrition by Age Group":
        "SELECT Age_Group, ROUND(AVG(Mean_Estimate),2) AS value FROM malnutrition GROUP BY Age_Group",

    "Top 5 Countries – Highest Malnutrition":
        "SELECT Country, ROUND(AVG(Mean_Estimate),2) AS value FROM malnutrition GROUP BY Country ORDER BY value DESC LIMIT 5",

    "Malnutrition – African Region Trend":
        "SELECT Year, ROUND(AVG(Mean_Estimate),2) AS value FROM malnutrition WHERE Region='Africa' GROUP BY Year ORDER BY Year",

    "Average malnutrition by Gender":
        "SELECT Gender, ROUND(AVG(Mean_Estimate),2) AS value FROM malnutrition GROUP BY Gender",

    "Country – Obesity vs Malnutrition":
        "SELECT o.Country, ROUND(AVG(o.Mean_Estimate),2) AS obesity, ROUND(AVG(m.Mean_Estimate),2) AS malnutrition "
        "FROM obesity o JOIN malnutrition m ON o.Country=m.Country GROUP BY o.Country LIMIT 15",

    "Region – Avg obesity vs malnutrition":
        "SELECT o.Region, ROUND(AVG(o.Mean_Estimate),2) AS obesity, ROUND(AVG(m.Mean_Estimate),2) AS malnutrition "
        "FROM obesity o JOIN malnutrition m ON o.Region=m.Region GROUP BY o.Region"
}

# ---------------- UI ----------------
st.title("📊 SQL Explorer")

choice = st.selectbox("Select Query", list(QUERIES.keys()))

# 🟢 BUTTON HANDLER (everything must stay INSIDE!)
if st.button("Execute"):
    st.write("⚡ EXECUTED")

    df = run_query(QUERIES[choice])
    st.write("Column Types:", df.dtypes)  # debug print

    # FORCE CONVERT NUMERIC
    for c in df.columns:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    df = df.dropna(how="all")
    df = df.dropna(axis=1, how="all")

    st.subheader("Query Result")
    st.dataframe(df, use_container_width=True)

    # ---- Visualization ----
    st.subheader("📈 Visualization")

    # detect x-axis
    x_candidates = ["Year", "Country", "Region", "Gender", "Age_Group"]
    x = next((c for c in x_candidates if c in df.columns), df.columns[0])

    num_cols = df.select_dtypes(include=['float64', 'int64']).columns.tolist()
    if not num_cols:
        st.warning("⚠ No numeric column to chart")
        st.stop()

    y = num_cols[0]

    # restrict chart options
    if x == "Year":
        chart = st.selectbox("Chart Type", ["Line", "Area", "Scatter", "Bar"])
    else:
        chart = st.selectbox("Chart Type", ["Bar", "Scatter"])

    # sort
    try:
        df = df.sort_values(x)
    except:
        ...

    import plotly.express as px
    if chart == "Line":
        fig = px.line(df, x=x, y=y, markers=True)
    elif chart == "Area":
        fig = px.area(df, x=x, y=y)
    elif chart == "Scatter":
        fig = px.scatter(df, x=x, y=y)
    else:
        fig = px.bar(df, x=x, y=y)

    st.plotly_chart(fig, use_container_width=True)
