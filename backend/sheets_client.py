import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import logging



# путь к JSON-файлу с ключом
SERVICE_ACCOUNT_FILE = "backend/timetracker-488519-2358658be50a.json"

# права для доступа
SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]

# авторизация
creds = Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE,
    scopes=SCOPES
)

client = gspread.authorize(creds)

# ID таблицы
SPREADSHEET_ID = "1_utFpsdXblQEHzgq2WPFjqxDgr3XT5iTgrJekwcytsc"

# название листа (Sheet)
SHEET_NAME = "Sheet1"







def fetch_data():

    logging.info("Loading data from Google Sheets")

    sheet = client.open_by_key(
        SPREADSHEET_ID
    ).worksheet(
        SHEET_NAME
    )

    data = sheet.get_all_records()

    logging.info(
        f"Loaded {len(data)} rows"
    )

    df = pd.DataFrame(data)

    return df.to_dict(orient="records")

