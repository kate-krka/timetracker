from fastapi import APIRouter
from backend.sheets_client import fetch_data

router = APIRouter(
    prefix="/activities",
    tags=["activities"]
)

@router.get("/")
def get_activities():

    try:
        return fetch_data()

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }