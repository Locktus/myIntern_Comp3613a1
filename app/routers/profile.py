from fastapi import Request
from fastapi.responses import HTMLResponse

from app.dependencies.auth import AuthDep
from . import router, templates


@router.get("/profile", response_class=HTMLResponse)
async def profile_view(request: Request, user: AuthDep):
    return templates.TemplateResponse(
        request=request,
        name="profile.html",
        context={"user": user},
    )
