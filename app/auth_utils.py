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

def verify_token(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="토큰이 없습니다.")

    token = auth_header.split(" ")[1]
    SECRET_KEY = os.getenv("SECRET_KEY")
    ALGORITHM = os.getenv("ALGORITHM")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload  # 여기서 user_id를 포함한 dict가 반환됨
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="토큰이 만료되었습니다.")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="유효하지 않은 토큰입니다.")