from fastapi import Request
from fastapi.responses import HTMLResponse

from app.dependencies.auth import AuthDep
from app.dependencies.session import SessionDep
from app.services.application import ApplicationService
from . import router, templates


@router.get("/my-applications", response_class=HTMLResponse)
async def my_applications(
    request: Request,
    user: AuthDep,
    db: SessionDep,
):
    applications = ApplicationService(db).list_for_student(user.id)
    return templates.TemplateResponse(
        request=request,
        name="my-applications.html",
        context={"user": user, "applications": applications},
    )
