from datetime import datetime

from pydantic import EmailStr
from sqlmodel import SQLModel


class RegisterRequest(SQLModel):
    first_name: str
    last_name: str
    username: str
    email: EmailStr
    password: str


class LoginRequest(SQLModel):
    username: str
    password: str


class TokenResponse(SQLModel):
    access_token: str
    token_type: str = "bearer"
    role: str


class MeResponse(SQLModel):
    id: int
    username: str
    email: EmailStr
    first_name: str
    last_name: str
    role: str


class CompanyResponse(SQLModel):
    id: int
    name: str
    offered_position: str
    position_description: str
    industry: str
    location: str
    available_positions: int
    description: str
    resume_instructions: str
    contact_email: str
    contact_phone: str
    address: str
    status: str


class ApplicationResponse(SQLModel):
    application_id: int
    application_reference: str
    student_id: int
    company_id: int
    admin_id: int | None
    status: str
    resume: str
    feedback: str | None
    submitted_at: datetime
    reviewed_at: datetime | None


class DecisionRequest(SQLModel):
    decision: str
    feedback: str = ""
