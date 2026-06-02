
import streamlit as st
from utils import load_data #вынести 

st.title("Исходные данные ")

df = load_data()

st.dataframe(df)