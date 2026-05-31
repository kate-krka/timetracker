import streamlit as st
import requests
import pandas as pd

@st.cache_data(ttl=300)
def load_data():

    response = requests.get(
        "http://127.0.0.1:8000/activities/"
    )

    return response.json()


st.set_page_config(page_title="TimeTrack Analytics", layout="wide")
st.title("TimeTrack Analytics")

try:
    # 1️⃣ Получаем данные с backend
    data = load_data()
    df = pd.DataFrame(data)



    # 2️⃣ Переименуем колонки и преобразуем timestamp
    df = df.rename(columns={"Дата/Время": "timestamp", "Активность": "category"})
    df["timestamp"] = pd.to_datetime(df["timestamp"], format="%d.%m.%Y %H:%M:%S")

    # -------------------------------
    # 3️⃣ Фильтр по дате (новый код)
    start_date = st.date_input("С", value=df["timestamp"].min().date())
    end_date = st.date_input("По", value=df["timestamp"].max().date())
    filtered_df = df[(df["timestamp"].dt.date >= start_date) & (df["timestamp"].dt.date <= end_date)]
    # -------------------------------

    # добавляем часы
    filtered_df = filtered_df.copy()
    filtered_df["hours"] = 0.25

    # суммируем по категориям
    hours_per_category = filtered_df.groupby("category")["hours"].sum()

    st.subheader("Часы по категориям")
    st.bar_chart(hours_per_category)


    # 4️⃣ Отображаем таблицу
    st.subheader("Таблица активностей")
    st.dataframe(filtered_df)


except Exception as e:
    st.error(f"Не удалось подключиться к backend: {e}")