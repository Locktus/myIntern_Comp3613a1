from sqlmodel import Session

from app.repositories.company import CompanyRepository
from app.repositories.application import ApplicationRepository


class CompanyService:
    def __init__(self, db: Session):
        self.db = db

    def list_companies(
        self,
        *,
        search: str | None = None,
        availability: str | None = None,
        industry: str | None = None,
        location: str | None = None,
    ) -> list:
        if availability:
            normalized_availability = availability.strip().lower()
            if normalized_availability == "avaliable":
                normalized_availability = "available"
            if normalized_availability not in {"available", "full"}:
                raise ValueError("Availability must be 'available' or 'full'.")
            availability = normalized_availability
        return CompanyRepository(self.db).list_companies(
            search=search,
            availability=availability,
            industry=industry,
            location=location,
        )

    def details_for_student(self, company_id: int, student_id: int):
        company = CompanyRepository(self.db).get_by_id(company_id)
        application = (
            ApplicationRepository(self.db).latest_for_student_company(
                student_id, company_id
            )
            if company
            else None
        )
        return company, application

    def get_company(self, company_id: int):
        return CompanyRepository(self.db).get_by_id(company_id)

    def filter_options(self) -> tuple[list[str], list[str]]:
        return CompanyRepository(self.db).filter_options()
