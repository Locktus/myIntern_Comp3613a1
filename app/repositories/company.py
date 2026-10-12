from sqlmodel import Session, select

from app.models.internship import Company


class CompanyRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_companies(
        self,
        *,
        search: str | None = None,
        availability: str | None = None,
    ) -> list[Company]:
        query = select(Company).order_by(Company.name)
        if search:
            query = query.where(Company.name.ilike(f"%{search}%"))
        if availability:
            query = query.where(Company.status == availability)
        return list(self.db.exec(query).all())

    def get_by_id(self, company_id: int) -> Company | None:
        return self.db.get(Company, company_id)
