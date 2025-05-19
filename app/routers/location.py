from fastapi import APIRouter, Depends
from pymongo.database import Database
from app.auth_utils import verify_token
from app.database import get_mongodb
from app.models.location import UserLocation, LocationTemperature
from datetime import datetime
import httpx
import os
from dotenv import load_dotenv


load_dotenv()
WEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

router = APIRouter(prefix="/location", tags=["Location"])

@router.post("/")
async def log_location_and_weather(
    loc: UserLocation,
    user: dict = Depends(verify_token),
    db: Database = Depends(get_mongodb)
):
    # 1. 위치 저장
    loc_data = loc.model_dump()
    loc_data["user_id"] = user["user_id"]
    loc_data["timestamp"] = datetime.utcnow()
    db.user_locations.insert_one(loc_data)

    # 2. 날씨 API 호출
    async with httpx.AsyncClient() as client:
        res = await client.get(
            "https://api.openweathermap.org/data/2.5/weather",
            params={
                "lat": loc.latitude,
                "lon": loc.longitude,
                "appid": WEATHER_API_KEY,
                "units": "metric"
            }
        )
    weather = res.json()
    temp = weather.get("main", {}).get("temp")

    # 3. 온도 저장
    db.location_temperatures.insert_one({
        "user_id": user["user_id"],
        "latitude": loc.latitude,
        "longitude": loc.longitude,
        "temperature": temp,
        "timestamp": datetime.utcnow()
    })

    return {
        "message": "위치 및 날씨 저장 완료",
        "temperature": temp
    }


@router.post("/humidity")
async def get_external_humidity(
    loc: UserLocation,
    user: dict = Depends(verify_token),
    db: Database = Depends(get_mongodb)
):
    async with httpx.AsyncClient() as client:
        res = await client.get(
            "https://api.openweathermap.org/data/2.5/weather",
            params={
                "lat": loc.latitude,
                "lon": loc.longitude,
                "appid": WEATHER_API_KEY,
                "units": "metric"
            }
        )

    if res.status_code != 200:
        raise HTTPException(status_code=502, detail="날씨 API 호출 실패")

    weather = res.json()
    humidity = weather.get("main", {}).get("humidity")

    if humidity is None:
        raise HTTPException(status_code=500, detail="습도 정보 없음")

    return {
        "user_id": user["user_id"],
        "latitude": loc.latitude,
        "longitude": loc.longitude,
        "humidity": humidity,
        "timestamp": loc.timestamp
    }



@router.post("/temperature")
async def get_external_temperature(
    loc: UserLocation,
    user: dict = Depends(verify_token),
    db: Database = Depends(get_mongodb)
):
    async with httpx.AsyncClient() as client:
        res = await client.get(
            "https://api.openweathermap.org/data/2.5/weather",
            params={
                "lat": loc.latitude,
                "lon": loc.longitude,
                "appid": WEATHER_API_KEY,
                "units": "metric"
            }
        )

    if res.status_code != 200:
        raise HTTPException(status_code=502, detail="날씨 API 호출 실패")

    weather = res.json()
    temp = weather.get("main", {}).get("temp")

    if temp is None:
        raise HTTPException(status_code=500, detail="기온 정보 없음")

    return {
        "user_id": user["user_id"],
        "latitude": loc.latitude,
        "longitude": loc.longitude,
        "temperature": temp,
        "timestamp": loc.timestamp
    }