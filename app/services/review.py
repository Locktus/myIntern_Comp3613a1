from datetime import datetime, timezone

from fastapi import HTTPException
from sqlmodel import Session, select

from app.models.internship import Admin
from app.models.internship import Company, Student
from app.repositories.review import ReviewRepository


class ReviewService:
    def __init__(self, db: Session):
        self.db = db
        self.repository = ReviewRepository(db)

    def list_applications(self):
        return self.repository.list_applications()

    def review_context(self):
        applications = self.list_applications()
        students = {
            student.id: student
            for student in self.db.exec(select(Student)).all()
        }
        companies = {
            company.id: company
            for company in self.db.exec(select(Company)).all()
        }
        return applications, students, companies

    def decide(
        self,
        *,
        application_id: int,
        admin_id: int,
        admin_name: str,
        admin_email: str,
        decision: str,
        feedback: str,
    ):
        application = self.repository.get_application(application_id)
        if application is None:
            raise HTTPException(status_code=404, detail="Application not found")
        if decision not in {"approved", "changes_requested", "rejected"}:
            raise HTTPException(status_code=400, detail="Invalid application decision")
        if decision in {"rejected", "changes_requested"} and not feedback.strip():
            raise HTTPException(
                status_code=400,
                detail="Feedback is required for rejected or changes-requested decisions.",
            )

        if self.db.get(Admin, admin_id) is None:
            self.db.add(Admin(admin_id=admin_id, name=admin_name, email=admin_email))
            self.db.commit()

        application.status = decision
        application.admin_id = admin_id
        application.feedback = feedback.strip() or None
        application.reviewed_at = datetime.now(timezone.utc)
        return self.repository.save(application)
