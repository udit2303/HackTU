from pydantic import BaseModel, EmailStr, field_validator


class UserCreate(BaseModel):
    email: str
    password: str

    @field_validator("password")
    def password_length(cls, v):
        if len(v.encode("utf-8")) > 72:
            raise ValueError("Password too long")
        return v


class UserOut(BaseModel):
    id: int
    email: EmailStr

    class Config:
        orm_mode = True
