import streamlit as st
import pandas as pd
import altair as alt

from utils import load_data, CATEGORY_TO_PRODUCTIVITY


st.set_page_config(
    page_title="Категории",
    layout="wide"
)

st.title("Категории")

df = load_data()


if not pd.api.types.is_datetime64_any_dtype(df["timestamp"]):
    df["timestamp"] = pd.to_datetime(df["timestamp"])

df["hours"] = 0.25

# -----------------------------------
# ФИЛЬТРЫ
# -----------------------------------


st.subheader("Период анализа")

today = pd.Timestamp.now().date()

period_options = [
    "Текущий месяц",
    "Прошлый месяц",
    "Текущий год",
    "Все время",
    "Свой период"
]

col_period, _ = st.columns([1, 2])

with col_period:
    selected_period = st.selectbox(
        "Выберите период",
        period_options,
        index=3
    )

start_date = df["timestamp"].min().date()
end_date = df["timestamp"].max().date()

if selected_period == "Текущий месяц":

    start_date = today.replace(day=1)
    end_date = today

elif selected_period == "Прошлый месяц":

    first_day_this_month = today.replace(day=1)

    last_day_last_month = (
        first_day_this_month
        - pd.Timedelta(days=1)
    )

    start_date = last_day_last_month.replace(day=1)
    end_date = last_day_last_month

elif selected_period == "Текущий год":

    start_date = today.replace(
        month=1,
        day=1
    )

    end_date = today

elif selected_period == "Свой период":

    col1, col2 = st.columns(2)

    with col1:
        start_date = st.date_input(
            "С",
            value=df["timestamp"].min().date()
        )

    with col2:
        end_date = st.date_input(
            "По",
            value=df["timestamp"].max().date()
        )

if selected_period != "Свой период":

    st.caption(
        f"Период: {start_date} — {end_date}"
    )

# фильтр по дате

df = df[
    (df["timestamp"].dt.date >= start_date)
    &
    (df["timestamp"].dt.date <= end_date)
].copy()






###########

st.subheader("Фильтры")

col1, col2, col3 = st.columns(3)

with col1:

    categories = ["Все"] + sorted(df["category"].dropna().unique())

    default_category = "Учёба"
    default_index = categories.index(default_category) if default_category in categories else 0

    selected_category = st.selectbox(
        "Категория",
        categories,
        index=default_index
    )


if selected_category != "Все":
    auto_productivity = CATEGORY_TO_PRODUCTIVITY.get(selected_category, None)
else:
    auto_productivity = None

with col2:

    productivity_options = ["Все"] + sorted(df["productivity"].dropna().unique())

    # если есть соответствие — ставим его как default
    if auto_productivity in productivity_options:
        default_productivity_index = productivity_options.index(auto_productivity)
    else:
        default_productivity_index = 0

    selected_productivity = st.selectbox(
        "Продуктивность",
        productivity_options,
        index=default_productivity_index
    )



with col3:
    period_type = st.selectbox(
        "Группировка",
        ["Дни", "Недели", "Месяцы"],
        index=1
    )

filtered_df = df.copy()

if selected_category != "Все":
    filtered_df = filtered_df[
        filtered_df["category"] == selected_category
    ]

if selected_productivity != "Все":
    filtered_df = filtered_df[
        filtered_df["productivity"] == selected_productivity
    ]


if len(filtered_df) == 0:
    st.warning("Нет данных по выбранным фильтрам")
    st.stop()




st.divider()    

# -----------------------------------
# KPI
# -----------------------------------

st.subheader("Ключевые показатели")

total_hours = filtered_df["hours"].sum()

total_records = len(filtered_df)

active_days = (
    filtered_df["timestamp"]
    .dt.date
    .nunique()
)

avg_hours_per_day = (
    total_hours / active_days
    if active_days > 0
    else 0
)

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "Часы",
    f"{total_hours:,.1f}".replace(",", " ")
)

c2.metric(
    "Записей",
    f"{total_records:,}".replace(",", " ")
)

c3.metric(
    "Активных дней",
    active_days
)

c4.metric(
    "Среднее в день",
    f"{avg_hours_per_day:.1f}"
)

st.divider()

# -----------------------------------
# ДИНАМИКА
# -----------------------------------

st.subheader("Динамика")

trend_df = filtered_df.copy()

if period_type == "Недели":

    trend_df["period"] = (
        trend_df["timestamp"]
        .dt.to_period("W")
        .astype(str)
    )

elif period_type == "Дни":
     trend_df["period"] = (
        trend_df["timestamp"]
        .dt.strftime("%Y-%m-%d")
    )
     


else:

    trend_df["period"] = (
        trend_df["timestamp"]
        .dt.to_period("M")
        .astype(str)
    )

trend_df = (
    trend_df
    .groupby("period")["hours"]
    .sum()
    .reset_index()
)

trend_chart = (
    alt.Chart(trend_df)
    .mark_line(point=True)
    .encode(
        x=alt.X(
            "period:N",
            title="Период"
        ),
        y=alt.Y(
            "hours:Q",
            title="Часы"
        ),
        tooltip=[
            "period",
            alt.Tooltip(
                "hours",
                title="Часы",
                format=".1f"
            )
        ]
    )
    .properties(height=400)
)

st.altair_chart(
    trend_chart,
    use_container_width=True
)

st.divider()



# -----------------------------------
# ПО ДНЯМ НЕДЕЛИ
# -----------------------------------

st.subheader("По дням недели")

weekday_map = {
    0: "Понедельник",
    1: "Вторник",
    2: "Среда",
    3: "Четверг",
    4: "Пятница",
    5: "Суббота",
    6: "Воскресенье"
}

weekday_df = filtered_df.copy()

weekday_df["weekday"] = (
    weekday_df["timestamp"]
    .dt.dayofweek
)

weekday_df["weekday_name"] = (
    weekday_df["weekday"]
    .map(weekday_map)
)

weekday_df = (
    weekday_df
    .groupby(
        ["weekday", "weekday_name"]
    )["hours"]
    .sum()
    .reset_index()
    .sort_values("weekday")
)

weekday_chart = (
    alt.Chart(weekday_df)
    .mark_bar()
    .encode(
        x=alt.X(
            "hours:Q",
            title="Часы"
        ),
        y=alt.Y(
            "weekday_name:N",
            sort=list(weekday_map.values()),
            title=""
        ),
        tooltip=[
            "weekday_name",
            alt.Tooltip(
                "hours",
                title="Часы",
                format=".1f"
            )
        ]
    )
    .properties(height=300)
)

st.altair_chart(
    weekday_chart,
    use_container_width=True
)

st.divider()

# -----------------------------------
# ПО ЧАСАМ ДНЯ
# -----------------------------------

st.subheader("По времени суток")

hours_df = filtered_df.copy()

hours_df["hour"] = (
    hours_df["timestamp"]
    .dt.hour
)

hours_df = (
    hours_df
    .groupby("hour")["hours"]
    .sum()
    .reset_index()
)

hours_chart = (
    alt.Chart(hours_df)
    .mark_bar()
    .encode(
        x=alt.X(
            "hour:O",
            title="Час"
        ),
        y=alt.Y(
            "hours:Q",
            title="Часы"
        ),
        tooltip=[
            "hour",
            alt.Tooltip(
                "hours",
                title="Часы",
                format=".1f"
            )
        ]
    )
    .properties(height=300)
)

st.altair_chart(
    hours_chart,
    use_container_width=True
)