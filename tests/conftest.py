import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import get_mongodb
import uuid

@pytest.fixture(scope="session")
def client():
    """FastAPI 테스트 클라이언트"""
    return TestClient(app)

@pytest.fixture(scope="session")
def db():
    # 테스트용 데이터베이스 연결
    db = get_mongodb()
    if db.connect():
        yield db
        db.close()
    else:
        pytest.fail("테스트 데이터베이스 연결 실패")
# 중복 방지를 위해 고유한 유저 ID를 생성

@pytest.fixture(scope="session")
def make_unique_user():
    """중복 방지를 위해 고유한 유저 ID를 생성하는 함수 반환"""
    def _make_user():
        unique_id = str(uuid.uuid4())[:8]
        return {
            "user_id": f"testuser_{unique_id}",
            "password": "testpassword123",
            "password_check": "testpassword123"
        }
    return _make_user


# @pytest.fixture(autouse=True)
# def mock_weather_service():
#     """날씨 API 호출을 mock으로 대체"""
#     with patch('app.water_requirement.weather.WeatherService.get_current_temperature') as mock:
#         mock.return_value = 25.0  # 기본 기온 25도
#         yield mock

# @pytest.fixture(autouse=True)
# def mock_health_service():
#     """헬스 API 호출을 mock으로 대체"""
#     with patch('app.water_requirement.health.HealthService.get_today_activity') as mock:
#         mock.return_value = 500.0  # 기본 운동량 500kcal
#         yield mock 