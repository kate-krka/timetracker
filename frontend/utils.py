import requests
import pandas as pd
import streamlit as st


@st.cache_data(ttl=300)
def load_data():

    response = requests.get(
        "http://127.0.0.1:8000/activities/"
    )

    data = response.json()

    df = pd.DataFrame(data)

    df = df.rename(
        columns={
            "Дата/Время": "timestamp",
            "Активность": "category",
            "Продуктивность": "productivity"
        }
    )

    df["timestamp"] = pd.to_datetime(
        df["timestamp"],
        format="%d.%m.%Y %H:%M:%S"
    )

    return df