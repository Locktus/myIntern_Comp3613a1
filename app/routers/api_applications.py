from fastapi import File, Form, HTTPException, UploadFile, status

from app.dependencies.auth import AuthDep
from app.dependencies.session import SessionDep
from app.routers import api_router
from app.schemas import ApplicationResponse
from app.services.application import ApplicationService


@api_router.post(
    "/applications",
    response_model=ApplicationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit an application",
)
async def submit_application_api(
    user: AuthDep,
    db: SessionDep,
    company_id: int = Form(...),
    resume: UploadFile = File(...),
):
    if user.role == "admin":
        raise HTTPException(status_code=403, detail="Admins cannot submit applications.")
    application, duplicate = await ApplicationService(db).submit(
        student_id=user.id,
        student_name=f"{user.first_name} {user.last_name}".strip(),
        student_email=str(user.email),
        company_id=company_id,
        resume=resume,
    )
    if duplicate:
        raise HTTPException(
            status_code=409,
            detail="You already have an active application for this company.",
        )
    return application


@api_router.get(
    "/applications/me",
    response_model=list[ApplicationResponse],
    status_code=status.HTTP_200_OK,
    summary="List my applications",
)
async def my_applications_api(user: AuthDep, db: SessionDep):
    return ApplicationService(db).list_for_student(user.id)


@api_router.get(
    "/applications/{application_id}",
    response_model=ApplicationResponse,
    status_code=status.HTTP_200_OK,
    summary="Get an application",
)
async def application_api(application_id: int, user: AuthDep, db: SessionDep):
    return ApplicationService(db).get_for_user(application_id, user)
