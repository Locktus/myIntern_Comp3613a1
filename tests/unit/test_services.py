from io import BytesIO
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException
from starlette.datastructures import UploadFile

from app.models.internship import Application, Student
from app.repositories.application import ApplicationRepository
from app.repositories.company import CompanyRepository
from app.repositories.user import UserRepository
from app.services.application import ApplicationService
from app.services.auth_service import AuthService
from app.services.company import CompanyService
from app.services.dashboard import DashboardService
from app.services.review import ReviewService
from app.utilities.security import encrypt_password, verify_password
from tests.factories import application_for


def test_ut_13_authenticate_valid(seeded):
    repo = MagicMock()
    user = seeded[0]["bob"]
    repo.get_by_username.return_value = user
    user.password = encrypt_password("bobpass")
    token = AuthService(repo).authenticate_user("bob", "bobpass")
    assert token


def test_ut_14_authenticate_wrong_password(seeded):
    repo = MagicMock()
    user = seeded[0]["bob"]
    user.password = encrypt_password("bobpass")
    repo.get_by_username.return_value = user
    assert AuthService(repo).authenticate_user("bob", "wrong") is None


def test_ut_15_authenticate_unknown():
    repo = MagicMock()
    repo.get_by_username.return_value = None
    assert AuthService(repo).authenticate_user("none", "wrong") is None


def test_ut_16_register_user():
    repo = MagicMock()
    repo.get_by_username.return_value = None
    repo.get_by_email.return_value = None
    repo.create.side_effect = lambda value: value
    user = AuthService(repo).register_user(" Bob ", " User ", "bob", "bob@example.com", "pass")
    assert user.first_name == "Bob" and user.last_name == "User"
    assert verify_password("pass", user.password)


def test_ut_17_register_duplicate():
    repo = MagicMock()
    repo.get_by_username.return_value = SimpleNamespace()
    with pytest.raises(HTTPException) as error:
        AuthService(repo).register_user("A", "B", "a", "a@example.com", "pass")
    assert error.value.status_code == 409


def test_ut_18_list_companies(seeded, session):
    assert [c.name for c in CompanyService(session).list_companies()] == [
        "ABC Technologies Ltd.", "Caribbean Business Services", "Island Finance Group"
    ]


def test_ut_19_normalise_availability(seeded, session):
    service = CompanyService(session)
    assert len(service.list_companies(availability="Available")) == 2
    assert len(service.list_companies(availability=" FULL ")) == 1


def test_ut_20_avaliable_typo(seeded, session):
    assert len(CompanyService(session).list_companies(availability="avaliable")) == 2


def test_ut_21_invalid_availability(seeded, session):
    with pytest.raises(ValueError):
        CompanyService(session).list_companies(availability="maybe")


def test_ut_22_search(seeded, session):
    assert [c.name for c in CompanyService(session).list_companies(search="abc")] == [
        "ABC Technologies Ltd."
    ]


def test_ut_23_filter_options(seeded, session):
    industries, locations = CompanyService(session).filter_options()
    assert industries == ["Business Services", "Finance", "Technology"]
    assert locations == ["Bridgetown", "Kingston"]


def test_ut_24_unknown_company(seeded, session):
    assert CompanyService(session).get_company(999) is None


async def test_ut_25_submit_unknown_company(seeded, session):
    upload = UploadFile(filename="resume.pdf", file=BytesIO(b"pdf"))
    with pytest.raises(HTTPException) as error:
        await ApplicationService(session).submit(
            student_id=seeded[0]["bob"].id, student_name="Bob User",
            student_email="bob@example.com", company_id=999, resume=upload
        )
    assert error.value.status_code == 404


async def test_ut_26_submit_happy_path(seeded, session):
    upload = UploadFile(filename="resume.pdf", file=BytesIO(b"pdf"))
    application, duplicate = await ApplicationService(session).submit(
        student_id=seeded[0]["bob"].id, student_name="Bob User",
        student_email="bob@example.com", company_id=seeded[1][0].id, resume=upload
    )
    assert application.status == "pending" and not duplicate and application.application_reference.startswith("APP-")


async def test_ut_27_submit_full_company(seeded, session):
    upload = UploadFile(filename="resume.pdf", file=BytesIO(b"pdf"))
    application, _ = await ApplicationService(session).submit(
        student_id=seeded[0]["bob"].id, student_name="Bob User",
        student_email="bob@example.com", company_id=seeded[1][2].id, resume=upload
    )
    assert application.status == "rejected"


async def test_ut_28_duplicate_application(seeded, session):
    existing = application_for(seeded[0]["bob"], seeded[1][0])
    session.add(existing)
    session.commit()
    upload = UploadFile(filename="resume.pdf", file=BytesIO(b"pdf"))
    result, duplicate = await ApplicationService(session).submit(
        student_id=seeded[0]["bob"].id, student_name="Bob User",
        student_email="bob@example.com", company_id=seeded[1][0].id, resume=upload
    )
    assert duplicate and result.status == "pending"


