import pytest
from datetime import datetime
from app.auth_utils import create_token
from app.database import get_test_mongodb

def test_log_activity(client, db):
    # ✅ 1. 클린업
    db.users.delete_many({})
    db.activity_logs.delete_many({})

    # ✅ 2. 유저 직접 삽입
    user_id = "testuser_activity"
    db.users.insert_one({
        "user_id": user_id,
        "password": "hashed_pw",  # password 검증 안 하니까 더미로 넣기
    })

    # ✅ 3. 토큰 직접 생성
    token = create_token({"user_id": user_id})

    # ✅ 4. POST 요청
    res = client.post(
        "/activity/log",
        json={"steps": 3500, "calories": 120.5},
        headers={"Authorization": f"Bearer {token}"}
    )

    # ✅ 5. 검증
    assert res.status_code == 200
    assert res.json()["message"] == "운동 기록 저장 완료"

    # ✅ 6. DB에 실제 기록됐는지 확인 (선택)
    saved = db.activity_logs.find_one({"user_id": user_id})
    assert saved is not None
    assert saved["steps"] == 3500