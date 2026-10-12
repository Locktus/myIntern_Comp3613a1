from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi import status
from app.dependencies.session import SessionDep
from app.dependencies.auth import AdminDep, IsUserLoggedIn, get_current_user, is_admin
from . import router, templates
from app.services.dashboard import DashboardService


@router.get("/admin", response_class=HTMLResponse)
async def admin_home_view(
    request: Request,
    user: AdminDep,
    db:SessionDep
):
    summary = DashboardService(db).admin_summary()
    return templates.TemplateResponse(
        request=request, 
        name="admin.html",
        context={
            "user": user,
            **summary,
        }
    )
