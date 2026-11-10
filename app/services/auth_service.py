from typing import Optional

from fastapi import HTTPException

from app.repositories.user import UserRepository
from app.schemas.user import RegularUserCreate
from app.utilities.security import create_access_token, encrypt_password, verify_password


class AuthService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    def authenticate_user(self, username: str, password: str) -> Optional[str]:
        user = self.user_repo.get_by_username(username)
        if not user or not verify_password(
            plaintext_password=password, encrypted_password=user.password
        ):
            return None
        return create_access_token(data={"sub": f"{user.id}", "role": user.role})

    def register_user(
        self,
        first_name: str,
        last_name: str,
        username: str,
        email: str,
        password: str,
    ):
        if (
            self.user_repo.get_by_username(username.strip()) is not None
            or self.user_repo.get_by_email(email) is not None
        ):
            raise HTTPException(status_code=409, detail="Username or email already exists")
        new_user = RegularUserCreate(
            first_name=first_name.strip(),
            last_name=last_name.strip(),
            username=username.strip(),
            email=email,
            password=encrypt_password(password),
        )
        return self.user_repo.create(new_user)
