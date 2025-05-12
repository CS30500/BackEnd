from app.auth_utils import create_token

def test_profile_registration(client, db):
    # 유저 수동 삽입
    user_id = "testuser_profile"
    db.users.insert_one({"user_id": user_id})
    token = create_token({"user_id": user_id})

    profile_data = {
        "sex": "F",
        "age": 30,
        "height": 165.0,
        "weight": 55.5
    }
    res = client.post("/profile", json=profile_data, headers={
        "Authorization": f"Bearer {token}"
    })

    assert res.status_code == 200
    assert res.json()["message"] == "프로필 등록 성공"

def test_profile_retrieval(client, db):
    user_id = "testuser_profile"
    db.users.insert_one({
        "user_id": user_id,
        "sex": "F",
        "age": 30,
        "height": 165.0,
        "weight": 55.5
    })
    token = create_token({"user_id": user_id})

    res = client.get("/profile", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    data = res.json()
    assert data["user_id"] == user_id
    assert data["sex"] == "F"
    assert data["age"] == 30
    assert data["height"] == 165.0
    assert data["weight"] == 55.5