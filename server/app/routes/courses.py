import requests
from fastapi import APIRouter, HTTPException
from app.config import Config
from app.helpers.mongo import upsert_courses, get_courses

router = APIRouter(prefix="/courses", tags=["courses"])

def fetch_course_data():
    """Fetch JSON course data from NJIT endpoint."""
    resp = requests.get(Config.SOURCE_URL, timeout=30)
    if resp.status_code != 200:
        raise HTTPException(status_code=resp.status_code, detail="Failed to fetch data from NJIT")

    try:
        data = resp.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Invalid JSON response: {e}")

    if not isinstance(data, list):
        raise HTTPException(status_code=500, detail="Expected a list of courses")
    return data


@router.get("/sync")
def sync_courses():
    """Fetch and upsert NJIT course data into MongoDB."""
    try:
        records = fetch_course_data()
        upsert_courses(records)
        return {"status": "success", "records_synced": len(records)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/")
def list_courses(limit: int = 20):
    """Get stored courses from MongoDB."""
    return get_courses(limit)
