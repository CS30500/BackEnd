from fastapi import APIRouter, HTTPException, Depends
from pymongo.database import Database
from app.database import get_mongodb
from app.auth_utils import verify_token
from app.models.user import ProfileModel

router = APIRouter(prefix="/profile", tags=["Profile"])

@router.post("/")
def set_profile(
    profile: ProfileModel,
    user: dict = Depends(verify_token),
    db: Database = Depends(get_mongodb)
) -> dict:
    db.users.update_one(
        {"user_id": user["user_id"]},
        {"$set": profile.model_dump()}
    )
    return {"message": "프로필 등록 성공"}

@router.get("/")
def get_profile(
    user: dict = Depends(verify_token),
    db: Database = Depends(get_mongodb)
) -> dict:
    user_data = db.users.find_one(
        {"user_id": user["user_id"]},
        {"_id": 0, "user_id": 1, "sex": 1, "age": 1, "height": 1, "weight": 1}
    )
    if not user_data:
        raise HTTPException(status_code=404, detail="프로필이 존재하지 않습니다.")
    return user_data