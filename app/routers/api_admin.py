from fastapi import status

from app.dependencies.auth import AdminDep
from app.dependencies.session import SessionDep
from app.routers import api_router
from app.schemas import ApplicationResponse, DecisionRequest
from app.services.application import ApplicationService
from app.services.review import ReviewService


@api_router.get(
    "/admin/applications",
    response_model=list[ApplicationResponse],
    status_code=status.HTTP_200_OK,
    summary="List all applications",
)
async def admin_applications_api(user: AdminDep, db: SessionDep):
    return ApplicationService(db).list_all()


@api_router.put(
    "/admin/applications/{application_id}/decision",
    response_model=ApplicationResponse,
    status_code=status.HTTP_200_OK,
    summary="Decide an application",
)
async def decide_application_api(
    application_id: int,
    payload: DecisionRequest,
    user: AdminDep,
    db: SessionDep,
):
    return ReviewService(db).decide(
        application_id=application_id,
        admin_id=user.id,
        admin_name=user.username,
        admin_email=str(user.email),
        decision=payload.decision,
        feedback=payload.feedback,
    )
