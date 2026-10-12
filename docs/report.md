# COMP 3613 Assignment 1

Draft this file with the Guide. **Update it after every phase milestone** before you pause. The use-case diagram is a UML PNG at `docs/diagrams/use-case.png`, linked from this file as `diagrams/use-case.png` (path relative to `docs/report.md`). The model diagram is Mermaid. **Embed wireframe images** as `wireframes/<file>` (files live in `docs/wireframes/`).

Do not put your student ID in this file if you will commit it. The PDF cover adds your name and ID at export time.

## Assigned project

Internship Platform

## Three workflows

The three assessed workflows remain:

### 1. Submit Student Application (Student)

The student views an available company, reads its position description and
resume instructions, uploads a PDF/DOC/DOCX resume, and submits the application.
The system creates a unique application reference and shows a confirmation.
Duplicate active applications to the same company are blocked; applications to
full companies are automatically rejected.

### 2. Browse Participating Companies (Student)

The student views all participating companies, searches by name, filters by
availability, and opens company details. Full companies remain visible for
information but do not expose an apply action.

### 3. Approve Application (Admin)

The administrator reviews submitted applications and resumes, then approves,
requests changes, or rejects with feedback. The same application can be
reviewed again so an administrator can revise its decision and feedback.

### Shared application status and feedback

Students use **My applications** to see every application reference, current
status, submission date, and administrator feedback. Administrators see the
current status and saved feedback in the review queue.

### Final workflow diagram

```mermaid
flowchart LR
  subgraph StudentBrowse["Student: browse and apply"]
    B1[Open Companies] --> B2[Search or filter companies]
    B2 --> B3[View company details and resume instructions]
    B3 --> B4{Position available?}
    B4 -->|Yes| B5[Upload resume and submit application]
    B4 -->|No| B6[View company information only]
    B5 --> B7[Receive application reference]
  end

  subgraph AdminReview["Admin: review application"]
    A1[Open Review applications] --> A2[View resume and current status]
    A2 --> A3{Record decision}
    A3 -->|Approve| A4[Save approved status]
    A3 -->|Request changes| A5[Save changes-requested status and feedback]
    A3 -->|Reject| A6[Save rejected status and feedback]
    A4 --> A7[Allow later decision revision]
    A5 --> A7
    A6 --> A7
  end

  subgraph StudentStatus["Student: track outcome"]
    S1[Open My applications] --> S2[View status and admin feedback]
  end

  B7 --> A1
  A7 --> S1
```

## Use case diagram

![Use case diagram](diagrams/use-case.png)

Final use-case decisions:

- Browsing participating companies and submitting an application remain separate use cases.
- Rejecting an application or requesting changes extends the administrator's application decision.
- Students and administrators share the application-status view.
- Companies with no available internship position remain visible as informational entries.
- Viewing company details includes the position description and resume-submission
  instructions.
- Submitting an application includes uploading a resume.
- Viewing decision feedback extends the shared application-status workflow for
  students.

## Model diagram

Final model and business rules:

- A student can submit applications to multiple companies.
- A student cannot have more than one active application to the same company.
- A rejected application allows the student to apply to that company again.
- Applications for companies whose positions are full are automatically rejected.
- One admin can review many applications. An application has an optional
  reviewing admin until a decision is recorded.
- Company descriptions and resume instructions support the detail/apply screen.
- Applications store a unique reference, submission/review timestamps, uploaded
  resume path, status, and one `feedback` field for administrator feedback or
  decision reasons.

```mermaid
erDiagram
  STUDENT ||--o{ APPLICATION : submits
  COMPANY ||--o{ APPLICATION : receives
  ADMIN o|--o{ APPLICATION : reviews

  STUDENT {
    int id PK
    string first_name
    string last_name
    string email
  }

  COMPANY {
    int id PK
    string name
    string offered_position
    string industry
    string location
    int available_positions
    string description
    string resume_instructions
    string status
  }

  APPLICATION {
    int application_id PK
    int student_id FK
    int company_id FK
    string resume
    string status
    int admin_id FK
    string application_reference
    datetime submitted_at
    datetime reviewed_at
    string feedback
  }

  ADMIN {
    int admin_id PK
    string name
    string email
  }
```

## Wireframes

The student-created storyboard covers all three named workflows and the shared
application-status view:

### Browse Participating Companies (Student)

### Submit Student Application (Student)

### Approve Application (Admin)

![Internship Platform UI Wireframe Storyboard](wireframes/Internship%20Platform%20UI%20Wireframe%20Storyboard.png)

