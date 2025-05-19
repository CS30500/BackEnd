from pymongo.database import Database
from datetime import datetime

def calculate_required_water(user_id: str, db: Database) -> float:
    # 1. 사용자 프로필
    user = db.users.find_one({"user_id": user_id})
    if not user:
        raise ValueError("프로필 정보가 없습니다.")

    weight = user.get("weight")
    sex = user.get("sex", "").upper()
    age = user.get("age")

    if not all([weight, sex, age]) or sex not in {"M", "F"}:
        raise ValueError("프로필 정보가 불완전하거나 잘못되었습니다.")

    # 2. 표 기반 권장량
    def base_table(age: int, sex: str) -> float:
        if age <= 0.5:
            return 0.7
        elif age <= 1:
            return 0.8
        elif age <= 3:
            return 1.3
        elif age <= 8:
            return 1.7
        elif age <= 13:
            return 2.4 if sex == "M" else 2.1
        elif age <= 18:
            return 3.3 if sex == "M" else 2.4
        else:
            return 3.7 if sex == "M" else 2.7

    table_liters = base_table(age, sex)
    weight_liters = weight * 0.033
    base_recommend = (table_liters + weight_liters) / 2

    # 3. location_temperatures에서 user_id 기준으로 최신 온도 검색
    temp_data = db.location_temperatures.find_one(
        {"user_id": user_id},
        sort=[("timestamp", -1)]
    )
    temp = float(temp_data["temperature"]) if temp_data else 20.0

    # 4. 온도 보정
    temp_bonus = 0
    if temp >= 20:
        temp_bonus = (temp - 20) / 20

    total_required = base_recommend + temp_bonus
    return round(total_required, 2)