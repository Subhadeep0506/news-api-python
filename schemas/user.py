from pydantic import BaseModel, EmailStr, Field, model_validator
from core.auth.roles import Role
from typing import Optional

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: Optional[Role] = Role.USER
    first_name: Optional[str] = ""
    last_name: Optional[str] = ""

class UserLogin(BaseModel):
    username: str = Field(default=None)
    email: str = Field(default=None)
    password: str

    @model_validator(mode="before")
    def check_username_or_email(cls, values):
        username, email = values.get("username"), values.get("email")
        if not username and not email:
            raise ValueError("Either username or email must be provided")
        return values

class UserUpdate(BaseModel):
    role: Optional[Role] = Role.USER
    first_name: Optional[str] = ""
    last_name: Optional[str] = ""
