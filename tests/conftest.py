import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import get_test_mongodb  # ✅ mongomock을 반환하는 함수
import uuid
from app.auth_utils import hash_password
        

@pytest.fixture
def make_user_in_db(db):
    def _create(user_id: str, password: str = "test1234"):
        db.users.insert_one({
            "user_id": user_id,
            "password": hash_password(password)
        })
        return {"user_id": user_id, "password": password}
    return _create

@pytest.fixture(scope="session")
def db():
    """mongomock 기반 DB 객체"""
    db = get_test_mongodb()
    yield db
    db.client.close()

@pytest.fixture(scope="session")
def client(db):
    from app.database import get_mongodb
    app.dependency_overrides[get_mongodb] = lambda: db
    return TestClient(app)

@pytest.fixture(scope="session")
def make_unique_user():
    def _make_user():
        unique_id = str(uuid.uuid4())[:8]
        return {
            "user_id": f"testuser_{unique_id}",
            "password": "testpassword123",
            "password_check": "testpassword123"
        }
    return _make_user
    
@pytest.fixture(autouse=True)
def clear_db(db):
    db.users.delete_many({})
    db.water_logs.delete_many({})
    db.daily_targets.delete_many({})
    db.bottle_temperatures.delete_many({})
    db.user_locations.delete_many({})
    db.location_temperatures.delete_many({})
