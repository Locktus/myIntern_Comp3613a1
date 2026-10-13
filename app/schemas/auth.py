from sqlmodel import SQLModel

class SigninRequest(SQLModel):
    username: str
    password: str

class SignupRequest(SQLModel):
    first_name: str
    last_name: str
    username: str
    email: str
    password: str