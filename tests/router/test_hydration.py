import pytest
from datetime import datetime

def test_hydration_log_and_target_and_summary(client, make_unique_user):
    # 1. 유저 생성 및 회원가입
    TEST_USER = make_unique_user()
    register_res = client.post("/auth/register", json=TEST_USER)
    assert register_res.status_code == 200

    # 2. 로그인 후 토큰 발급
    login_data = {
        "user_id": TEST_USER["user_id"],
        "password": TEST_USER["password"]
    }
    login_res = client.post("/auth/login", json=login_data)
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 3. 음수 목표량 설정
    target_res = client.post("/hydration/target", params={"target_ml": 1800}, headers=headers)
    assert target_res.status_code == 200
    assert target_res.json()["message"] == "목표 섭취량이 설정되었습니다."

    # 4. 음수 기록 3회
    for amount in [250, 300, 200]:
        log_res = client.post("/hydration/log", params={"amount": amount}, headers=headers)
        assert log_res.status_code == 200
        assert log_res.json()["message"] == "음수량이 기록되었습니다."

    # 5. 오늘 요약 확인
    today_res = client.get("/hydration/today", headers=headers)
    assert today_res.status_code == 200
    today_data = today_res.json()
    assert today_data["target_ml"] == 1800
    assert today_data["total_intake_ml"] == 750  # 250 + 300 + 200

    # 6. 월간 요약 확인
    monthly_res = client.get("/hydration/monthly", headers=headers)
    assert monthly_res.status_code == 200
    monthly_data = monthly_res.json()
    today_str = datetime.utcnow().strftime("%Y-%m-%d")
    today_summary = next((d for d in monthly_data if d["date"] == today_str), None)
    assert today_summary is not None
    assert today_summary["total_intake_ml"] == 750
    assert today_summary["target_ml"] == 1800