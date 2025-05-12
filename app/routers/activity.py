# routers/activity.py
from fastapi import APIRouter, Depends
from datetime import datetime, timezone
from app.auth_utils import verify_token
from app.database import get_mongodb
from app.models.activity import ActivityLog

router = APIRouter(prefix="/activity", tags=["Activity"])

@router.post("/log")
def log_activity(
    activity: ActivityLog,
    user: dict = Depends(verify_token),
    db=Depends(get_mongodb)
) -> dict:
    data = activity.model_dump()
    data["user_id"] = user["user_id"]
    data["timestamp"] = datetime.now(timezone.utc)
    db.activity_logs.insert_one(data)
    return {"message": "운동 기록 저장 완료"}