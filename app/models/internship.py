from datetime import datetime, timezone
from typing import Optional

from sqlmodel import Field, SQLModel


class Company(SQLModel, table=True):
    """Participating company shown in the student browse workflow."""

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    offered_position: str
    description: str
    resume_instructions: str
    status: str = "available"


class Student(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    first_name: str
    last_name: str
    email: str


class Admin(SQLModel, table=True):
    admin_id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    email: str


class Application(SQLModel, table=True):
    """Student application submitted for a company position."""

    application_id: Optional[int] = Field(default=None, primary_key=True)
    # STUDENT CHECKPOINT: add the application fields and foreign keys.
    student_id: int = Field(foreign_key="student.id")
    company_id: int = Field(foreign_key="company.id")
    admin_id: Optional[int] = Field(default=None, foreign_key="admin.admin_id")
    status: str = "pending"
    resume: str
    application_reference: str = Field(unique=True, index=True)

    submitted_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    reviewed_at: Optional[datetime] = Field(default=None)
    feedback: Optional[str] = Field(default=None)