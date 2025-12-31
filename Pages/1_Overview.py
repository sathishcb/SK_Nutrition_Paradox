import streamlit as st
import pymysql
import pandas as pd
from src.db_settings import HOST, PORT, USER, PASSWORD, DB, SSL

def get_df(tbl):
    conn = pymysql.connect(host=HOST, port=PORT, user=USER, password=PASSWORD, database=DB, ssl=SSL)
    df = pd.read_sql(f"SELECT * FROM {tbl}", conn)
    conn.close()
    return df

st.title("📊 Dataset Overview")

ob = get_df("obesity")
ml = get_df("malnutrition")

st.subheader(f"Obesity Dataset – {ob.shape[0]} rows")
st.dataframe(ob)

st.subheader(f"Malnutrition Dataset – {ml.shape[0]} rows")
st.dataframe(ml)
