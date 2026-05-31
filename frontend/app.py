import streamlit as st
from utils import load_data

st.set_page_config(
    page_title="TimeTracker Analytics",
    layout="wide"
)

st.title("🏠 TimeTracker Analytics")

try:
    df = load_data()

    start_date = st.date_input(
        "С",
        value=df["timestamp"].min().date()
    )

    end_date = st.date_input(
        "По",
        value=df["timestamp"].max().date()
    )

    filtered_df = df[
        (df["timestamp"].dt.date >= start_date)
        & (df["timestamp"].dt.date <= end_date)
    ]

    filtered_df = filtered_df.copy()
    filtered_df["hours"] = 0.25

    hours_per_category = (
        filtered_df
        .groupby("category")["hours"]
        .sum()
    )

    st.subheader("Часы по категориям")
    st.bar_chart(hours_per_category)

    st.subheader("Таблица активностей")
    st.dataframe(filtered_df)

except Exception as e:
    st.error(f"Не удалось подключиться к backend: {e}")