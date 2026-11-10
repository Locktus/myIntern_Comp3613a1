import os
from pathlib import Path

os.environ["DATABASE_URI"] = "sqlite:///./.pytest_app.db"
os.environ["SECRET_KEY"] = "test-secret-key-for-pytest-0123456789"
os.environ["ENV"] = "ci"

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlalchemy.pool import StaticPool

from app.database import get_session
from app.main import app as fastapi_app
from app.models.internship import Company
from app.models.user import User
from app.repositories.user import UserRepository
from app.schemas.user import AdminCreate, RegularUserCreate
from app.utilities.security import create_access_token, encrypt_password


def pytest_collection_modifyitems(items):
    for item in items:
        if "tests\\unit\\" in str(item.fspath) or "/tests/unit/" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        if "tests\\integration\\" in str(item.fspath) or "/tests/integration/" in str(item.fspath):
            item.add_marker(pytest.mark.integration)


@pytest.fixture(scope="function")
def engine():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    import app.models
    SQLModel.metadata.create_all(engine)
    yield engine
    engine.dispose()


@pytest.fixture
def session(engine):
    with Session(engine) as value:
        yield value


@pytest.fixture
def client(engine):
    def override():
        with Session(engine) as value:
            yield value
    fastapi_app.dependency_overrides[get_session] = override
    value = TestClient(fastapi_app, follow_redirects=False)
    yield value
    fastapi_app.dependency_overrides.clear()


@pytest.fixture(autouse=True)
def upload_dir(tmp_path, monkeypatch):
    monkeypatch.setattr("app.services.application.UPLOAD_DIR", tmp_path / "uploads")


def _user(session, username, email, password, role="regular_user"):
    data_cls = AdminCreate if role == "admin" else RegularUserCreate
    return UserRepository(session).create(
        data_cls(
            first_name=username.title(),
            last_name="User",
            username=username,
            email=email,
            password=encrypt_password(password),
        )
    )


def seed_data(session):
    users = {
        "bob": _user(session, "bob", "bob@example.com", "bobpass"),
        "alice": _user(session, "alice", "alice@example.com", "alicepass"),
        "admin": _user(session, "admin", "admin@example.com", "adminpass", "admin"),
    }
    companies = [
        Company(
            name="ABC Technologies Ltd.",
            offered_position="Software Intern",
            position_description="Build software",
            industry="Technology",
            location="Kingston",
            available_positions=3,
            description="Technology company",
            resume_instructions="PDF preferred",
            contact_email="abc@example.com",
            status="available",
        ),
        Company(
            name="Caribbean Business Services",
            offered_position="Business Intern",
            position_description="Support operations",
            industry="Business Services",
            location="Bridgetown",
            available_positions=2,
            description="Business company",
            resume_instructions="PDF preferred",
            contact_email="cbs@example.com",
            status="available",
        ),
        Company(
            name="Island Finance Group",
            offered_position="Finance Intern",
            position_description="Analyse finance",
            industry="Finance",
            location="Kingston",
            available_positions=0,
            description="Finance company",
            resume_instructions="PDF preferred",
            contact_email="ifg@example.com",
            status="full",
        ),
    ]
    session.add_all(companies)
    session.commit()
    for company in companies:
        session.refresh(company)
    return users, companies


@pytest.fixture
def seeded(session):
    return seed_data(session)


def login_token(client, username, password):
    response = client.post("/api/auth/login", json={"username": username, "password": password})
    assert response.status_code == 200
    return response.json()["access_token"]


def auth(token):
    return {"Authorization": f"Bearer {token}"}


def pdf_upload(name="resume.pdf", content=b"%PDF-1.4 test"):
    return {"resume": (name, content, "application/pdf")}


@pytest.fixture
def student_headers(client, seeded):
    return auth(login_token(client, "bob", "bobpass"))


@pytest.fixture
def admin_headers(client, seeded):
    return auth(login_token(client, "admin", "adminpass"))


@pytest.fixture
def alice_headers(client, seeded):
    return auth(login_token(client, "alice", "alicepass"))
