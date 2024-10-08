from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional


class UserSignup(BaseModel):
    username: str
    email: EmailStr
    password: str
    phone: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None

    @field_validator("password")
    def password_length(cls, v: str):
        if len(v) < 8:
            raise ValueError(
                "Password must be at least 8 characters long and must be alphanumeric."
            )
        return v

    def model_dump(self):
        return {
            "email": self.email,
            "password": self.password,
            "options": {
                "data": {
                    "username": self.username,
                    "first_name": self.first_name,
                    "last_name": self.last_name,
                }
            },
        }


class UserLogin(BaseModel):
    email: EmailStr
    password: str
