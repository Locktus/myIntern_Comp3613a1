from datetime import datetime, timezone

from fastapi import HTTPException
from sqlmodel import Session

from app.models.internship import Admin
from app.repositories.review import ReviewRepository


class ReviewService:
    def __init__(self, db: Session):
        self.db = db
        self.repository = ReviewRepository(db)

    def list_applications(self):
        return self.repository.list_applications()

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

        if self.db.get(Admin, admin_id) is None:
            self.db.add(Admin(admin_id=admin_id, name=admin_name, email=admin_email))
            self.db.commit()

        application.status = decision
        application.admin_id = admin_id
        application.feedback = feedback.strip() or None
        application.reviewed_at = datetime.now(timezone.utc)
        return self.repository.save(application)
