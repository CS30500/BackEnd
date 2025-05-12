from pymongo.database import Database

def assess_water_risk(user_id: str, db: Database) -> str:
    latest = db.bottle_temperatures.find_one(
        {"user_id": user_id}, sort=[("timestamp", -1)]
    )
    if not latest:
        raise ValueError("물병 온도 정보가 없습니다.")

    temp = float(latest["temperature_c"])
    if temp >= 40:
        return "고위험"
    elif temp >= 30:
        return "주의"
    return "안전"