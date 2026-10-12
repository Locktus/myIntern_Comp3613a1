from sqlmodel import Session, select

from app.models.internship import Application


class ReviewRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_applications(self) -> list[Application]:
        return list(
            self.db.exec(
                select(Application).order_by(Application.submitted_at.desc())
            ).all()
        )

    def get_application(self, application_id: int) -> Application | None:
        return self.db.get(Application, application_id)

    def save(self, application: Application) -> Application:
        self.db.add(application)
        self.db.commit()
        self.db.refresh(application)
        return application
