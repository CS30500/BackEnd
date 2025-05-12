from fastapi import FastAPI
from app.routers.auth import router as auth_router
from app.routers.profile import router as profile_router
from app.routers.hydration import router as hydration_router
from app.routers.activity import router as activity_router
from app.routers.location import router as location_router
from app.routers.bottle import router as bottle_router

from app.database import get_mongodb
import uvicorn

app = FastAPI()
app.include_router(auth_router)
app.include_router(profile_router)
app.include_router(hydration_router)
app.include_router(activity_router)
app.include_router(location_router)
app.include_router(bottle_router)


@app.get("/")
def root():
    return {"message": "Hello World"}

def main():
    # MongoDB 연결 시도
    mongodb = get_mongodb()
    if mongodb.connect():
        # FastAPI 서버 실행
        uvicorn.run(app, host="0.0.0.0", port=8000)
    else:
        print("MongoDB 연결에 실패했습니다.")
        
    # 프로그램 종료 시 연결 종료
    mongodb.close()

if __name__ == "__main__":
    main()
