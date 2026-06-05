import streamlit as st
import pandas as pd
import altair as alt

from utils import load_data

# -----------------------------------


st.set_page_config(
    page_title="Продуктивность",
    layout="wide"
)

st.title("Продуктивность")



df = load_data()

if not pd.api.types.is_datetime64_any_dtype(df["timestamp"]):
    df["timestamp"] = pd.to_datetime(df["timestamp"])

df["hours"] = 0.25


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

df = df[
    (df["timestamp"].dt.date >= start_date)
    &
    (df["timestamp"].dt.date <= end_date)
].copy()



# -----------------------------------
# -----------------------------------

total_hours = df["hours"].sum()

productive_hours = (
    df[df["productivity"] == "Продуктивная"]
    ["hours"]
    .sum()
)

neutral_hours = (
    df[df["productivity"] == "Нейтральная"]
    ["hours"]
    .sum()
)

unproductive_hours = (
    df[df["productivity"] == "Непродуктивная"]
    ["hours"]
    .sum()
)

productivity_index = (
    productive_hours / total_hours * 100
    if total_hours > 0
    else 0
)

percent_productive = (
    productive_hours / total_hours * 100
    if total_hours > 0 else 0
)

percent_neutral = (
    neutral_hours / total_hours * 100
    if total_hours > 0 else 0
)

percent_unproductive = (
    unproductive_hours / total_hours * 100
    if total_hours > 0 else 0
)




# -----------------------------------
# KPI
# -----------------------------------

st.subheader("Ключевые показатели")

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.metric(
        "Продуктивные часы",
        f"{productive_hours:,.1f}".replace(",", " ")
    )
    st.caption(
        f"{percent_productive:.1f}% от общего времени"
    )

with c2:
    st.metric(
        "Нейтральные часы",
        f"{neutral_hours:,.1f}".replace(",", " ")
    )
    st.caption(
        f"{percent_neutral:.1f}% от общего времени"
    )

with c3:
    st.metric(
        "Непродуктивные часы",
        f"{unproductive_hours:,.1f}".replace(",", " ")
    )
    st.caption(
        f"{percent_unproductive:.1f}% от общего времени"
    )

with c4:
    st.metric(
        "Индекс продуктивности",
        f"{productivity_index:.1f}%"
    )

st.divider()

# -----------------------------------
# СТРУКТУРА ВРЕМЕНИ
# -----------------------------------

st.subheader("Структура времени")

pie_df = pd.DataFrame({
    "productivity": [
        "Продуктивная",
        "Нейтральная",
        "Непродуктивная"
    ],
    "hours": [
        productive_hours,
        neutral_hours,
        unproductive_hours
    ]
    
})

pie_chart = (
    alt.Chart(pie_df)
    .mark_arc()
    .encode(
        theta="hours:Q",
        color=alt.Color(
            "productivity:N",
            scale=alt.Scale(
                domain=[
                    "Продуктивная",
                    "Нейтральная",
                    "Непродуктивная"
                ],
                
                range=["#5a86cb","#f2dcdb","#f2aebc"]


            ),
            legend=alt.Legend(title="")
        ),
        tooltip=[
            "productivity",
            alt.Tooltip(
                "hours",
                title="Часы",
                format=".1f"
            )
        ]
    )
)

st.altair_chart(
    pie_chart,
    use_container_width=True
)

st.divider()

# -----------------------------------
# ДИНАМИКА ПРОДУКТИВНОСТИ
# -----------------------------------

st.subheader("Индекс продуктивности")

group_type = st.radio(
    "Группировка",
    ["Дни", "Недели", "Месяцы"],
    index=1,
    horizontal=True
)

trend_df = df.copy()


if group_type == "Дни":

    trend_df["period"] = (
        trend_df["timestamp"]
        .dt.strftime("%Y-%m-%d")
    )

elif group_type == "Недели":

    trend_df["period"] = (
        trend_df["timestamp"]
        .dt.to_period("W")
        .astype(str)
    )

else:

    trend_df["period"] = (
        trend_df["timestamp"]
        .dt.to_period("M")
        .astype(str)
    )

summary = (
    trend_df
    .groupby(
        ["period", "productivity"]
    )["hours"]
    .sum()
    .unstack(fill_value=0)
    .reset_index()
)

summary["index"] = (
    summary.get("Продуктивная", 0)
    /
    (
        summary.get("Продуктивная", 0)
        +
        summary.get("Нейтральная", 0)
        +
        summary.get("Непродуктивная", 0)
    )
    * 100
)

line_chart = (
    alt.Chart(summary)
    .mark_line(point=True)
    .encode(
        x=alt.X(
            "period:N",
            title="Период"
        ),
        y=alt.Y(
            "index:Q",
            title="%"
        ),
        tooltip=[
            "period",
            alt.Tooltip(
                "index",
                title="Индекс",
                format=".1f"
            )
        ]
    )
    .properties(height=400)
)

st.altair_chart(
    line_chart,
    use_container_width=True
)

st.divider()

# -----------------------------------
# ПО ДНЯМ НЕДЕЛИ
# -----------------------------------

st.subheader("Продуктивность по дням недели")

weekday_map = {
    0: "Понедельник",
    1: "Вторник",
    2: "Среда",
    3: "Четверг",
    4: "Пятница",
    5: "Суббота",
    6: "Воскресенье"
}

weekday_df = df.copy()

weekday_df["weekday"] = (
    weekday_df["timestamp"]
    .dt.dayofweek
)

weekday_df["weekday_name"] = (
    weekday_df["weekday"]
    .map(weekday_map)
)

weekday_summary = (
    weekday_df
    .groupby(
        ["weekday", "weekday_name", "productivity"]
    )["hours"]
    .sum()
    .unstack(fill_value=0)
    .reset_index()
)

weekday_summary["index"] = (
    weekday_summary.get("Продуктивная", 0)
    /
    (
        weekday_summary.get("Продуктивная", 0)
        +
        weekday_summary.get("Нейтральная", 0)
        +
        weekday_summary.get("Непродуктивная", 0)
    )
    * 100
)

weekday_chart = (
    alt.Chart(weekday_summary)
    .mark_bar()
    .encode(
        x=alt.X(
            "weekday_name:N",
            sort=list(weekday_map.values()),
            title=""
        ),
        y=alt.Y(
            "index:Q",
            title="%"
        ),
        tooltip=[
            "weekday_name",
            alt.Tooltip(
                "index",
                title="Индекс",
                format=".1f"
            )
        ]
    )
)

st.altair_chart(
    weekday_chart,
    use_container_width=True
)