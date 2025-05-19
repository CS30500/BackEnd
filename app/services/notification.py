from firebase_admin import messaging
from datetime import datetime, timedelta
from pymongo.database import Database
from app.services.alert_conditions import (  # 네가 작성한 파일 기준
    should_alert_inactivity,
    should_alert_morning_target,
    should_alert_high_activity,
    should_alert_high_temp_morning,
    should_alert_urgent_rate,
    should_alert_water_status,
)

def run_hydration_alerts(user_id: str, db: Database, now: datetime = None) -> list[dict]:
    now = now or datetime.utcnow()
    alerts = []
    
    def send_alert(title: str, body: str) -> dict:
        # 30분 이내 동일한 알림 여부 확인
        recent = db.alert_logs.find_one({
            "user_id": user_id,
            "title": title,
            "sent_at": {"$gte": datetime.utcnow() - timedelta(minutes=30)}
        })

        if recent:
            return {"message": "최근에 전송된 알림 → 생략", "title": title}

        token_doc = db.fcm_tokens.find_one({"user_id": user_id})
        if not token_doc or "token" not in token_doc:
            return {"message": "FCM 토큰 없음", "title": title}

        try:
            message = messaging.Message(
                notification=messaging.Notification(title=title, body=body),
                token=token_doc["token"],
            )
            response = messaging.send(message)

            # ✅ 전송 후 로그 기록
            db.alert_logs.insert_one({
                "user_id": user_id,
                "title": title,
                "sent_at": datetime.utcnow()
            })

            return {"message": "알림 전송됨", "title": title, "fcm_response": response}
        except messaging.ApiCallError as e:
            if e.code in ("messaging/registration-token-not-registered", "messaging/invalid-registration-token"):
                db.fcm_tokens.delete_one({"user_id": user_id})
                return {"message": "무효 토큰 삭제됨", "title": title}
            raise

    # 조건별 검사 및 전송
    if should_alert_inactivity(user_id, db, now):
        alerts.append(send_alert("💧 오랜 시간 음수 없음", "최근 물을 마시지 않았어요. 한 잔 어때요?"))

    if should_alert_morning_target(user_id, db, now):
        target_doc = db.daily_targets.find_one({"user_id": user_id, "date": now.strftime("%Y-%m-%d")})
        target_ml = target_doc.get("target_ml", 2000) if target_doc else 2000
        alerts.append(send_alert("🌅 오늘의 음수 목표", f"오늘의 목표는 {int(target_ml)}mL입니다!"))

    if should_alert_high_activity(user_id, db, now):
        alerts.append(send_alert("🔥 활동량 증가", "운동량이 많았어요! 수분 보충을 잊지 마세요."))

    if should_alert_high_temp_morning(user_id, db, now):
        alerts.append(send_alert("☀️ 오늘 고온 예보", "기온이 높아요. 탈수를 예방하려면 물을 자주 마셔야 해요."))

    if should_alert_urgent_rate(user_id, db, now):
        alerts.append(send_alert("⚠️ 수분 섭취 속도 주의", "남은 시간 대비 너무 많은 물이 남았어요. 자주 나눠 마셔요."))

    if should_alert_water_status(user_id, db, now):
        alerts.append(send_alert("🥛 물 교체 필요", "물병 속 물이 오래되었어요. 새로운 물로 바꿔주세요!"))


    return alerts