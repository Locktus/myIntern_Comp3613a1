"""Database table models.

Import every table model here so ``SQLModel.metadata.create_all`` sees them.
"""

from app.models.user import User
from app.models.internship import Admin, Application, Company, Student

__all__ = ["User", "Company", "Student", "Admin", "Application"]
