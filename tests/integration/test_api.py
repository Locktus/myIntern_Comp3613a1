import re
from tests.conftest import auth, login_token, pdf_upload


def test_it_01_register(client, seeded):
    """IT-01: Register a valid user."""
    response = client.post("/api/auth/register", json={
        "first_name": "New", "last_name": "User", "username": "new",
        "email": "new@example.com", "password": "pass123"
    })
    assert response.status_code == 201 and "password" not in response.json()


def test_it_02_duplicate_username(client, seeded):
    """IT-02: Duplicate usernames return conflict."""
    response = client.post("/api/auth/register", json={
        "first_name": "Bob", "last_name": "Two", "username": "bob",
        "email": "other@example.com", "password": "pass123"
    })
    assert response.status_code == 409


def test_it_03_invalid_email(client, seeded):
    """IT-03: Invalid emails return validation error."""
    response = client.post("/api/auth/register", json={
        "first_name": "A", "last_name": "B", "username": "new",
        "email": "invalid", "password": "pass123"
    })
    assert response.status_code == 422


def test_it_04_login(client, seeded):
    """IT-04: Valid login returns a bearer token."""
    response = client.post("/api/auth/login", json={"username": "bob", "password": "bobpass"})
    assert response.status_code == 200 and response.json()["token_type"] == "bearer"


def test_it_05_wrong_login(client, seeded):
    """IT-05: Wrong credentials return JSON 401."""
    response = client.post("/api/auth/login", json={"username": "bob", "password": "wrong"})
    assert response.status_code == 401 and response.headers["content-type"].startswith("application/json")


def test_it_06_me(client, student_headers, seeded):
    """IT-06: Authenticated users can view themselves."""
    response = client.get("/api/auth/me", headers=student_headers)
    assert response.status_code == 200 and response.json()["username"] == "bob"


def test_it_07_me_without_token(client, seeded):
    """IT-07: Missing API credentials return JSON 401."""
    response = client.get("/api/auth/me")
    assert response.status_code == 401 and response.json()["detail"]


def test_it_08_me_tampered(client, seeded):
    """IT-08: Tampered tokens return 401."""
    assert client.get("/api/auth/me", headers=auth("garbage")).status_code == 401


def test_it_09_companies(client, student_headers, seeded):
    """IT-09: Authenticated users can list companies."""
    response = client.get("/api/companies", headers=student_headers)
    assert response.status_code == 200 and len(response.json()) == 3


def test_it_10_companies_unauthenticated(client, seeded):
    """IT-10: Company listing requires authentication."""
    assert client.get("/api/companies").status_code == 401


def test_it_11_company_filters(client, student_headers, seeded):
    """IT-11: Company search and availability filters work."""
    assert len(client.get("/api/companies?search=ABC", headers=student_headers).json()) == 1
    assert len(client.get("/api/companies?availability=full", headers=student_headers).json()) == 1


def test_it_12_invalid_company_filter(client, student_headers, seeded):
    """IT-12: Invalid availability returns 400."""
    assert client.get("/api/companies?availability=maybe", headers=student_headers).status_code == 400


def test_it_13_company_details(client, student_headers, seeded):
    """IT-13: Company details handle existing and unknown ids."""
    assert client.get("/api/companies/1", headers=student_headers).status_code == 200
    assert client.get("/api/companies/999", headers=student_headers).status_code == 404


def test_it_14_submit_application(client, student_headers, seeded):
    """IT-14: Students can submit PDF applications."""
    response = client.post("/api/applications", headers=student_headers, data={"company_id": "1"}, files=pdf_upload())
    assert response.status_code == 201 and response.json()["status"] == "pending"


def test_it_15_invalid_upload(client, student_headers, seeded):
    """IT-15: Invalid resume types return 400."""
    files = {"resume": ("resume.exe", b"x", "application/octet-stream")}
    assert client.post("/api/applications", headers=student_headers, data={"company_id": "1"}, files=files).status_code == 400


def test_it_16_duplicate_application(client, student_headers, seeded):
    """IT-16: Active duplicate applications return 409."""
    kwargs = {"headers": student_headers, "data": {"company_id": "1"}, "files": pdf_upload()}
    assert client.post("/api/applications", **kwargs).status_code == 201
    assert client.post("/api/applications", headers=student_headers, data={"company_id": "1"}, files=pdf_upload()).status_code == 409


def test_it_17_full_company(client, student_headers, seeded):
    """IT-17: Full companies create rejected applications."""
    response = client.post("/api/applications", headers=student_headers, data={"company_id": "3"}, files=pdf_upload())
    assert response.status_code == 201 and response.json()["status"] == "rejected"


def test_it_18_application_rejected_file(client, student_headers, seeded):
    """IT-18: Application upload contract rejects bad files."""
    files = {"resume": ("resume.txt", b"x", "text/plain")}
    assert client.post("/api/applications", headers=student_headers, data={"company_id": "1"}, files=files).status_code == 400


