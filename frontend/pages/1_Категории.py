import streamlit as st
from utils import load_data

st.title("📚 Категории")

df = load_data()

df["hours"] = 0.25

hours = (
    df.groupby("category")["hours"]
    .sum()
    .sort_values(ascending=False)
)

st.bar_chart(hours)

st.dataframe(hours)