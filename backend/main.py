from fastapi import FastAPI
from .routers import activities
import logging


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


app = FastAPI(title="TimeTrack Analytics API")

# подключить роутеры
app.include_router(activities.router)

@app.get("/")
def root():
    return {"message": "Backend works"}