import streamlit as st
import pandas as pd

from utils import load_data


st.set_page_config(
    page_title="TimeTracker Analytics",
    layout="wide"
)

st.title("🏠 TimeTracker Analytics")
st.divider()

try:
    df = load_data()

    # -----------------------------------
    # ФИЛЬТР ПО ДАТЕ
    # -----------------------------------
    st.subheader("Период анализа")
    
    # проверить, что timestamp имеет тип datetime
    if not pd.api.types.is_datetime64_any_dtype(df["timestamp"]):
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        
    today = pd.Timestamp.now().date()
    
    # выбор предустановленного периода
    period_options = [
        "Текущий месяц", 
        "Прошлый месяц", 
        "Текущий год", 
        "Все время", 
        "Свой период"
    ]
    

    # 3 колонки
    col_preset, _ = st.columns([1, 2]) 

    with col_preset:
        selected_period = st.selectbox("Выберите период:", period_options, index=3)
    


    # вводим переменные для границ дат
    start_date = df["timestamp"].min().date()
    end_date = df["timestamp"].max().date()
    
    if selected_period == "Текущий месяц":
        start_date = today.replace(day=1)
        end_date = today
        
    elif selected_period == "Прошлый месяц":
        # вычислить последний день предыдущего месяца
        first_day_this_month = today.replace(day=1)
        last_day_last_month = first_day_this_month - pd.Timedelta(days=1)
        start_date = last_day_last_month.replace(day=1)
        end_date = last_day_last_month
        
    elif selected_period == "Текущий год":
        start_date = today.replace(month=1, day=1)
        end_date = today
        
    elif selected_period == "Свой период":
        # если выбран "Свой период", показать привычные инпуты для дат
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("С", value=df["timestamp"].min().date())
        with col2:
            end_date = st.date_input("По", value=df["timestamp"].max().date())
            
    # если выбран не "Свой период", показать, какие даты применились
    if selected_period != "Свой период":
        st.caption(f"Применен период: c **{start_date}** по **{end_date}**")

    # фильтр датафрейма
    filtered_df = df[
        (df["timestamp"].dt.date >= start_date) & 
        (df["timestamp"].dt.date <= end_date)
    ].copy()
    
    # одна строка записи в таблице = 15 минут = 1/4 часа
    filtered_df["hours"] = 0.25



    st.divider()

    
    # -----------------------------------
    # карточки
    # -----------------------------------

    total_hours = filtered_df["hours"].sum()

    active_days = (
        filtered_df["timestamp"]
        .dt.date
        .nunique()
    )

    avg_hours = (
        total_hours / active_days
        if active_days > 0 else 0
    )

    top_category = (
        filtered_df
        .groupby("category")["hours"]
        .sum()
        .idxmax()
        if len(filtered_df) > 0
        else "-"
    )

    st.subheader("Ключевые показатели")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Всего часов",
        f"{total_hours:,.1f}".replace(",", " ") # вывод с разделителем тысяч
    )

    c2.metric(
        "Активных дней",
        active_days
    )

    c3.metric(
        "Среднее в день",
        f"{avg_hours:.1f}"
    )

    c4.metric(
        "Топ категория",
        top_category
    )

    st.divider()




    # -----------------------------------
    # ЧАСЫ ПО КАТЕГОРИЯМ
    # -----------------------------------

    st.subheader("Часы по категориям")

    
        # горизонтальный график
#        hours_per_category = (
#        filtered_df
#        .groupby("category")["hours"]
#        .sum()
#        .sort_values(ascending=False)
#    )

#    st.bar_chart(hours_per_category)

#    st.divider()




    import altair as alt 
    hours_per_category = (
        filtered_df
        .groupby("category")["hours"]
        .sum()
        .reset_index() # для Altair - сбросить индекс, чтобы "category" стала колонкой
    )

    # горизонтальный график
    chart = (
        alt.Chart(hours_per_category)
        .mark_bar()
        .encode(
            x=alt.X("hours:Q", title="Часы"),
            y=alt.Y("category:N", sort="-x", title="Категории") # sort="-x" автоматически отсортирует от большего к меньшему
        )
        .properties(height=400) # настроить высоту под количество категорий
    )

    st.altair_chart(chart, use_container_width=True)




    st.divider()






    # -----------------------------------
    # ТОП КАТЕГОРИЙ / РАСПРЕДЕЛЕНИЕ ПРОДУКТИВНОСТИ
    # -----------------------------------

    # в 3 колонки: левая (30%), пустой зазор (10% ширины) и правая (50%)
    col_top, col_spacer, col_prod = st.columns([3, 1, 5])

    # Лелевая колонка: ТОП КАТЕГОРИЙ
    with col_top:
        st.subheader("Топ-5 категорий")

        top_categories = (
            filtered_df
            .groupby("category")["hours"]
            .sum()
            .sort_values(ascending=False)
            .head(5)
            .reset_index()
        )

        top_categories.columns = [
            "Категория",
            "Часы"
        ]


        top_categories["Часы"] = top_categories["Часы"].apply(
            lambda x: f"{int(x):,}".replace(",", " ")
        )


        st.dataframe(
            top_categories,
            use_container_width=True,
            hide_index=True
        )





    # Центральную колонку пустой

    # Правая колонка: РАСПРЕДЕЛЕНИЕ ПРОДУКТИВНОСТИ
    with col_prod:
        st.subheader("Распределение продуктивности")

        productivity_hours = (
            filtered_df
            .groupby("productivity")["hours"]
            .sum()
        )

        st.bar_chart(productivity_hours)





    st.divider()





    # -----------------------------------
    # ДИНАМИКА ПРОДУКТИВНЫХ ЧАСОВ
    # -----------------------------------

    st.subheader("Продуктивные часы по неделям")

    productive_df = filtered_df[
        filtered_df["productivity"] == "Продуктивная"].copy()

    if len(productive_df) > 0:

        productive_df["week"] = (
            productive_df["timestamp"]
            .dt.to_period("W")
            .astype(str)
        )

        weekly_productive = (
            productive_df
            .groupby("week")["hours"]
            .sum()
            .reset_index()
        )

        st.line_chart(
            weekly_productive.set_index("week")
        )

    else:
        st.info(
            "Нет продуктивных активностей за выбранный период."
        )

except Exception as e:
    st.error(
        f"Не удалось загрузить данные: {e}"
    )