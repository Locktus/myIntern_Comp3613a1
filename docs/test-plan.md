# MyIntern: Test Plans (COMP 3613 Assignment 2)

This document holds the four test plans for the MyIntern internship platform. Every row has a unique ID. Each automated test is named after its ID (for example `test_ut_07_...`), so graders can trace plan to implementation. The traceability table at the end is filled in when the tests are written.

## 0. Approach and environment

| Level | What it proves | Tooling | How it is run |
|-------|----------------|---------|---------------|
| Unit | One module in isolation (functions, services, repositories, dependencies) | pytest, in-memory SQLite, mocks where a collaborator is not under test | `pytest tests/unit -v` |
| Integration | Routes, auth, services, repositories and database working together | pytest + FastAPI `TestClient`, in-memory SQLite | `pytest tests/integration -v` |
| API | The deployed contract as an external client sees it | Postman collection with test scripts (Newman-compatible) | Postman Collection Runner |
| User acceptance | A person can complete each workflow described by the wireframes | Manual, against the running app | Tester follows the steps and records Pass/Fail |

**Test data (seeded by `python manage.py init`):** users `bob` / `bobpass` (regular_user) and `admin` / `adminpass` (admin); companies ABC Technologies Ltd. (available), Caribbean Business Services (available), Island Finance Group (full).

**Business rules under test:** one active application per student per company; applications to full companies are automatically rejected; resumes must be PDF, DOC or DOCX up to 5 MB; admins cannot apply; rejecting or requesting changes requires feedback; decisions can be revised; students see only their own applications.

## 1. User Acceptance Test Plan

