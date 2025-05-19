# routers/auth.py
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from app.database import get_mongodb
from app.models.user import UserRegister, UserLogin, FCMToken
from app.auth_utils import hash_password, verify_password, create_token, verify_token
from dotenv import load_dotenv
import os

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register")
def register(user: UserRegister, db=Depends(get_mongodb)):
    if user.password != user.password_check:
        raise HTTPException(status_code=400, detail="비밀번호와 비밀번호 확인이 다릅니다.")
    
    if db.users.find_one({"user_id": user.user_id}):
        raise HTTPException(status_code=400, detail="이미 존재하는 아이디입니다.")
    
    hashed_pw = hash_password(user.password)
    db.users.insert_one({
        "user_id": user.user_id,
        "password": hashed_pw
    })

    return {"message": "회원가입 성공"}

@router.post("/login")
def login(user: UserLogin, db=Depends(get_mongodb)):
    db_user = db.users.find_one({"user_id": user.user_id})
    if not db_user:
        raise HTTPException(status_code=404, detail="존재하지 않는 아이디입니다.")
    
    if not verify_password(user.password, db_user["password"]):
        raise HTTPException(status_code=401, detail="비밀번호가 일치하지 않습니다.")
    
    token = create_token({"user_id": user.user_id})
    return {"access_token": token}


@router.get("/verify")
def verify(user=Depends(verify_token)):
    return {
        "message": "토큰이 유효합니다.",
        "user_id": user["user_id"]
    }

from pydantic import BaseModel



@router.post("/fcm/register")
def register_fcm_token(
    fcm: FCMToken,
    user=Depends(verify_token),
    db=Depends(get_mongodb)
):
    db.fcm_tokens.update_one(
        {"user_id": user["user_id"]},
        {"$set": {"token": fcm.token, "updated_at": datetime.utcnow()}},
        upsert=True
    )
    return {"message": "FCM 토큰 등록 완료"}

