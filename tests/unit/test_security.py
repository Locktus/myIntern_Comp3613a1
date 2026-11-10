import jwt
import pytest
from datetime import timedelta
from app.utilities.security import encrypt_password, verify_password, create_access_token
from app.config import get_settings


def test_ut_01_encrypt_password():
    """UT-01: Passwords are hashed."""
    value = encrypt_password("pass123")
    assert value and value != "pass123"


def test_ut_02_verify_password():
    """UT-02: Correct passwords verify."""
    assert verify_password("pass123", encrypt_password("pass123"))


def test_ut_03_reject_wrong_password():
    """UT-03: Wrong passwords fail."""
    assert not verify_password("wrong", encrypt_password("pass123"))


def test_ut_04_token_payload():
    """UT-04: Tokens contain payload and expiry."""
    token = create_access_token({"sub": "7", "role": "admin"})
    value = jwt.decode(token, get_settings().secret_key, algorithms=["HS256"])
    assert value["sub"] == "7" and value["role"] == "admin" and value["exp"]


def test_ut_05_token_expiry():
    """UT-05: Expired tokens are rejected."""
    token = create_access_token({"sub": "7"}, timedelta(minutes=-1))
    with pytest.raises(jwt.ExpiredSignatureError):
        jwt.decode(token, get_settings().secret_key, algorithms=["HS256"])
