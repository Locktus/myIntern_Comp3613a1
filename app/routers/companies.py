from fastapi import HTTPException, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse

from app.dependencies.auth import AuthDep
from app.dependencies.session import SessionDep
from app.services.company import CompanyService
from app.utilities.flash import flash
from . import router, templates


@router.get("/companies", response_class=HTMLResponse)
async def companies_view(
    request: Request,
    user: AuthDep,
    db: SessionDep,
    search: str | None = None,
    availability: str | None = None,
    industry: str | None = None,
    location: str | None = None,
):
    # STUDENT CHECKPOINT: create the service and call it with both filters.
    service = CompanyService(db)
    companies = service.list_companies(
        search=search,
        availability=availability,
        industry=industry,
        location=location,
    )
    industries, locations = service.filter_options()
    return templates.TemplateResponse(
        request=request,
        name="companies.html",
        context={
            "user": user,
            "companies": companies,
            "industries": industries,
            "locations": locations,
        },
    )


@router.get("/companies/{company_id}/apply", response_class=HTMLResponse)
async def application_form(
    request: Request,
    company_id: int,
    user: AuthDep,
    db: SessionDep,
):
    if user.role == "admin":
        flash(
            request,
            "Admins can view company details but cannot submit applications.",
            "info",
        )
        return RedirectResponse(
            url=f"/companies/{company_id}",
            status_code=status.HTTP_303_SEE_OTHER,
        )
    company, application = CompanyService(db).details_for_student(
        company_id, user.id
    )
    if company is None:
        raise HTTPException(status_code=404, detail="Company not found")
    return templates.TemplateResponse(
        request=request,
        name="application-form.html",
        context={"user": user, "company": company, "application": application},
    )


@router.get("/companies/{company_id}", response_class=HTMLResponse)
async def company_details(
    request: Request,
    company_id: int,
    user: AuthDep,
    db: SessionDep,
):
    company = CompanyService(db).get_company(company_id)
    if company is None:
        raise HTTPException(status_code=404, detail="Company not found")
    return templates.TemplateResponse(
        request=request,
        name="company-details.html",
        context={"user": user, "company": company},
    )
