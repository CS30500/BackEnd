import pytest
from datetime import datetime
from app.auth_utils import create_token

def test_set_daily_hydration_target(client, db):
    db.users.insert_one({"user_id": "user1"})
    token = create_token({"user_id": "user1"})

    res = client.post("/hydration/target", params={"target_ml": 1800}, headers={
        "Authorization": f"Bearer {token}"
    })
    assert res.status_code == 200
    assert res.json()["message"] == "목표 섭취량이 설정되었습니다."

def test_log_water_intake(client, db):
    db.users.insert_one({"user_id": "user1"})
    token = create_token({"user_id": "user1"})

    res = client.post("/hydration/log", params={"amount": 300}, headers={
        "Authorization": f"Bearer {token}"
    })
    assert res.status_code == 200
    assert res.json()["message"] == "음수량이 기록되었습니다."

def test_today_summary(client, db):
    user_id = "user1"
    db.users.insert_one({"user_id": user_id})
    token = create_token({"user_id": user_id})
    today = datetime.utcnow().strftime("%Y-%m-%d")

    # 테스트용 기록 삽입
    db.daily_targets.insert_one({
        "user_id": user_id,
        "date": today,
        "target_ml": 1500,
        "timestamp": datetime.utcnow()
    })
    db.water_logs.insert_many([
        {"user_id": user_id, "amount_ml": 500, "timestamp": datetime.utcnow()}
    ])

    res = client.get("/hydration/today", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    data = res.json()
    assert data["target_ml"] == 1500
    assert data["total_intake_ml"] == 500

def test_monthly_summary_with_query_params(client, db):
    user_id = "user2"
    db.users.insert_one({"user_id": user_id})
    token = create_token({"user_id": user_id})

    # 날짜 지정 → 예: 2024년 4월 15일
    test_date = datetime(2024, 4, 15)
    test_date_str = test_date.strftime("%Y-%m-%d")

    db.daily_targets.insert_one({
        "user_id": user_id,
        "date": test_date_str,
        "target_ml": 1800,
        "timestamp": test_date
    })
    db.water_logs.insert_one({
        "user_id": user_id,
        "amount_ml": 600,
        "timestamp": test_date
    })

    # ✅ year/month 명시적으로 지정
    res = client.get(
        "/hydration/monthly?year=2024&month=4",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert res.status_code == 200
    data = res.json()
    summary = next((d for d in data if d["date"] == test_date_str), None)
    assert summary is not None
    assert summary["target_ml"] == 1800
    assert summary["total_intake_ml"] == 600