async def test_ut_29_submit_after_rejected(seeded, session):
    session.add(application_for(seeded[0]["bob"], seeded[1][0], "rejected"))
    session.commit()
    result, duplicate = await ApplicationService(session).submit(
        student_id=seeded[0]["bob"].id, student_name="Bob User",
        student_email="bob@example.com", company_id=seeded[1][0].id,
        resume=UploadFile(filename="resume.pdf", file=BytesIO(b"pdf"))
    )
    assert result.status == "pending" and not duplicate


@pytest.mark.parametrize("filename", ["resume.exe", "resume.pdf"])
async def test_ut_30_31_invalid_resume(seeded, session, filename):
    """UT-30/31: Invalid resume types and sizes are rejected."""
    content = b"x" if filename.endswith(".exe") else b"x" * (5 * 1024 * 1024 + 1)
    with pytest.raises(HTTPException) as error:
        await ApplicationService(session).submit(
            student_id=seeded[0]["bob"].id, student_name="Bob User",
            student_email="bob@example.com", company_id=seeded[1][0].id,
            resume=UploadFile(filename=filename, file=BytesIO(content))
        )
    assert error.value.status_code == 400


async def test_ut_32_creates_student(seeded, session):
    user = seeded[0]["bob"]
    result, _ = await ApplicationService(session).submit(
        student_id=user.id, student_name="Bob User", student_email="bob@example.com",
        company_id=seeded[1][0].id, resume=UploadFile(filename="resume.pdf", file=BytesIO(b"x"))
    )
    assert session.get(Student, user.id) is not None and result.student_id == user.id


def test_ut_33_review_approved(seeded, session):
    app = application_for(seeded[0]["bob"], seeded[1][0])
    session.add(app)
    session.commit()
    result = ReviewService(session).decide(
        application_id=app.application_id, admin_id=seeded[0]["admin"].id,
        admin_name="admin", admin_email="admin@example.com", decision="approved", feedback="Good"
    )
    assert result.status == "approved" and result.admin_id


def test_ut_34_invalid_decision(seeded, session):
    with pytest.raises(HTTPException):
        ReviewService(session).decide(
            application_id=999, admin_id=1, admin_name="a", admin_email="a@e.com",
            decision="maybe", feedback=""
        )


def test_ut_35_unknown_application(seeded, session):
    with pytest.raises(HTTPException) as error:
        ReviewService(session).decide(
            application_id=999, admin_id=1, admin_name="a", admin_email="a@e.com",
            decision="approved", feedback=""
        )
    assert error.value.status_code == 404


def test_ut_36_feedback_required(seeded, session):
    app = application_for(seeded[0]["bob"], seeded[1][0])
    session.add(app)
    session.commit()
    with pytest.raises(HTTPException) as error:
        ReviewService(session).decide(
            application_id=app.application_id, admin_id=1, admin_name="a",
            admin_email="a@e.com", decision="rejected", feedback=" "
        )
    assert error.value.status_code == 400 and app.status == "pending"


def test_ut_37_revise_decision(seeded, session):
    app = application_for(seeded[0]["bob"], seeded[1][0])
    session.add(app)
    session.commit()
    service = ReviewService(session)
    kwargs = dict(application_id=app.application_id, admin_id=1, admin_name="a", admin_email="a@e.com")
    service.decide(**kwargs, decision="changes_requested", feedback="Fix")
    result = service.decide(**kwargs, decision="approved", feedback="Good")
    assert result.status == "approved" and result.feedback == "Good"


def test_ut_38_student_summary(seeded, session):
    session.add_all([
        application_for(seeded[0]["bob"], seeded[1][0], "pending"),
        application_for(seeded[0]["bob"], seeded[1][1], "approved"),
        application_for(seeded[0]["alice"], seeded[1][0], "rejected"),
    ])
    session.commit()
    summary = DashboardService(session).student_summary(seeded[0]["bob"].id)
    assert summary["application_count"] == 2 and summary["pending_count"] == 1


def test_ut_39_admin_summary(seeded, session):
    session.add(application_for(seeded[0]["bob"], seeded[1][0], "approved"))
    session.commit()
    assert DashboardService(session).admin_summary()["approved_count"] == 1


def test_ut_40_user_repository(seeded, session):
    repo = UserRepository(session)
    assert repo.get_by_username("bob").id == seeded[0]["bob"].id
    assert repo.get_by_email("bob@example.com").id == seeded[0]["bob"].id


def test_ut_41_application_repository(seeded, session):
    repo = ApplicationRepository(session)
    rejected = application_for(seeded[0]["bob"], seeded[1][0], "rejected")
    pending = application_for(seeded[0]["bob"], seeded[1][0], "pending", application_reference="APP-LATEST")
    session.add_all([rejected, pending])
    session.commit()
    assert repo.active_for_student_company(seeded[0]["bob"].id, seeded[1][0].id).status == "pending"
    assert repo.latest_for_student_company(seeded[0]["bob"].id, seeded[1][0].id).application_reference == "APP-LATEST"


def test_ut_42_company_repository(seeded, session):
    result = CompanyRepository(session).list_companies(industry="Technology", location="Kingston")
    assert len(result) == 1 and result[0].name == "ABC Technologies Ltd."
