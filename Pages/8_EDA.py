import streamlit as st
import pandas as pd
import pymysql
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt

from src.db_settings import HOST, PORT, USER, PASSWORD, DB, SSL

st.set_page_config(page_title="EDA – Nutrition Data", layout="wide")

@st.cache_resource
def get_conn():
    return pymysql.connect(
        host=HOST, port=PORT, user=USER, password=PASSWORD, database=DB, ssl=SSL
    )

def query(sql):
    conn = get_conn()
    return pd.read_sql(sql, conn)

# Load data
df_ob = query("SELECT * FROM obesity")
df_ml = query("SELECT * FROM malnutrition")

st.title("🧮 Exploratory Data Analysis – Global Nutrition Dataset")

# ---- Dataset selector ----
dataset = st.selectbox("Select Dataset", ["Obesity", "Malnutrition"])
df = df_ob if dataset == "Obesity" else df_ml

# ---- Head ----
st.subheader("📦 First 50 Rows")
st.dataframe(df.head(50), use_container_width=True)

# ---- Shape ----
c1, c2, c3 = st.columns(3)
c1.metric("# Rows", len(df))
c2.metric("# Columns", len(df.columns))
c3.metric("Years Range", f"{df['Year'].min()} – {df['Year'].max()}")

# ---- Missing Value Check ----
st.subheader("🚨 Missing Values")
missing = df.isna().sum().reset_index()
missing.columns = ["Column", "Missing Count"]
missing["Missing %"] = round(missing["Missing Count"] / len(df) * 100, 2)
st.dataframe(missing, use_container_width=True)

# ---- Summary statistics ----
st.subheader("📊 Summary Statistics")
st.dataframe(df.describe(), use_container_width=True)

# ---- Distribution ----
st.subheader("🎯 Distribution – Mean Estimate")
fig = px.histogram(df, x="Mean_Estimate", nbins=40, title="Distribution of Mean Estimates")
st.plotly_chart(fig, use_container_width=True)

# ---- Variability by Region ----
st.subheader("📦 Box Plot – Variability by Region")
fig = px.box(df, x="Region", y="Mean_Estimate")
st.plotly_chart(fig, use_container_width=True)

# ---- Correlation Heatmap ----
st.subheader("🔥 Heatmap – Features Correlation")
numeric_df = df.select_dtypes(include=["float64", "int64"])
if not numeric_df.empty:
    fig, ax = plt.subplots()
    sns.heatmap(numeric_df.corr(), annot=True, cmap="coolwarm", ax=ax)
    st.pyplot(fig)
else:
    st.info("⚪ No numeric data available for heatmap")

# ---- Scatter plot ----
st.subheader("📌 Relationship – Mean Estimate vs CI Width")
if "CI_Width" in df.columns:
    fig = px.scatter(df, x="Mean_Estimate", y="CI_Width", color="Region")
    st.plotly_chart(fig, use_container_width=True)

# ---- Trends ----
st.subheader("📈 Trend Over Years")
trend = df.groupby("Year", as_index=False)["Mean_Estimate"].mean()
fig = px.line(trend, x="Year", y="Mean_Estimate", markers=True)
st.plotly_chart(fig, use_container_width=True)

# ---- Compare datasets ----
st.subheader("⚖️ Obesity vs Malnutrition – Country Comparison")
ml_country = query("SELECT Country, AVG(Mean_Estimate) AS v FROM malnutrition GROUP BY Country")
ob_country = query("SELECT Country, AVG(Mean_Estimate) AS v FROM obesity GROUP BY Country")

merged = pd.merge(ob_country, ml_country, on="Country", suffixes=("_obesity", "_malnutrition"))
fig = px.scatter(merged, x="v_obesity", y="v_malnutrition", hover_name="Country")
st.plotly_chart(fig, use_container_width=True)
