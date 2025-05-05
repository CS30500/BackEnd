from fastapi import APIRouter, Depends
from app.auth_utils import verify_token
from app.database import get_mongodb
from app.models.activity import ActivityLog

from datetime import datetime

router = APIRouter()
db = get_mongodb()

@router.post("/")
def log_activity(activity: ActivityLog, user=Depends(verify_token)):
    data = activity.model_dump()
    data["user_id"] = user["user_id"]
    db.activity_logs.insert_one(data)
    return {"message": "운동 기록 저장 완료"}