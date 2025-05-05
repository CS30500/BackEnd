from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError
from dotenv import load_dotenv
import os
import sys

load_dotenv()

class MongoDB:
    def __init__(self, is_test=False):
        self.uri = os.getenv("MONGO_URI")
        self.db_name = os.getenv("MONGO_TESTDB") if is_test else os.getenv("MONGO_DB")
        self.client = MongoClient(self.uri)
        self.db = self.client[self.db_name]
        
    def connect(self):
        try:
            # 연결 테스트
            self.client.server_info()
            print(f"MongoDB 연결 성공! (DB: {self.db_name})")
            return self
        except ServerSelectionTimeoutError as e:
            print(f"MongoDB 연결 실패: {e}")
            raise e
            
    def close(self):
        self.client.close()
        print("MongoDB 연결 종료")

    @property
    def users(self):
        return self.db["users"]
    
    @property
    def daily_targets(self):
        return self.db["daily_targets"]
    
    @property
    def water_logs(self):
        return self.db["water_logs"]
        
    @property
    def bottle_temperatures(self):
        return self.db["bottle_temperatures"]

    @property
    def user_locations(self):
        return self.db["user_locations"]

    @property
    def location_temperatures(self):
        return self.db["location_temperatures"]

    @property
    def activity_logs(self):
        return self.db["activity_logs"]
        

def get_mongodb():
    is_test = "pytest" in sys.modules
    return MongoDB(is_test=is_test).connect()