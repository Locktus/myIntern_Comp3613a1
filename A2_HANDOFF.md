# COMP 3613 Assignment 2: Copilot Agent Handoff

**Audience:** GitHub Copilot in Agent mode, working inside this repository.
**Goal:** add a JSON REST API, fix a few defects, then implement pytest unit and integration tests and a Postman collection, all matching `docs/test-plan.md` exactly.

---

## 0. Operating rules (read first, these override everything else)

1. **This is Assignment 2 mode.** The "Guide / student-build / phase / coaching" rules in `AGENTS.md`, `.github/copilot-instructions.md` and `.agents/skills/` were for Assignment 1 and **do not apply now**. Implement directly. Do not ask coaching questions, do not ask the student for code snippets, do not stop after one feature.
2. **Run things.** After every phase, run the commands listed in that phase and fix failures. The old "do not run verification scripts" rule is void.
3. **Do not edit** `AGENTS.md`, `.agents/skills/**`, `.cursor/skills/**`, `.agents/skills.lock.json`. Do not edit `docs/report.md` or `docs/judge.md`.
4. **Architecture stays layered:** thin routers, then services, then repositories, then models. No `select(...)` or `db.exec(...)` inside any file in `app/routers/`. New API routers call services.
5. **Never weaken a test to make it pass.** If a test fails, fix the code or stop and report the contradiction.
6. **Do not ask questions.** The three open design decisions have defaults below (D1, D2, D3). Use them.
7. **Do not add dependencies.** Everything needed (`pytest`, `pytest-asyncio`, `httpx`, `python-multipart` via `fastapi[all]`) is already in `requirements.txt`.
8. **Tests must never touch the real `database.db` or `app/static/uploads/`.** See section 3.
9. After each phase: run its checks, `git add -A && git commit -m "<phase message>"`, print a short summary (what changed, command output tail), then continue to the next phase without waiting.

### Design decisions (defaults, already confirmed)

- **D1 Duplicate application:** the existing application stays untouched. The new submission is simply not created. (The current code wrongly marks the *existing* application as rejected.)
- **D2 Feedback rule:** decisions `rejected` and `changes_requested` require non-blank feedback; `approved` does not. (Wireframe 4 shows "Feedback / Reason \*".)
- **D3 Status codes:** missing or invalid credentials return **401**; logged in but wrong role returns **403**.

---

## 1. Repository facts (verified)

- FastAPI + SQLModel, Jinja templates, Python 3.10+. Entry: `app/main.py` (`app`). CLI: `python manage.py init` (drops, creates, seeds) and `python manage.py run` (port 5000).
- Seed: users `bob`/`bobpass` (role `regular_user`), `admin`/`adminpass` (role `admin`). Companies: **ABC Technologies Ltd.** (Technology, Kingston, available), **Caribbean Business Services** (Business Services, Bridgetown, available), **Island Finance Group** (Finance, Kingston, **full**).
- Two routers in `app/routers/__init__.py`: `router` (HTML, no prefix) and `api_router` (prefix `/api`). A new router module only works once it is added to the import list at the bottom of `app/routers/__init__.py`.
- Auth: JWT in an `access_token` cookie; `AuthDep` (any logged-in user) and `AdminDep` live in `app/dependencies/auth.py`. Token payload: `sub` (user id as string) and `role`.
- `app/database.py` builds the engine **at import time** from settings. The DB session comes from the `get_session` dependency (override it in tests).
- `app/schemas/__init__.py` does `from .auth import *` then `from .user import *`. **Both define `SignupRequest`; the one in `user.py` wins.** Do not reuse that name. New schema names are given below.
- Existing HTML routes and templates must keep working. Only change them where Phase 0 says so.
- Existing endpoints: `GET /health` returns `{"ok": true}`; `GET /api/users` (currently public, must become admin only).

---

## 2. Phase 0: fixes (commit: "A2 phase 0: fixes")

