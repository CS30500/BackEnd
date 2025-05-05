# routers/auth.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.database import get_mongodb
import jwt
from datetime import datetime
import os, sys 
from typing import Optional
from dotenv import load_dotenv
import bcrypt
from fastapi import Request, HTTPException, Depends
from app.models.user import UserRegister, UserLogin
load_dotenv()
db = get_mongodb()
router = APIRouter()



    
def create_token(data: dict, expire: Optional[int] = None):
    payload = data.copy()
    SECRET_KEY = os.getenv("SECRET_KEY")
    ALGORITHM = os.getenv("ALGORITHM")
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token

@router.post("/register")
def register(user: UserRegister):
    if user.password != user.password_check:
        raise HTTPException(status_code=400, detail="비밀번호와 비밀번호 확인이 다릅니다.")
    if db.users.find_one({"user_id": user.user_id}):
        raise HTTPException(status_code=400, detail="이미 존재하는 아이디입니다.")

    hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    db.users.insert_one({
        "user_id": user.user_id,
        "password": hashed_password
    })

    return {"message": "회원가입 성공"}

@router.post("/login")
def login(user: UserLogin):
    db_user = db.users.find_one({"user_id": user.user_id})
    if not db_user:
        raise HTTPException(status_code=404, detail="존재하지 않는 아이디입니다.")

    if not bcrypt.checkpw(user.password.encode('utf-8'), db_user["password"].encode('utf-8')):
        raise HTTPException(status_code=401, detail="비밀번호가 일치하지 않습니다.")

    token = create_token({"user_id": user.user_id})
    print(user.user_id, token)
    return {"access_token": token}