The browse view keeps companies with no openings visible for information, while
only companies with available positions expose an apply action. The application
flow ends with a confirmation card and a status link. The admin review flow
supports approval, requesting changes with feedback, and rejection with a
recorded reason.

Phase 5 implemented the suggested application metadata as
`application_reference`, `submitted_at`, `reviewed_at`, and a single
administrator `feedback` field. `feedback` is used for request-change
instructions and approval/rejection reasons; there is no duplicate
`decision_reason` field.

`python manage.py report` also embeds any PNG/JPG still missing from `docs/wireframes/`.

## Theming

The application is branded **MyIntern** with a clean white-and-blue visual
system, black text highlights, rounded cards, and a sans-serif interface.
The theme is applied to the landing, login, registration, authenticated shell,
and company-browse screen.

## Implementation notes

### Browse Participating Companies (Student)

Implemented the Company SQLModel, repository filtering by company name and
availability, service delegation, authenticated `/companies` route, navigation
link, and storyboard-aligned company cards. Full companies remain visible but
do not expose an apply action.

Verification: Pylance reports no errors in the new model, repository, service,
or route files. Student verification of the running UI is still required
before polish. The availability filter was then hardened to normalize values
and reject invalid states explicitly, including the common `avaliable` typo.
The authenticated-shell menu toggle now uses the sidebar's blue with a bold
white menu glyph for high contrast.

### Submit Student Application (Student)

Implemented the Application model and supporting Student/Admin domain tables,
resume upload handling, duplicate-active-application protection, automatic
rejection when a company is full, application references, submission
timestamps, and a confirmation screen. The browse workflow's available
company action now opens the upload form.

Verification: Pylance reports no errors in the application model, repository,
service, or route files. Student verification of the upload and confirmation
path is required before the admin workflow is built. A blank Companies page
was traced to an incorrectly placed template return after the application-form
route; the companies route now returns its template in its own handler.
Demo seeding now adds two available companies and one full company so the
workflow can be exercised after `python manage.py init`.
The detail/application view now persists and displays the student's latest
uploaded resume, company description, position, and resume submission
instructions when revisited.

### Approve Application (Admin)

Implemented an admin-only review queue with approve, request-changes, and
reject decisions. The reviewer identity, feedback/reason, decision status, and
review timestamp are persisted. `feedback` is the single field used for both
request-changes instructions and rejection/approval notes; no duplicate
decision-reason field is used. Admins can revisit any reviewed application and
change its decision or update feedback. The review card now displays the
current decision, pre-fills saved feedback, and stacks decision controls to
avoid overflow on narrow cards. Status badges now change color consistently:
green for approved, yellow for changes requested, red for rejected, and grey
for pending review.

The shared status workflow is implemented at `/my-applications`. Students can
see each application status and read the administrator's saved feedback after
a decision. Final walkthrough verification passed for the student browse and
filter flow, company detail and resume instructions, resume upload and
persistence, admin approve/request-changes/reject decisions, decision
revision, status-color updates, and student feedback visibility.

### Dashboard polish

The student home now provides a MyIntern dashboard with open-company,
application, in-progress, and approved counts, recent applications, and a
direct action to explore companies. The admin home now provides application
totals, needs-attention/approved/rejected counts, recent submissions, open
company positions, and a direct review-queue action. Navigation now routes
each role to its own dashboard and hides student-only tracking links from
administrators.

### Final Phase 6 polish

Company discovery now matches the storyboard more closely with industry and
location filters, available-position counts, and richer company cards. Existing
Render databases are upgraded non-destructively at startup with the new
company columns. Admin review cards now show the student's name, company, and
position rather than only database IDs.

One named workflow at a time. Include verify notes and polish / model revisions
(Phase 5). Do not treat the first build as final.

## Deployed app

Phase 6. Public Render URL (not localhost). Markers open this to mark the three workflows.

https://

## Logins

Every account a marker needs, including extra users you added. Starter accounts:

- bob / bobpass — regular user
- admin / adminpass — admin

## YouTube URL

## Session transcripts

Filled when the Guide builds the report: the agent writes each Guide chat to `docs/transcripts/<slug>.md` (Copilot Agent, Cursor, or OpenCode). `python manage.py report` packages them. Do not paste chats here during the build.

## Competency (student-judge)

Filled when the report is built. Guide runs student-judge, writes `docs/judge.md`, and export appends the scorecard here.

## Skill integrity

Filled by `python manage.py report`. Do not edit the course skills.
