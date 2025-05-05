from app.database import get_mongodb

db = get_mongodb()

def calculate_required_water(user_id: str) -> float:
    # 프로필 불러오기
    user = db.users.find_one({"user_id": user_id})
    if not user:
        raise ValueError("프로필 정보가 없습니다.")
    weight = user.get("weight")
    sex = user.get("sex")
    age = user.get("age")

    if not all([weight, sex, age]):
        raise ValueError("프로필 정보가 불완전합니다.")

    # 오늘 날씨 정보 가져오기
    today = db.user_locations.find_one({"user_id": user_id}, sort=[("timestamp", -1)])
    if not today:
        raise ValueError("위치 정보가 없습니다.")

    lat = today["latitude"]
    lon = today["longitude"]

    temp_data = db.location_temperatures.find_one(
        {"latitude": lat, "longitude": lon}, sort=[("timestamp", -1)]
    )
    temp = temp_data["temperature_c"] if temp_data else 20.0  # 기본값

    # 필요 음수량 계산 (기본 30ml/kg, 기온 높을수록 증가)
    base = 30 * weight
    if temp >= 30:
        base *= 1.2
    return round(base, 1)