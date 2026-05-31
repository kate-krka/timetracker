import streamlit as st
from utils import load_data

st.title("⚡ Продуктивность")

df = load_data()

df["hours"] = 0.25

productivity = (
    df.groupby("Продуктивность")["hours"]
    .sum()
)

st.bar_chart(productivity)