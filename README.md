# TimeTrack Analytics

Проект для анализа распределения времени на основе личных логов активности.

## Стек

- Python
- FastAPI
- Streamlit
- Google Sheets API
- Pandas

## Возможности

- загрузка данных из Google Sheets
- фильтрация по датам
- подсчет часов по категориям
- визуализация данных

## Запуск backend

uvicorn backend.main:app --reload

## Запуск frontend

streamlit run frontend/app.py