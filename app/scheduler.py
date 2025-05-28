from apscheduler.schedulers.background import BackgroundScheduler
from app.database import get_mongodb
from app.services.notification import run_hydration_alerts

def alert_job():
    print("efefef")
    db = get_mongodb()
    users = db.users.find({}, {"user_id": 1})
    for user in users:
        try:
            run_hydration_alerts(user["user_id"], db)
        except Exception as e:
            print(f"[알림 실패] {user['user_id']} → {e}")

def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(alert_job, "interval", seconds=5)
    scheduler.start()
    print("🔁 스케줄러 시작됨")