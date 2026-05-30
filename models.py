from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    name: str = Field(min_length=1)
    email: EmailStr
    age: int | None = Field(default=None, ge=0)


class UserUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1)
    email: EmailStr | None = None
    age: int | None = Field(default=None, ge=0)


class User(BaseModel):
    id: int
    name: str
    email: EmailStr
    age: int | None
    created: datetime
