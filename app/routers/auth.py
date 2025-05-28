# routers/auth.py
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from app.database import get_mongodb
from app.models.user import UserRegister, UserLogin, FCMToken
from app.auth_utils import hash_password, verify_password, create_token, verify_token
from dotenv import load_dotenv
import os
import requests
import os
from google.oauth2 import service_account
import google.auth.transport.requests
import requests
import json

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


@router.post("/notify")
def notify_user(
    title: str,
    body: str,
    db=Depends(get_mongodb)
):
    token_entry = {
        "token": "eXDCVngmQ1ew9fkgI6HuX6:APA91bHx-2gIidMr28cApYbA9EUnFcFB1WJTa3Qs1eYnmB2TH69fxqd9LXJjCeUnboDusM3aiDxIAycHCkCsBZLjzgqlKWOmyw44_L_1BM2jQnOn8kmupdU"
    }

    if not token_entry or "token" not in token_entry:
        raise HTTPException(status_code=404, detail="FCM 토큰이 없음")

    print("🚀 보내는 FCM 토큰:", token_entry["token"])

    result = send_push_notification(token_entry["token"], title, body)
    return {"result": result}




import json
import requests
from google.oauth2 import service_account
import google.auth.transport.requests

def send_push_notification(token, title, body):
    SERVICE_ACCOUNT_FILE = "smartbottle-c732c-fd3f28f3cca2.json"
    PROJECT_ID = "smartbottle-c732c"

    SCOPES = ["https://www.googleapis.com/auth/firebase.messaging"]
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    credentials.refresh(google.auth.transport.requests.Request())
    access_token = credentials.token

    url = f"https://fcm.googleapis.com/v1/projects/{PROJECT_ID}/messages:send"
    print("📡 요청 URL:", url)

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json; UTF-8"
    }

    payload = {
        "message": {
            "token": token,
            "notification": {
                "title": title,
                "body": body
            }
        }
    }

    print("📦 전송 payload:", json.dumps(payload, indent=2))

    response = requests.post(url, headers=headers, data=json.dumps(payload))
    print("📨 응답 상태:", response.status_code)
    print("📨 응답 본문:", response.text)

    try:
        return response.json()
    except Exception:
        return {
            "error": "Invalid JSON",
            "status": response.status_code,
            "text": response.text
        }