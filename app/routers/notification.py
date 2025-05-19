import firebase_admin
from firebase_admin import credentials, messaging

# 1. 서비스 계정 키로 초기화
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)

# 2. 푸시 보낼 디바이스 토큰 (앱에서 수신한 FCM 등록 토큰)
device_token = "디바이스_FCM_등록_토큰"

# 3. 메시지 구성
message = messaging.Message(
    notification=messaging.Notification(
        title="물 마실 시간이에요!",
        body="1시간 넘게 물을 마시지 않았어요 💧",
    ),
    token=device_token,
)

# 4. 전송
response = messaging.send(message)
print("알림 전송 완료:", response)