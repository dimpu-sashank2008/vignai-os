from pydantic import BaseModel, ConfigDict
from datetime import datetime

class LoginRequest(BaseModel):
    identifier: str | None = None
    email: str | None = None
    password: str

class StudentProfileResponse(BaseModel):
    id: int
    enrollment_number: str | None = None
    year_of_study: int | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class UserResponse(BaseModel):
    id: int
    email: str
    role: str
    is_active: bool
    roll_number: str | None = None
    faculty_id: str | None = None
    management_id: str | None = None
    must_change_password: bool = False
    created_at: datetime
    student_profile: StudentProfileResponse | None = None

    model_config = ConfigDict(from_attributes=True)

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str
    confirm_password: str

class ChangePasswordResponse(BaseModel):
    message: str
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

class ForgotPasswordRequest(BaseModel):
    identifier: str

class ForgotPasswordResponse(BaseModel):
    message: str
    identifier: str
    masked_email: str
    reset_token: str

class ResetPasswordRequest(BaseModel):
    identifier: str
    reset_token: str
    new_password: str
    confirm_password: str

class ResetPasswordResponse(BaseModel):
    message: str
    success: bool

