from fastapi import APIRouter

from queries.recent_market_trends import get_last_sync_time
from backend.dashboard_state import dashboard_data

router = APIRouter(tags=["health"])


@router.get("/health")
def health_check():
    return {"status": "ok", "message": "API is running"}


@router.get("/last-sync")
def last_sync():
    result = {"last_sync": get_last_sync_time()}
    dashboard_data["pipeline"]["last_sync"] = result["last_sync"]
    return result