| # | File | Change |
|---|------|--------|
| F1 | `app/main.py` | The 401 handler must return **status 401**. For paths starting with `/api`, or when the request does not accept `text/html`, return `JSONResponse({"detail": exc.detail}, status_code=401)`. Otherwise render `401.html` with `status_code=401`. |
| F2 | `app/dependencies/auth.py` | `is_admin_dep` raises **403** (not 401) for a logged-in non-admin. Add a `403.html` template (extend `base.html`, "Access denied", link home) and a 403 handler in `app/main.py` with the same JSON-or-HTML split as F1. |
| F3 | `app/dependencies/auth.py` | `get_current_user` reads `Authorization: Bearer <token>` first, then falls back to the cookie. Treat a missing or non-numeric `sub` as 401. Keep the existing function signatures so current routes still work. |
| F4 | `app/services/application.py` | Add module-level `UPLOAD_DIR = Path("app/static/uploads")` and use it inside `submit` (tests monkeypatch it). |
| F5 | `app/services/application.py` | After the company 404 check and before anything is written: resume extension must be in `{.pdf, .doc, .docx}` and size at most `5 * 1024 * 1024` bytes, otherwise `HTTPException(400, ...)`. Read the bytes once and reuse them for the size check and the write. |
| F5b | `app/routers/applications.py` | In the HTML route catch `HTTPException` with 400, `flash(...)` the detail as `"danger"`, and redirect (303) to `/companies/{company_id}/apply`. |
| F6 | `app/services/application.py` | **D1.** Duplicate branch returns `(existing_application, True)` without modifying or committing anything. |
| F7 | `app/routers/companies.py` | `ValueError` from `list_companies` must not 500. In the HTML route catch it, `flash` the message as `"warning"` and list with `availability=None`. |
| F8 | `app/services/review.py` | **D2.** In `decide`, for `rejected` and `changes_requested` raise `HTTPException(400, "Feedback is required ...")` when `feedback.strip()` is empty (check after the decision-value check, before any write). |
| F8b | `app/routers/admin_applications.py` | In the HTML decision route catch `HTTPException` with 400, `flash` the detail as `"danger"`, redirect (303) to `/admin/applications`. Keep the 404 behaviour. |
| F9 | `app/repositories/user.py`, `app/services/auth_service.py` | Add `UserRepository.get_by_email(email)`. `AuthService.register_user` raises `HTTPException(409, "Username or email already exists")` when username or email is taken (check before creating). The HTML register route already catches any exception and flashes. |
| F10 | `pyproject.toml` | Under `[tool.pytest.ini_options]` keep `asyncio_mode = "auto"` and add `testpaths = ["tests"]`, `addopts = "-ra"` and `markers = ["unit: unit tests", "integration: integration tests"]`. |
| F11 | `.gitignore` | Append `.pytest_app.db`. |

**Check:** `python -c "import app.main"` succeeds, then start the app (`python manage.py init && python manage.py run --no-reload`), open `/health`, and confirm `GET /companies` logged out returns status 401.

---

## 3. Phase 1: JSON API (commit: "A2 phase 1: REST API")

### 3.1 New schemas (names are fixed; place in `app/schemas/`, export from `__init__.py`)

- `RegisterRequest`: `first_name: str`, `last_name: str`, `username: str`, `email: EmailStr`, `password: str`
- `LoginRequest`: `username: str`, `password: str`
- `TokenResponse`: `access_token: str`, `token_type: str = "bearer"`, `role: str`
- `MeResponse`: `id`, `username`, `email`, `first_name`, `last_name`, `role`
- `CompanyResponse`: all `Company` fields (`id`, `name`, `offered_position`, `position_description`, `industry`, `location`, `available_positions`, `description`, `resume_instructions`, `contact_email`, `contact_phone`, `address`, `status`)
- `ApplicationResponse`: `application_id`, `application_reference`, `student_id`, `company_id`, `admin_id`, `status`, `resume`, `feedback`, `submitted_at`, `reviewed_at`
- `DecisionRequest`: `decision: str`, `feedback: str = ""`
- Reuse the existing `UserResponse` (`id`, `username`, `email`) for register and users list. It must never expose `password`.

