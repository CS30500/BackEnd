from pydantic import BaseModel, Field

class UserRegister(BaseModel):
    user_id: str
    password: str
    password_check: str

class UserLogin(BaseModel):
    user_id: str
    password: str

class ProfileModel(BaseModel):
    sex: str = Field(..., description="성별 (M/F)")
    age: int = Field(..., gt=0, description="나이")
    height: float = Field(..., gt=0, description="키 (cm)")
    weight: float = Field(..., gt=0, description="체중 (kg)")

class User(BaseModel):
    user_id: str = Field(..., description="아이디")
    password: str = Field(..., description="비밀번호")
    password_check: str = Field(..., description="비밀번호 확인")

    height: float = Field(..., description="키 (cm)")
    weight: float = Field(..., description="체중 (kg)")
    sex: str = Field(..., description="성별 (M/F)")
    age: int = Field(..., description="나이")
