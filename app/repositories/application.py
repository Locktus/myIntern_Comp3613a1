from sqlmodel import Session, select

from app.models.internship import Application


class ApplicationRepository:
    def __init__(self, db: Session):
        self.db = db

    def active_for_student_company(
        self, student_id: int, company_id: int
    ) -> Application | None:
        query = select(Application).where(
            Application.student_id == student_id,
            Application.company_id == company_id,
            Application.status.in_(["pending", "under_review", "changes_requested", "approved"]),
        )
        return self.db.exec(query).first()

    def create(self, application: Application) -> Application:
        self.db.add(application)
        self.db.commit()
        self.db.refresh(application)
        return application

    def latest_for_student_company(
        self, student_id: int, company_id: int
    ) -> Application | None:
        query = (
            select(Application)
            .where(
                Application.student_id == student_id,
                Application.company_id == company_id,
            )
            .order_by(Application.submitted_at.desc())
        )
        return self.db.exec(query).first()

    def list_for_student(self, student_id: int) -> list[Application]:
        query = select(Application).where(
            Application.student_id == student_id
        ).order_by(Application.submitted_at.desc())
        return list(self.db.exec(query).all())

    def list_all(self) -> list[Application]:
        query = select(Application).order_by(Application.submitted_at.desc())
        return list(self.db.exec(query).all())