### 3.2 Endpoint contract (every route gets `summary`, `response_model`, explicit `status_code`)

| Method and path | Auth | Request | Success | Errors |
|-----------------|------|---------|---------|--------|
| `POST /api/auth/register` | none | JSON `RegisterRequest` | **201** `UserResponse` | 409 duplicate, 422 invalid |
| `POST /api/auth/login` | none | JSON `LoginRequest` | **200** `TokenResponse` | 401 bad credentials |
| `GET /api/auth/me` | any user | none | 200 `MeResponse` | 401 |
| `GET /api/users` | **admin** | none | 200 `list[UserResponse]` | 401, 403 |
| `GET /api/companies` | any user | query `search`, `availability`, `industry`, `location` (all optional) | 200 `list[CompanyResponse]` | 401, **400** invalid availability |
| `GET /api/companies/{company_id}` | any user | none | 200 `CompanyResponse` | 401, 404 |
| `POST /api/applications` | student (admin gets 403) | multipart: `company_id` (int), `resume` (file) | **201** `ApplicationResponse` (a full company yields 201 with status `rejected`) | 400 bad file, 401, 403 admin, 404 company, **409** duplicate active application |
| `GET /api/applications/me` | any user | none | 200 `list[ApplicationResponse]`, newest first, own only | 401 |
| `GET /api/applications/{application_id}` | owner or admin | none | 200 `ApplicationResponse` | 401, **403** someone else's, 404 |
| `GET /api/admin/applications` | **admin** | none | 200 `list[ApplicationResponse]` | 401, 403 |
| `PUT /api/admin/applications/{application_id}/decision` | **admin** | JSON `DecisionRequest` | 200 `ApplicationResponse` | 400 invalid decision or missing feedback, 401, 403, 404 |

Notes:
- Login returns the token in the body for API clients. It does **not** need to set a cookie. The HTML `/login` flow stays as is.
- Duplicate-application handling: `ApplicationService.submit` returns `(application, was_duplicate)`. The API turns `was_duplicate` into `HTTPException(409, "You already have an active application for this company.")`.
- Ownership check for `GET /api/applications/{id}`: add `ApplicationService.get_for_user(application_id, user)` which raises 404 or 403. Do not put the check in the router.
- Admin list: add `ApplicationService.list_all()` or reuse `ReviewService.list_applications()`. Keep it simple.
- `ValueError` from `CompanyService.list_companies` becomes `HTTPException(400, str(exc))` in the API router.
- Responses for datetimes are ISO strings (FastAPI default).

### 3.3 Files to create or edit

- Create `app/routers/api_auth.py`, `api_companies.py`, `api_applications.py`, `api_admin.py`; edit `app/routers/users.py` (make `list_users` depend on `AdminDep`). Register new modules in `app/routers/__init__.py`.
- Add any missing service methods listed above (services and repositories only, no SQL in routers).

**Check:** run the app, open `http://127.0.0.1:5000/docs` and confirm all routes appear under "API Endpoints". Then, with `curl`, log in as `bob` via `/api/auth/login` and call `/api/companies` using the token.

---

## 4. Phase 2: pytest infrastructure and tests (commit: "A2 phase 2: tests")

### 4.1 Layout

```
tests/
  conftest.py
  factories.py
  unit/
    test_security.py          test_pagination_flash.py   test_auth_dependency.py
    test_auth_service.py      test_company_service.py    test_application_service.py
    test_review_service.py    test_dashboard_service.py  test_repositories.py
  integration/
    test_api_auth.py          test_api_companies.py      test_api_applications.py
    test_api_admin.py         test_api_users.py          test_html_flows.py
```

Add empty `__init__.py` files only if pytest import errors require them.

### 4.2 `tests/conftest.py` requirements

