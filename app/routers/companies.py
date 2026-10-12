from fastapi import Request
from fastapi.responses import HTMLResponse

from app.dependencies.auth import AuthDep
from app.dependencies.session import SessionDep
from app.services.company import CompanyService
from . import router, templates


@router.get("/companies", response_class=HTMLResponse)
async def companies_view(
    request: Request,
    user: AuthDep,
    db: SessionDep,
    search: str | None = None,
    availability: str | None = None,
):
    # STUDENT CHECKPOINT: create the service and call it with both filters.
    service = CompanyService(db)
    companies = service.list_companies(
        search=search,
        availability=availability,
    )
    return templates.TemplateResponse(
        request=request,
        name="companies.html",
        context={"user": user, "companies": companies},
    )


@router.get("/companies/{company_id}/apply", response_class=HTMLResponse)
async def application_form(
    request: Request,
    company_id: int,
    user: AuthDep,
    db: SessionDep,
):
    company, application = CompanyService(db).details_for_student(
        company_id, user.id
    )
    if company is None:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="Company not found")
    return templates.TemplateResponse(
        request=request,
        name="application-form.html",
        context={"user": user, "company": company, "application": application},
    )
