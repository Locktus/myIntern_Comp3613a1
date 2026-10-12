from sqlmodel import Session, func, select

from app.models.internship import Application, Company


class DashboardService:
    def __init__(self, db: Session):
        self.db = db

    def student_summary(self, student_id: int) -> dict:
        applications = list(
            self.db.exec(
                select(Application)
                .where(Application.student_id == student_id)
                .order_by(Application.submitted_at.desc())
                .limit(5)
            ).all()
        )
        return {
            "available_companies": self._count_companies("available"),
            "application_count": self._count_applications(student_id=student_id),
            "pending_count": self._count_applications(
                student_id=student_id,
                statuses=("pending", "under_review", "changes_requested"),
            ),
            "approved_count": self._count_applications(
                student_id=student_id,
                statuses=("approved",),
            ),
            "recent_applications": applications,
        }

    def admin_summary(self) -> dict:
        return {
            "application_count": self._count_applications(),
            "pending_count": self._count_applications(
                statuses=("pending", "under_review", "changes_requested"),
            ),
            "approved_count": self._count_applications(statuses=("approved",)),
            "rejected_count": self._count_applications(statuses=("rejected",)),
            "available_companies": self._count_companies("available"),
            "recent_applications": list(
                self.db.exec(
                    select(Application)
                    .order_by(Application.submitted_at.desc())
                    .limit(5)
                ).all()
            ),
        }

    def _count_companies(self, status: str) -> int:
        return int(
            self.db.exec(
                select(func.count()).select_from(Company).where(Company.status == status)
            ).one()
        )

    def _count_applications(
        self,
        *,
        student_id: int | None = None,
        statuses: tuple[str, ...] | None = None,
    ) -> int:
        query = select(func.count()).select_from(Application)
        if student_id is not None:
            query = query.where(Application.student_id == student_id)
        if statuses:
            query = query.where(Application.status.in_(statuses))
        return int(self.db.exec(query).one())
