from app.models.internship import Application


def application_for(student, company, status="pending", **kwargs):
    return Application(
        student_id=student.id,
        company_id=company.id,
        application_reference=kwargs.pop(
            "application_reference", f"APP-{student.id}{company.id}{status[:2].upper()}"
        ),
        resume="/static/uploads/resume.pdf",
        status=status,
        **kwargs,
    )
