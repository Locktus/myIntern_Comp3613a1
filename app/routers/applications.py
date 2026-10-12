from fastapi import File, Form, Request, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse

from app.dependencies.auth import AuthDep
from app.dependencies.session import SessionDep
from app.services.application import ApplicationService
from app.utilities.flash import flash
from . import router, templates


@router.post("/applications", response_class=HTMLResponse)
async def submit_application(
    request: Request,
    user: AuthDep,
    db: SessionDep,
    company_id: int = Form(...),
    resume: UploadFile = File(...),
):
    # STUDENT CHECKPOINT: create the service and delegate submission rules.
    service = ApplicationService(db)
    application, was_duplicate = await service.submit(
        student_id=user.id,
        student_name=user.username,
        student_email=str(user.email),
        company_id=company_id,
        resume=resume,
    )
    if was_duplicate:
        flash(
            request,
            "Your new submission was automatically rejected because you already "
            "had an application for this company.",
            "warning",
        )
        return RedirectResponse(
            url=f"/companies/{company_id}/apply",
            status_code=303,
        )
    return templates.TemplateResponse(
        request=request,
        name="application-confirmation.html",
        context={"user": user, "application": application},
    )
