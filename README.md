# TimeTrack Analytics

Проект для анализа распределения времени на основе личных логов активности.

## Стек

- Python
- Pandas
- FastAPI
- Streamlit
- Google Sheets API


## Возможности

- загрузка данных из Google Sheets
- фильтрация по датам
- подсчет часов по категориям
- визуализация данных


## Запуск через Docker
1. Выполните команду в корне проекта: `docker-compose up --build`
2. Откройте в браузере: http://localhost:8501


###################################

## Запуск backend

uvicorn backend.main:app --reload

## Запуск frontend   

streamlit run frontend/app.py
