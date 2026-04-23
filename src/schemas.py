from pydantic import BaseModel, EmailStr, Field
from typing import Literal


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str = Field(min_length=4)
    role: Literal[
        "student",
        "trainer",
        "institution",
        "programme_manager",
        "monitoring_officer"
    ]
    institution_id: int | None = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str