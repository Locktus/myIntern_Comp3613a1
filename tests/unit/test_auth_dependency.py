from types import SimpleNamespace
import pytest
from fastapi import HTTPException
from app.dependencies.auth import get_current_user, is_admin
from app.utilities.security import create_access_token


@pytest.mark.parametrize("token", [None, "garbage"])
async def test_ut_08_09_invalid_credentials(session, token):
    """UT-08/09: Missing and tampered credentials are rejected."""
    request = SimpleNamespace(cookies={} if token is None else {"access_token": token}, headers={})
    with pytest.raises(HTTPException) as error:
        await get_current_user(request, session)
    assert error.value.status_code == 401


async def test_ut_10_authorization_header(session, seeded):
    """UT-10: Authorization bearer tokens authenticate."""
    token = create_access_token({"sub": str(seeded[0]["bob"].id), "role": "regular_user"})
    request = SimpleNamespace(cookies={}, headers={"Authorization": f"Bearer {token}"})
    assert (await get_current_user(request, session)).username == "bob"


async def test_ut_11_cookie_token(session, seeded):
    """UT-11: Cookie tokens authenticate."""
    token = create_access_token({"sub": str(seeded[0]["bob"].id), "role": "regular_user"})
    request = SimpleNamespace(cookies={"access_token": token}, headers={})
    assert (await get_current_user(request, session)).username == "bob"


async def test_ut_12_is_admin():
    """UT-12: Admin role detection works."""
    assert await is_admin(SimpleNamespace(role="admin"))
    assert not await is_admin(SimpleNamespace(role="regular_user"))
