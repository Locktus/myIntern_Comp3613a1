from fastapi import Form, Request
from fastapi.responses import HTMLResponse

from app.dependencies.auth import AdminDep
from app.dependencies.session import SessionDep
from app.services.review import ReviewService
from . import router, templates


@router.get("/admin/applications", response_class=HTMLResponse)
async def admin_applications(
    request: Request,
    user: AdminDep,
    db: SessionDep,
):
    # STUDENT CHECKPOINT: keep admin review loading in the service layer.
    service = ReviewService(db)
    applications = service.list_applications()
    return templates.TemplateResponse(
        request=request,
        name="admin-applications.html",
        context={"user": user, "applications": applications},
    )


@router.post("/admin/applications/{application_id}/decision", response_class=HTMLResponse)
async def admin_decision(
    request: Request,
    application_id: int,
    user: AdminDep,
    db: SessionDep,
    decision: str = Form(...),
    feedback: str = Form(""),
):
    # STUDENT CHECKPOINT: delegate the decision to the review service.
    service = ReviewService(db)
    application = service.decide(
        application_id=application_id,
        admin_id=user.id,
        admin_name=user.username,
        admin_email=str(user.email),
        decision=decision,
        feedback=feedback,
    )
    return templates.TemplateResponse(
        request=request,
        name="admin-decision-confirmation.html",
        context={"user": user, "application": application},
    )