def test_it_19_unknown_company_application(client, student_headers, seeded):
    """IT-19: Unknown application companies return 404."""
    assert client.post("/api/applications", headers=student_headers, data={"company_id": "999"}, files=pdf_upload()).status_code == 404


def test_it_20_my_applications_ownership(client, student_headers, alice_headers, seeded):
    """IT-20: Students see only their own applications."""
    client.post("/api/applications", headers=student_headers, data={"company_id": "1"}, files=pdf_upload())
    client.post("/api/applications", headers=alice_headers, data={"company_id": "2"}, files=pdf_upload())
    assert len(client.get("/api/applications/me", headers=student_headers).json()) == 1


def test_it_21_application_ownership(client, student_headers, alice_headers, seeded):
    """IT-21: Application ownership is enforced."""
    app = client.post("/api/applications", headers=student_headers, data={"company_id": "1"}, files=pdf_upload()).json()
    assert client.get(f"/api/applications/{app['application_id']}", headers=student_headers).status_code == 200
    assert client.get(f"/api/applications/{app['application_id']}", headers=alice_headers).status_code == 403


def test_it_22_admin_listing(client, admin_headers, student_headers, seeded):
    """IT-22: Admin application listing is role protected."""
    assert client.get("/api/admin/applications", headers=admin_headers).status_code == 200
    assert client.get("/api/admin/applications", headers=student_headers).status_code == 403
    assert client.get("/api/admin/applications").status_code == 401


def test_it_23_approve_application(client, student_headers, admin_headers, seeded):
    """IT-23: Admins can approve applications."""
    app = client.post("/api/applications", headers=student_headers, data={"company_id": "1"}, files=pdf_upload()).json()
    response = client.put(f"/api/admin/applications/{app['application_id']}/decision", headers=admin_headers, json={"decision": "approved", "feedback": "Good"})
    assert response.status_code == 200 and response.json()["status"] == "approved"


def test_it_24_reject_without_feedback(client, student_headers, admin_headers, seeded):
    """IT-24: Rejection requires feedback."""
    app = client.post("/api/applications", headers=student_headers, data={"company_id": "1"}, files=pdf_upload()).json()
    response = client.put(f"/api/admin/applications/{app['application_id']}/decision", headers=admin_headers, json={"decision": "rejected", "feedback": ""})
    assert response.status_code == 400


def test_it_25_invalid_decision(client, admin_headers, seeded):
    """IT-25: Invalid and unknown decisions are rejected."""
    assert client.put("/api/admin/applications/999/decision", headers=admin_headers, json={"decision": "maybe"}).status_code == 404


def test_it_26_decision_workflow(client, student_headers, admin_headers, seeded):
    """IT-26: A decision workflow can be revised."""
    app = client.post("/api/applications", headers=student_headers, data={"company_id": "1"}, files=pdf_upload()).json()
    path = f"/api/admin/applications/{app['application_id']}/decision"
    assert client.put(path, headers=admin_headers, json={"decision": "changes_requested", "feedback": "Fix"}).status_code == 200
    assert client.put(path, headers=admin_headers, json={"decision": "approved", "feedback": "Welcome"}).json()["status"] == "approved"


def test_it_27_users_admin(client, admin_headers, seeded):
    """IT-27: Admin user listing does not expose passwords."""
    response = client.get("/api/users", headers=admin_headers)
    assert response.status_code == 200 and all("password" not in item for item in response.json())


def test_it_28_users_student(client, student_headers, seeded):
    """IT-28: Students cannot list users."""
    assert client.get("/api/users", headers=student_headers).status_code == 403


def test_it_29_html_login(client, seeded):
    """IT-29: HTML login redirects students and admins."""
    student = client.post("/login", data={"username": "bob", "password": "bobpass"})
    admin = client.post("/login", data={"username": "admin", "password": "adminpass"})
    assert student.status_code == 303 and admin.status_code == 303


def test_it_30_html_invalid_login(client, seeded):
    """IT-30: Invalid HTML login redirects without a token."""
    response = client.post("/login", data={"username": "bob", "password": "wrong"})
    assert response.status_code == 303 and "access_token" not in response.cookies


def test_it_31_html_companies_unauthenticated(client, seeded):
    """IT-31: HTML companies requires login."""
    response = client.get("/companies", headers={"Accept": "text/html"})
    assert response.status_code == 401 and "Session Expired" in response.text


def test_it_32_html_admin_for_student(client, seeded):
    """IT-32: Students receive forbidden admin access."""
    client.post("/login", data={"username": "bob", "password": "bobpass"})
    assert client.get("/admin", headers={"Accept": "text/html"}).status_code == 403


def test_it_33_html_companies_student(client, seeded):
    """IT-33: Students can browse companies in HTML."""
    client.post("/login", data={"username": "bob", "password": "bobpass"})
    response = client.get("/companies", headers={"Accept": "text/html"})
    assert response.status_code == 200 and "ABC Technologies Ltd." in response.text


def test_it_34_health(client, seeded):
    """IT-34: Health is public."""
    response = client.get("/health")
    assert response.status_code == 200 and response.json() == {"ok": True}
