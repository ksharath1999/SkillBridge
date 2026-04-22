from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: str
    institution_id: int | None = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str