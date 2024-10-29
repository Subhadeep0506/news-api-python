from pydantic import BaseModel


class ChangePassword(BaseModel):
    email: str
    old_password: str
    new_password: str
