from pydantic import BaseModel, EmailStr, Field
class CreateUser(BaseModel):
    username: str = Field(min_length=4, max_length=20)
    email: EmailStr
    password: str = Field(min_length=6)


class AuthUser(BaseModel):
    username: str = Field(min_length=4, max_length=20)
    password: str = Field(min_length=6)