1. **Before any `app` import**, set `os.environ["DATABASE_URI"] = "sqlite:///./.pytest_app.db"`, `os.environ["SECRET_KEY"] = "test-secret-key-for-pytest-0123456789"`, `os.environ["ENV"] = "ci"`. (`app.database` builds an engine from settings at import; a bare `sqlite://` would break because of the pool arguments, and `ENV=ci` keeps SQL echo off.)
2. `pytest_collection_modifyitems`: add marker `unit` to items under `tests/unit/` and `integration` to items under `tests/integration/`.
3. Fixture `engine` (function scope): `create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)`, `import app.models`, `SQLModel.metadata.create_all`; dispose afterwards.
4. Fixture `session`: `Session(engine)`.
5. Fixture `client`: override `app.database.get_session` (the dependency that `SessionDep` uses) so it yields sessions from `engine`; return `TestClient(fastapi_app, follow_redirects=False)`; clear `dependency_overrides` afterwards. **Do not use `with TestClient(...)`**, because that triggers the lifespan and would create tables in the real database.
6. Name clash warning: `app` is both the package and the FastAPI instance. Import it as `from app.main import app as fastapi_app`.
7. Autouse fixture `upload_dir(tmp_path, monkeypatch)`: `monkeypatch.setattr("app.services.application.UPLOAD_DIR", tmp_path / "uploads")`.
8. `seeded` fixture using `tests/factories.py`: creates `bob` (regular_user), `alice` (second regular_user, for ownership tests), `admin` (admin), and the three seed companies with the same values as `cmd_seed` in `app/cli.py`. Passwords: `bobpass`, `alicepass`, `adminpass` (hash with `encrypt_password`; create via `UserRepository` and `RegularUserCreate` / `AdminCreate`).
9. Helpers: `login_token(client, username, password)` (calls `/api/auth/login`), `auth(token)` returning `{"Authorization": f"Bearer {token}"}`, and `pdf_upload()` returning `{"resume": ("resume.pdf", b"%PDF-1.4 test", "application/pdf")}`.
10. Fixtures `student_headers`, `admin_headers`, `alice_headers` built on the above.

### 4.3 Test implementation rules

- Implement **every row** of `docs/test-plan.md` sections 2 and 3: one test function per ID, named `test_ut_NN_<short_slug>` or `test_it_NN_<short_slug>` (two-digit IDs), with a one-line docstring starting with the ID (e.g. `"""UT-07: Pagination page maths and flags."""`). Where one plan row needs several cases (for example "existing id; unknown id"), keep them in the same function or use `pytest.mark.parametrize`, but keep one function name per ID.
- Unit tests for `AuthService` use `unittest.mock.MagicMock` for the repository. Service and repository unit tests use the `session` fixture. Dependency tests (`get_current_user`) are `async def` and build a minimal fake request (for example `SimpleNamespace(cookies={...}, headers={...})`) because `asyncio_mode = "auto"` is already configured.
- Integration tests use `client` only (no direct service calls except via the factories).
- Plan wording for expected status codes must match the contract in section 3.2 exactly.

### 4.4 Checks

```bash
pytest tests/unit -v
pytest tests/integration -v
pytest -m unit -q
pytest -m integration -q
pytest -q          # everything green
pytest --collect-only -q tests/unit | tail -1          # expect 42 tests
pytest --collect-only -q tests/integration | tail -1   # expect 34 tests
```

If a count differs, find the missing ID and add it. Confirm afterwards that `database.db` was not modified and that `app/static/uploads/` has no new files (`git status` should be clean apart from your changes).

Then generate the traceability table: replace section 5 of `docs/test-plan.md` with a table of every `UT-NN`, `IT-NN` and its `file::function`. Do this with a small script that reads function names and docstrings; do not type it by hand.

---

## 5. Phase 3: Postman collection (commit: "A2 phase 3: postman")

Create under `postman/`:

- `MyIntern_API.postman_collection.json` (Collection v2.1)
- `MyIntern_Local.postman_environment.json` with `baseUrl = http://127.0.0.1:5000`
- `sample_resume.pdf` (tiny valid PDF, a few hundred bytes)
- `not_a_resume.txt` (one line of text)

Requirements:

