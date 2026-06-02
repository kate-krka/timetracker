import streamlit as st
from utils import load_data

st.title("🗂 Сырые данные")

df = load_data()

st.dataframe(df)