from fastapi import FastAPI
from app.routers import auth, profile, hydration, activity, location, bottle
from app.scheduler import start_scheduler
import uvicorn

app = FastAPI()
app.include_router(auth.router)
app.include_router(profile.router)
app.include_router(hydration.router)
app.include_router(activity.router)
app.include_router(location.router)
app.include_router(bottle.router)

@app.get("/")
def root():
    return {"message": "Hello World"}

def main():
    start_scheduler()  # ⬅️ 스케줄러 시작
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()