1. Implement all 28 requests of `docs/test-plan.md` section 4, **in that order**, grouped into folders Setup, Auth, Companies, Applications, Admin, Users. Request names start with the plan ID (for example `PM-15 Submit application`).
2. All URLs use `{{baseUrl}}`. Protected requests set the header `Authorization: Bearer {{studentToken}}` or `{{adminToken}}` (set on the request, not collection-wide, because some requests deliberately send no token or the wrong one).
3. The first register request has a pre-request script that sets `studentUsername = "student_" + Date.now()`, `studentEmail = studentUsername + "@example.com"`. The body uses those variables. The duplicate-register request reuses them. This keeps the collection re-runnable without resetting the DB. Student password is the collection variable `studentPassword = "Passw0rd!"`.
4. Every request has a **Tests** script. Minimum per request: status code assertion, `Content-Type` contains `application/json` (except the file-upload failure cases if they still return JSON, which they do), plus the specific checks listed in the plan. Use `pm.test`, `pm.expect`, and `pm.collectionVariables.set` for `studentToken`, `adminToken`, `availableCompanyId`, `fullCompanyId`, `applicationId`.
5. `availableCompanyId` = first company in the list with `status == "available"`; `fullCompanyId` = the one with `status == "full"`.
6. File uploads: `form-data` with `company_id` (text) and `resume` (file, `src` = `sample_resume.pdf`). The invalid-file request uses `not_a_resume.txt`.
7. Add a short `postman/README.md`: prerequisites (`python manage.py init`, `python manage.py run`), how to import both JSON files, how to set the Runner's working directory to the `postman/` folder so the files are found, and the Newman command below.

**Check (Newman):**

```bash
python manage.py init
python manage.py run --no-reload &        # wait until /health responds
npx --yes newman run postman/MyIntern_API.postman_collection.json \
  -e postman/MyIntern_Local.postman_environment.json --working-dir postman
```

All 28 requests and all assertions must pass. Run it **twice in a row** without re-initialising the database; the second run must also pass.

---

## 6. Phase 4: docs (commit: "A2 phase 4: docs")

1. In `README.md` add a "Testing" section: install (`pip install -r requirements.txt`), run unit tests, run integration tests, run both, run by marker, how to run the Postman collection (link to `postman/README.md`), and the note that tests use an in-memory database.
2. Add `docs/a2-report.md` as a skeleton for the PDF with these headings in order, using placeholders where a human must add screenshots: Name and ID, Project description, Use case diagram (`diagrams/use-case.png`), Entity relationship diagram (copy the Mermaid block from `docs/report.md` "Model diagram"), Application wireframe (`wireframes/Internship%20Platform%20UI%20Wireframe%20Storyboard.png`), Test plans (include the contents of `docs/test-plan.md` sections 1 to 4), Implementation (repo link placeholder; list of test files; Postman collection path), Reports (three placeholders: unit run screenshot, integration run screenshot, Postman run screenshot), UAT results (reference the results table in `docs/test-plan.md`). Do not invent screenshots.
3. Final full verification: `pytest -q` green, Newman green, `git status` clean.

---

## 7. Final summary Copilot must print

- Files added or changed (grouped by phase)
- Counts: unit tests, integration tests, Postman requests
- Last lines of `pytest tests/unit -v`, `pytest tests/integration -v`, and the Newman run
- Anything that deviated from this document and why

---

## 8. For the human (not Copilot): remaining steps

1. Start the app (`python manage.py init`, `python manage.py run`) and walk through the 15 UAT rows in `docs/test-plan.md`. Fill in the results table, taking a few screenshots.
2. Take screenshots: `pytest tests/unit -v` (all passing), `pytest tests/integration -v` (all passing), and the Postman Collection Runner showing all green. Export the collection JSON from Postman only if you changed it (the file in `postman/` is already the one to submit).
3. Make sure the repository is public (or accessible to the marker) and the new files are pushed.
4. Assemble the single PDF from `docs/a2-report.md` in the order the assignment lists, adding your name and student ID.
