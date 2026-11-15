from datetime import datetime
from pydantic import BaseModel, ConfigDict, field_validator, EmailStr, Field

class UserCreate(BaseModel):
    name : str = Field(min_length=2, max_length=50)
    email : EmailStr = Field(min_length=3, max_length=254)
    password : str = Field(min_length=8, max_length=128)

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Display name cannot be blank")
        return value

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        return value.strip().lower()

class UserLogin(BaseModel):
    email : EmailStr = Field(max_length=254)
    password : str = Field(min_length=8, max_length=128)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        return value.strip().lower()

class PasswordChange(BaseModel):
    current_password : str = Field(min_length=1, max_length=128)
    new_password : str = Field(min_length=8, max_length=128)

class UserUpdate(BaseModel):
    name : str | None = Field(default=None, min_length=3, max_length=50)
    bio : str | None = Field(default=None, max_length=500)
    avatar_url : str | None = Field(default=None, max_length=500)
    cover_image_url : str | None = Field(default=None, max_length=500)

class UserResponse(BaseModel):
    id : int
    name : str
    email : str
    bio : str | None = None
    avatar_url : str | None = None
    cover_image_url : str | None = None
    is_admin : bool
    is_active :bool
    created_at : datetime

    model_config = ConfigDict(from_attributes=True)