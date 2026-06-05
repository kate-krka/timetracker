import streamlit as st
import pandas as pd
from utils import load_data, CATEGORY_TO_PRODUCTIVITY

st.title("Исходные данные")

df = load_data()

# на всякий случай приводим дату
df["timestamp"] = pd.to_datetime(df["timestamp"])

# сортировка: новые сверху
df = df.sort_values("timestamp", ascending=False)

# -----------------------------------
# ФИЛЬТРЫ
# -----------------------------------
col1, col2 = st.columns(2)

with col1:
    selected_category = st.selectbox(
        "Категория",
        ["Все"] + sorted(df["category"].dropna().unique())
    )

# дефолт продуктивности зависит от категории
if selected_category != "Все":
    default_productivity = CATEGORY_TO_PRODUCTIVITY.get(selected_category, "Все")
else:
    default_productivity = "Все"

with col2:
    productivity_options = ["Все"] + sorted(df["productivity"].dropna().unique())

    selected_productivity = st.selectbox(
        "Продуктивность",
        productivity_options,
        index=(
            productivity_options.index(default_productivity)
            if default_productivity in productivity_options
            else 0
        )
    )

# -----------------------------------
# ФИЛЬТР ДАННЫХ
# -----------------------------------
filtered_df = df.copy()

if selected_category != "Все":
    filtered_df = filtered_df[
        filtered_df["category"] == selected_category
    ]

if selected_productivity != "Все":
    filtered_df = filtered_df[
        filtered_df["productivity"] == selected_productivity
    ]


# -----------------------------------
# ТАБЛИЦА
# -----------------------------------
st.dataframe(
    filtered_df,
    use_container_width=True,
    hide_index=True
)