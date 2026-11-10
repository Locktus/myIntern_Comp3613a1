from fastapi import HTTPException, status

from app.dependencies.auth import AuthDep
from app.dependencies.session import SessionDep
from app.routers import api_router
from app.schemas import CompanyResponse
from app.services.company import CompanyService


@api_router.get(
    "/companies",
    response_model=list[CompanyResponse],
    status_code=status.HTTP_200_OK,
    summary="List companies",
)
async def companies_api(
    user: AuthDep,
    db: SessionDep,
    search: str | None = None,
    availability: str | None = None,
    industry: str | None = None,
    location: str | None = None,
):
    try:
        return CompanyService(db).list_companies(
            search=search,
            availability=availability,
            industry=industry,
            location=location,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@api_router.get(
    "/companies/{company_id}",
    response_model=CompanyResponse,
    status_code=status.HTTP_200_OK,
    summary="Get company details",
)
async def company_api(company_id: int, user: AuthDep, db: SessionDep):
    company = CompanyService(db).get_company(company_id)
    if company is None:
        raise HTTPException(status_code=404, detail="Company not found")
    return company
