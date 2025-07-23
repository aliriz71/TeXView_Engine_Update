from pydantic import BaseModel, EmailStr, Field

class User(BaseModel):
    email: str
    password: str