Tester runs each task in the browser against the running app (`python manage.py init`, then `python manage.py run`, then open http://127.0.0.1:5000). Record Pass or Fail and any note in the results table.

| ID | Task | Role | Preconditions | Steps | Success criteria | Wireframe ref |
|----|------|------|---------------|-------|------------------|---------------|
| UAT-01 | Register and sign in | New user | App running; landing page open | 1. Open `/` and click Register. 2. Fill first name, last name, username, email, password. 3. Submit. 4. Sign in with the new account. | Success message shown after registering; sign-in lands on the student home page showing the user's name. | Auth screens (not in storyboard); signed-in header as in Wireframe 1 |
| UAT-02 | Browse participating companies | Student (bob) | Logged in as bob | 1. Click **Companies** in the navigation. | All 3 seeded companies are listed with industry, location and an availability badge; Island Finance Group is marked Full. | Wireframe 1 |
| UAT-03 | Search and filter companies | Student (bob) | On the Companies page | 1. Search for `ABC`. 2. Clear the search. 3. Set availability to Full. 4. Clear it and choose an industry, then a location. | Each action narrows the list correctly (e.g. `ABC` shows only ABC Technologies Ltd.; Full shows only Island Finance Group); clearing restores all. | Wireframe 1 (search bar and dropdowns) |
| UAT-04 | View company details | Student (bob) | On the Companies page | 1. Click **View details** on ABC Technologies Ltd. | Company description, position offered, contact details and an **Apply for this position** button are shown. | Wireframe 1 and 2 |
| UAT-05 | Full company cannot be applied to | Student (bob) | On the Companies page | 1. Open Island Finance Group details. | Page states the company is full; no Apply button is shown. | Wireframe 1 (full companies have no apply option) |
| UAT-06 | Submit an application | Student (bob) | Logged in; no previous application to ABC | 1. Open ABC Technologies Ltd. and click Apply. 2. Choose a small PDF resume. 3. Submit. | Confirmation page shows an `APP-XXXXXXXX` reference, the company and status Pending. | Wireframe 2 (confirmation panel) |
| UAT-07 | Duplicate application is not accepted | Student (bob) | UAT-06 completed | 1. Open ABC Technologies Ltd. apply form again. 2. Upload a resume and submit. | A warning explains the duplicate was not accepted; the original application still shows status Pending in My Applications. | Wireframe 2 (existing status shown instead of a new submission) |
| UAT-08 | Invalid resume file is refused | Student (bob) | On an apply form | 1. Choose a `.txt` file (select All files in the picker). 2. Submit. | Submission is refused with a clear message that only PDF, DOC or DOCX up to 5 MB are allowed; no application is created. | Wireframe 2 (PDF, DOC or DOCX, max 5MB) |
| UAT-09 | View my applications | Student (bob) | UAT-06 completed | 1. Click **My Applications**. | Table lists each application with company, status, submitted date and reference. | Wireframe 3 (left) |
| UAT-10 | Admin requests changes with feedback | Admin | bob has a Pending application; logged in as admin | 1. Open **Review applications**. 2. Find bob's application and open its resume link. 3. Enter feedback `Please add your GPA`. 4. Click **Request changes**. | Confirmation page shows status Changes requested and the feedback; the review queue shows the updated status. | Wireframe 3 (right) and 4 |
| UAT-11 | Student sees admin feedback | Student (bob) | UAT-10 completed | 1. Log in as bob. 2. Open **My Applications**. | Application shows status Changes requested together with the admin's feedback text. | Wireframe 3 (left) |
| UAT-12 | Admin revises decision to approved | Admin | UAT-10 completed | 1. Reopen the same application in the review queue. 2. Enter feedback `Approved, welcome aboard`. 3. Click **Approve**. | Status becomes Approved and the new feedback replaces the old; bob sees Approved after refreshing My Applications. | Wireframe 4 |
| UAT-13 | Reject or request-changes requires feedback | Admin | A Pending application exists | 1. Leave feedback empty. 2. Click **Reject**. | A message says feedback is required; the application status is unchanged. | Wireframe 4 (Feedback / Reason is a required field) |
| UAT-14 | Access control | Anonymous user and student | App running | 1. Logged out, open `/companies`. 2. Log in as bob and open `/admin`. | Logged out: sign-in-required page. As bob: access-denied page and no admin data visible. | Not in storyboard (authorization) |
| UAT-15 | Log out | Any logged-in user | Logged in | 1. Click **Log Out**. 2. Press browser Back, or open `/app`. | User is returned to the login page; protected pages require signing in again. | Wireframe 1 (Log Out in sidebar) |

### UAT results (complete after testing)

Tester name: Kris Partapsingh  Date: 2026-11-10  Build/commit: b5c1ebc

| ID | Result (Pass/Fail) | Observed behaviour / notes | Screenshot |
|----|--------------------|----------------------------|------------|
| UAT-01 | Pass | Registration, sign-in, and student home page completed. | `evidence/screenshots/uat/UAT1_1.png`, `UAT1_2.png`, `UAT1_3.png` |
| UAT-02 | Pass | All seeded companies and availability states displayed. | `evidence/screenshots/uat/UAT2.png` |
| UAT-03 | Pass | Search and company filters narrowed and restored results. | `evidence/screenshots/uat/UAT3.png` |
| UAT-04 | Pass | Company details, position, contacts, and apply action displayed. | `evidence/screenshots/uat/UAT4.png` |
| UAT-05 | Pass | Full company displayed without an apply action. | `evidence/screenshots/uat/UAT5.png` |
| UAT-06 | Pass | Resume submission produced a reference and pending status. | `evidence/screenshots/uat/UAT6_1.png`, `UAT6_2.png` |
| UAT-07 | Pass | Duplicate active application was refused. | `evidence/screenshots/uat/UAT7.png` |
| UAT-08 | Pass | Invalid resume file was refused. | `evidence/screenshots/uat/UAT8.png` |
| UAT-09 | Pass | Student applications list displayed required fields. | `evidence/screenshots/uat/UAT9.png` |
| UAT-10 | Pass | Admin requested changes and saved feedback. | `evidence/screenshots/uat/UAT10.png` |
| UAT-11 | Pass | Student saw the changes-requested status and feedback. | `evidence/screenshots/uat/UAT11.png` |
| UAT-12 | Pass | Admin revised the decision to approved. | `evidence/screenshots/uat/UAT12.png` |
| UAT-13 | Pass | Empty decision feedback was rejected. | `evidence/screenshots/uat/UAT13.png` |
| UAT-14 | Pass | Anonymous and student access restrictions worked. | `evidence/screenshots/uat/UAT14_1.png`, `UAT14_2.png` |
| UAT-15 | Pass | Logout returned to login and protected pages remained guarded. | `evidence/screenshots/uat/UAT15.png` |

## 2. Unit Test Plan

| ID | Module (`app/`) | Behaviour tested | Input / setup | Expected result | Isolation |
|----|-----------------|------------------|---------------|-----------------|-----------|
| UT-01 | utilities/security | `encrypt_password` hashes a password | `"pass123"` | Returns a non-empty string different from the input | Pure function |
| UT-02 | utilities/security | `verify_password` with the correct password | Hash of `pass123`, check `pass123` | Returns True | Pure function |
| UT-03 | utilities/security | `verify_password` with a wrong password | Hash of `pass123`, check `wrong` | Returns False | Pure function |
| UT-04 | utilities/security | `create_access_token` payload | `{"sub":"7","role":"admin"}` | Decoded token has sub `7`, role `admin` and a future `exp` | Pure function |
| UT-05 | utilities/security | `create_access_token` expiry | `expires_delta` = -1 minute | `jwt.decode` raises `ExpiredSignatureError` | Pure function |
| UT-06 | utilities/pagination | `Pagination` page maths and flags | 25 items, limit 10, pages 1, 2, 3 | `total_pages`=3; `has_prev` F/T/T; `has_next` T/T/F; `next_num`/`prev_num` correct | Pure class |
| UT-07 | utilities/flash | `flash` and `get_flashed_messages` | Fake request object with a `session` dict | Messages stored with type; retrieval returns them and empties the list; second call returns `[]` | Fake request |
| UT-08 | dependencies/auth | `get_current_user` without credentials | No header, no cookie | Raises HTTPException 401 | Fake request, in-memory DB |
| UT-09 | dependencies/auth | `get_current_user` with a tampered token | Cookie `access_token`=`garbage` | Raises HTTPException 401 | Fake request, in-memory DB |
| UT-10 | dependencies/auth | `get_current_user` with a Bearer header | Valid token in `Authorization: Bearer ...` | Returns the matching `User` | Fake request, in-memory DB |
| UT-11 | dependencies/auth | `get_current_user` with a cookie | Valid token in `access_token` cookie | Returns the matching `User` | Fake request, in-memory DB |
| UT-12 | dependencies/auth | `is_admin` | User with role `admin`, user with role `regular_user` | True for admin, False for regular user | Plain objects |
| UT-13 | services/auth_service | `authenticate_user` valid credentials | Mock repo returns user with hashed password | Returns a token whose `sub` equals the user id and role matches | Mocked repository |
| UT-14 | services/auth_service | `authenticate_user` wrong password | Mock repo returns user; wrong password | Returns None | Mocked repository |
| UT-15 | services/auth_service | `authenticate_user` unknown user | Mock repo returns None | Returns None | Mocked repository |
| UT-16 | services/auth_service | `register_user` builds the new user | Names with surrounding spaces | Names stripped, password stored hashed (not equal to input), role `regular_user` | Mocked repository |
| UT-17 | services/auth_service | `register_user` duplicate | Mock repo reports existing username or email | Raises HTTPException 409 | Mocked repository |
| UT-18 | services/company | `list_companies` with no filters | 3 seeded companies | Returns 3, ordered by name | In-memory DB |
| UT-19 | services/company | `list_companies` normalises availability | `"Available"` and `" FULL "` | Treated as `available` and `full` | In-memory DB |
| UT-20 | services/company | `list_companies` accepts the `avaliable` typo | `"avaliable"` | Treated as `available` | In-memory DB |
| UT-21 | services/company | `list_companies` invalid availability | `"maybe"` | Raises `ValueError` | In-memory DB |
| UT-22 | services/company | `list_companies` search | `search="abc"` | Case-insensitive partial match on name returns ABC Technologies Ltd. only | In-memory DB |
| UT-23 | services/company | `filter_options` | 3 seeded companies | Returns sorted, de-duplicated industries and locations | In-memory DB |
| UT-24 | services/company | `get_company` unknown id | id 999 | Returns None | In-memory DB |
| UT-25 | services/application | `submit` unknown company | company_id 999 | Raises HTTPException 404 | In-memory DB, temp upload dir |
| UT-26 | services/application | `submit` happy path | Student, available company, small PDF | Status `pending`; reference matches `^APP-[0-9A-F]{8}$`; resume path starts `/static/uploads/`; file exists in temp dir; `was_duplicate` False | In-memory DB, temp upload dir |
| UT-27 | services/application | `submit` to a full company | Company with status `full` | Application saved with status `rejected` | In-memory DB, temp upload dir |
| UT-28 | services/application | `submit` duplicate active application | Student already has a pending application to the company | Returns the existing application unchanged with `was_duplicate` True; still only 1 row | In-memory DB, temp upload dir |
| UT-29 | services/application | `submit` after a rejected application | Previous application status `rejected` | New application is created | In-memory DB, temp upload dir |
| UT-30 | services/application | `submit` invalid file type | `resume.exe` | Raises HTTPException 400; no file written | In-memory DB, temp upload dir |
| UT-31 | services/application | `submit` oversize file | Resume larger than 5 MB | Raises HTTPException 400; no file written | In-memory DB, temp upload dir |
| UT-32 | services/application | `submit` creates a `Student` row if missing | User id with no `Student` record | `Student` row created with the user's name and email | In-memory DB, temp upload dir |
| UT-33 | services/review | `decide` approved | Pending application, admin id 1, feedback `Good` | Status `approved`; `admin_id` set; `reviewed_at` set; feedback saved; `Admin` row created if missing | In-memory DB |
| UT-34 | services/review | `decide` invalid decision | `"maybe"` | Raises HTTPException 400 | In-memory DB |
| UT-35 | services/review | `decide` unknown application | id 999 | Raises HTTPException 404 | In-memory DB |
| UT-36 | services/review | `decide` requires feedback for reject and request-changes | `rejected` and `changes_requested` with blank feedback | Raises HTTPException 400; application unchanged | In-memory DB |
| UT-37 | services/review | `decide` can be revised | Decide `changes_requested`, then `approved` | Second decision overwrites status and feedback | In-memory DB |
| UT-38 | services/dashboard | `student_summary` counts | Two students with mixed statuses | Counts include only that student's applications; pending count includes `pending`, `under_review`, `changes_requested` | In-memory DB |
| UT-39 | services/dashboard | `admin_summary` counts | Mixed statuses across students | Totals, pending, approved, rejected and available-company counts are correct; at most 5 recent applications | In-memory DB |
| UT-40 | repositories/user | `UserRepository` create and lookups | Create a user | `get_by_username`, `get_by_id`, `get_by_email` return it; duplicate username raises | In-memory DB |
| UT-41 | repositories/application | `ApplicationRepository` active and latest queries | Rejected plus pending applications | `active_for_student_company` ignores rejected; `latest_for_student_company` returns the newest | In-memory DB |
| UT-42 | repositories/company | `CompanyRepository.list_companies` combined filters | industry + location | Only companies matching both are returned | In-memory DB |

## 3. Integration Test Plan

All run through `TestClient` against a fresh in-memory database seeded with the users and companies above (plus a second student for ownership checks).

| ID | Area | Endpoint | Scenario | Expected result |
|----|------|----------|----------|-----------------|
| IT-01 | Auth | POST /api/auth/register | Valid new user | 201; body has id, username, email; no password field |
| IT-02 | Auth | POST /api/auth/register | Duplicate username | 409 |
| IT-03 | Auth | POST /api/auth/register | Invalid email format | 422 |
| IT-04 | Auth | POST /api/auth/login | Valid credentials (bob) | 200; `access_token`, `token_type`=`bearer`, `role`=`regular_user` |
| IT-05 | Auth | POST /api/auth/login | Wrong password | 401 JSON |
| IT-06 | Auth | GET /api/auth/me | Valid Bearer token | 200; matches the logged-in user |
| IT-07 | Auth | GET /api/auth/me | No token | 401 with a JSON body (not an HTML page) |
| IT-08 | Auth | GET /api/auth/me | Tampered token | 401 |
| IT-09 | Companies | GET /api/companies | Authenticated | 200; list of 3 seeded companies |
| IT-10 | Companies | GET /api/companies | No token | 401 |
| IT-11 | Companies | GET /api/companies?search=&availability= | Search `ABC`; `availability=full` | Only ABC returned; only Island Finance returned |
| IT-12 | Companies | GET /api/companies?availability=maybe | Invalid availability | 400 |
| IT-13 | Companies | GET /api/companies/{id} | Existing id; unknown id | 200 with full details; 404 |
| IT-14 | Applications | POST /api/applications | Student uploads a PDF to an available company | 201; status `pending`; reference `APP-XXXXXXXX` |
| IT-15 | Applications | POST /api/applications | Upload a `.exe` file | 400; no application created |
| IT-16 | Applications | POST /api/applications | Second application to same company while one is active | 409; original unchanged |
| IT-17 | Applications | POST /api/applications | Apply to a full company | 201 with status `rejected` |
| IT-18 | Applications | POST /api/applications | Admin attempts to apply | 403 |
| IT-19 | Applications | POST /api/applications | Unknown company id | 404 |
| IT-20 | Applications | GET /api/applications/me | Two students each applied | Each student sees only their own applications |
| IT-21 | Applications | GET /api/applications/{id} | Own application; another student's application | 200; 403 |
| IT-22 | Admin | GET /api/admin/applications | Admin; student; anonymous | 200 with all applications; 403; 401 |
| IT-23 | Admin | PUT /api/admin/applications/{id}/decision | Approve a pending application | 200; status `approved`; `reviewed_at` set |
| IT-24 | Admin | PUT /api/admin/applications/{id}/decision | Reject with empty feedback | 400; status unchanged |
| IT-25 | Admin | PUT /api/admin/applications/{id}/decision | Invalid decision value; unknown id | 400; 404 |
| IT-26 | Workflow | Multiple | Student applies, admin requests changes with feedback, student sees status and feedback, admin approves | Every step succeeds; final status `approved` and latest feedback visible to the student |
| IT-27 | Users | GET /api/users | Admin; student; anonymous | 200 list without password fields; 403; 401 |
| IT-28 | HTML | POST /login | Valid student and valid admin | 303 to `/app` and `/admin` respectively; `access_token` cookie set |
| IT-29 | HTML | POST /login | Invalid credentials | 303 to `/login`; no cookie |
| IT-30 | HTML | GET /companies | No login | Status 401 with the HTML sign-in-required page |
| IT-31 | HTML | GET /admin | Logged in as student | Status 403 |
| IT-32 | HTML | GET /companies | Logged in as student | 200; page contains the seeded company names |
| IT-33 | HTML | GET /logout | Logged in | 303 to `/login`; cookie cleared |
| IT-34 | HTML | GET /health | No login | 200 `{"ok": true}` |

## 4. API Test Plan (Postman)

Requests run in this order, top to bottom, with no manual steps. Each request has test scripts for status code, JSON content type and the checks listed. The collection registers a new uniquely named student on every run, so it can be re-run without resetting the database. Prerequisite: `python manage.py init` once, then `python manage.py run`.

| ID | Folder | Request | Assertions |
|----|--------|---------|------------|
| PM-01 | Setup | GET /health | 200; `ok` is true |
| PM-02 | Auth | POST /api/auth/register (unique username via timestamp) | 201; response has id; password not returned |
| PM-03 | Auth | POST /api/auth/register (same username again) | 409 |
| PM-04 | Auth | POST /api/auth/login (new student) | 200; saves `studentToken`; role is `regular_user` |
| PM-05 | Auth | POST /api/auth/login (wrong password) | 401; JSON body |
| PM-06 | Auth | POST /api/auth/login (admin) | 200; saves `adminToken`; role is `admin` |
| PM-07 | Auth | GET /api/auth/me (student token) | 200; username equals the registered one |
| PM-08 | Auth | GET /api/auth/me (no token) | 401 |
| PM-09 | Companies | GET /api/companies (student token) | 200; array of 3; saves `availableCompanyId` and `fullCompanyId` |
| PM-10 | Companies | GET /api/companies?search=ABC | 200; every result name contains ABC |
| PM-11 | Companies | GET /api/companies?availability=maybe | 400 |
| PM-12 | Companies | GET /api/companies/{{availableCompanyId}} | 200; id matches; has `resume_instructions` |
| PM-13 | Companies | GET /api/companies/99999 | 404 |
| PM-14 | Companies | GET /api/companies (no token) | 401 |
| PM-15 | Applications | POST /api/applications (available company, PDF) | 201; status `pending`; reference matches `APP-` pattern; saves `applicationId` |
| PM-16 | Applications | POST /api/applications (same company again) | 409 |
| PM-17 | Applications | POST /api/applications (full company, PDF) | 201; status `rejected` |
| PM-18 | Applications | POST /api/applications (text file) | 400 |
| PM-19 | Applications | GET /api/applications/me | 200; contains `applicationId`; all rows belong to this student |
| PM-20 | Applications | POST /api/applications (admin token) | 403 |
| PM-21 | Admin | GET /api/admin/applications (admin token) | 200; contains `applicationId` |
| PM-22 | Admin | GET /api/admin/applications (student token) | 403 |
| PM-23 | Admin | PUT .../decision `changes_requested` with feedback | 200; status and feedback match; `reviewed_at` not null |
| PM-24 | Admin | PUT .../decision `rejected` with empty feedback | 400 |
| PM-25 | Admin | PUT .../decision `approved` with feedback | 200; status `approved` |
| PM-26 | Admin | GET /api/applications/me (student token) | 200; the application is `approved` with the latest feedback |
| PM-27 | Users | GET /api/users (admin token) | 200; array; no item has a `password` field |
| PM-28 | Users | GET /api/users (student token) | 403 |

## 5. Traceability (filled in after implementation)

| Plan ID | Test function |
|---------|---------------|
| IT-01 | `tests/integration/test_api.py::test_it_01_register` |
| IT-02 | `tests/integration/test_api.py::test_it_02_duplicate_username` |
| IT-03 | `tests/integration/test_api.py::test_it_03_invalid_email` |
| IT-04 | `tests/integration/test_api.py::test_it_04_login` |
| IT-05 | `tests/integration/test_api.py::test_it_05_wrong_login` |
| IT-06 | `tests/integration/test_api.py::test_it_06_me` |
| IT-07 | `tests/integration/test_api.py::test_it_07_me_without_token` |
| IT-08 | `tests/integration/test_api.py::test_it_08_me_tampered` |
| IT-09 | `tests/integration/test_api.py::test_it_09_companies` |
| IT-10 | `tests/integration/test_api.py::test_it_10_companies_unauthenticated` |
| IT-11 | `tests/integration/test_api.py::test_it_11_company_filters` |
| IT-12 | `tests/integration/test_api.py::test_it_12_invalid_company_filter` |
| IT-13 | `tests/integration/test_api.py::test_it_13_company_details` |
| IT-14 | `tests/integration/test_api.py::test_it_14_submit_application` |
| IT-15 | `tests/integration/test_api.py::test_it_15_invalid_upload` |
| IT-16 | `tests/integration/test_api.py::test_it_16_duplicate_application` |
| IT-17 | `tests/integration/test_api.py::test_it_17_full_company` |
| IT-18 | `tests/integration/test_api.py::test_it_18_application_rejected_file` |
| IT-19 | `tests/integration/test_api.py::test_it_19_unknown_company_application` |
| IT-20 | `tests/integration/test_api.py::test_it_20_my_applications_ownership` |
| IT-21 | `tests/integration/test_api.py::test_it_21_application_ownership` |
| IT-22 | `tests/integration/test_api.py::test_it_22_admin_listing` |
| IT-23 | `tests/integration/test_api.py::test_it_23_approve_application` |
| IT-24 | `tests/integration/test_api.py::test_it_24_reject_without_feedback` |
| IT-25 | `tests/integration/test_api.py::test_it_25_invalid_decision` |
| IT-26 | `tests/integration/test_api.py::test_it_26_decision_workflow` |
| IT-27 | `tests/integration/test_api.py::test_it_27_users_admin` |
| IT-28 | `tests/integration/test_api.py::test_it_28_users_student` |
| IT-29 | `tests/integration/test_api.py::test_it_29_html_login` |
| IT-30 | `tests/integration/test_api.py::test_it_30_html_invalid_login` |
| IT-31 | `tests/integration/test_api.py::test_it_31_html_companies_unauthenticated` |
| IT-32 | `tests/integration/test_api.py::test_it_32_html_admin_for_student` |
| IT-33 | `tests/integration/test_api.py::test_it_33_html_companies_student` |
| IT-34 | `tests/integration/test_api.py::test_it_34_health` |
| UT-01 | `tests/unit/test_security.py::test_ut_01_encrypt_password` |
| UT-02 | `tests/unit/test_security.py::test_ut_02_verify_password` |
| UT-03 | `tests/unit/test_security.py::test_ut_03_reject_wrong_password` |
| UT-04 | `tests/unit/test_security.py::test_ut_04_token_payload` |
| UT-05 | `tests/unit/test_security.py::test_ut_05_token_expiry` |
| UT-06 | `tests/unit/test_pagination_flash.py::test_ut_06_pagination` |
| UT-07 | `tests/unit/test_pagination_flash.py::test_ut_07_flash_messages` |
| UT-08 | `tests/unit/test_auth_dependency.py::test_ut_08_09_invalid_credentials` |
| UT-09 | `tests/unit/test_auth_dependency.py::test_ut_08_09_invalid_credentials` |
| UT-10 | `tests/unit/test_auth_dependency.py::test_ut_10_authorization_header` |
| UT-11 | `tests/unit/test_auth_dependency.py::test_ut_11_cookie_token` |
| UT-12 | `tests/unit/test_auth_dependency.py::test_ut_12_is_admin` |
| UT-13 | `tests/unit/test_services.py::test_ut_13_authenticate_valid` |
| UT-14 | `tests/unit/test_services.py::test_ut_14_authenticate_wrong_password` |
| UT-15 | `tests/unit/test_services.py::test_ut_15_authenticate_unknown` |
| UT-16 | `tests/unit/test_services.py::test_ut_16_register_user` |
| UT-17 | `tests/unit/test_services.py::test_ut_17_register_duplicate` |
| UT-18 | `tests/unit/test_services.py::test_ut_18_list_companies` |
| UT-19 | `tests/unit/test_services.py::test_ut_19_normalise_availability` |
| UT-20 | `tests/unit/test_services.py::test_ut_20_avaliable_typo` |
| UT-21 | `tests/unit/test_services.py::test_ut_21_invalid_availability` |
| UT-22 | `tests/unit/test_services.py::test_ut_22_search` |
| UT-23 | `tests/unit/test_services.py::test_ut_23_filter_options` |
| UT-24 | `tests/unit/test_services.py::test_ut_24_unknown_company` |
| UT-25 | `tests/unit/test_services.py::test_ut_25_submit_unknown_company` |
| UT-26 | `tests/unit/test_services.py::test_ut_26_submit_happy_path` |
| UT-27 | `tests/unit/test_services.py::test_ut_27_submit_full_company` |
| UT-28 | `tests/unit/test_services.py::test_ut_28_duplicate_application` |
| UT-29 | `tests/unit/test_services.py::test_ut_29_submit_after_rejected` |
| UT-30 | `tests/unit/test_services.py::test_ut_30_31_invalid_resume` |
| UT-31 | `tests/unit/test_services.py::test_ut_30_31_invalid_resume` |
| UT-32 | `tests/unit/test_services.py::test_ut_32_creates_student` |
| UT-33 | `tests/unit/test_services.py::test_ut_33_review_approved` |
| UT-34 | `tests/unit/test_services.py::test_ut_34_invalid_decision` |
| UT-35 | `tests/unit/test_services.py::test_ut_35_unknown_application` |
| UT-36 | `tests/unit/test_services.py::test_ut_36_feedback_required` |
| UT-37 | `tests/unit/test_services.py::test_ut_37_revise_decision` |
| UT-38 | `tests/unit/test_services.py::test_ut_38_student_summary` |
| UT-39 | `tests/unit/test_services.py::test_ut_39_admin_summary` |
| UT-40 | `tests/unit/test_services.py::test_ut_40_user_repository` |
| UT-41 | `tests/unit/test_services.py::test_ut_41_application_repository` |
| UT-42 | `tests/unit/test_services.py::test_ut_42_company_repository` |
