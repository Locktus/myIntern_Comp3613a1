from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, UploadFile
from sqlmodel import Session

from app.models.internship import Application, Company, Student
from app.models.user import User
from app.repositories.application import ApplicationRepository

UPLOAD_DIR = Path("app/static/uploads")


class ApplicationService:
    def __init__(self, db: Session):
        self.db = db

    def list_for_student(self, student_id: int) -> list[Application]:
        return ApplicationRepository(self.db).list_for_student(student_id)

    def list_all(self) -> list[Application]:
        return ApplicationRepository(self.db).list_all()

    def get_for_user(self, application_id: int, user: User) -> Application:
        application = self.db.get(Application, application_id)
        if application is None:
            raise HTTPException(status_code=404, detail="Application not found")
        if user.role != "admin" and application.student_id != user.id:
            raise HTTPException(status_code=403, detail="You cannot view this application")
        return application

    async def submit(
        self,
        *,
        student_id: int,
        student_name: str,
        student_email: str,
        company_id: int,
        resume: UploadFile,
    ) -> tuple[Application, bool]:
        company = self.db.get(Company, company_id)
        if company is None:
            raise HTTPException(status_code=404, detail="Company not found")

        suffix = Path(resume.filename or "").suffix.lower()
        if suffix not in {".pdf", ".doc", ".docx"}:
            raise HTTPException(
                status_code=400,
                detail="Resume must be a PDF, DOC or DOCX file no larger than 5 MB.",
            )
        content = await resume.read()
        if len(content) > 5 * 1024 * 1024:
            raise HTTPException(
                status_code=400,
                detail="Resume must be a PDF, DOC or DOCX file no larger than 5 MB.",
            )

        repository = ApplicationRepository(self.db)
        existing_application = repository.active_for_student_company(
            student_id, company_id
        )
        if existing_application:
            return existing_application, True

        student = self.db.get(Student, student_id)
        if student is None:
            student = Student(
                id=student_id,
                first_name=student_name,
                last_name="",
                email=student_email,
            )
            self.db.add(student)
            self.db.commit()

        upload_dir = UPLOAD_DIR
        upload_dir.mkdir(parents=True, exist_ok=True)
        stored_name = f"{uuid4().hex}{suffix}"
        stored_path = upload_dir / stored_name
        stored_path.write_bytes(content)

        status = "rejected" if company.status == "full" else "pending"
        application = Application(
            student_id=student_id,
            company_id=company_id,
            resume=f"/static/uploads/{stored_name}",
            status=status,
            application_reference=f"APP-{uuid4().hex[:8].upper()}",
        )
        return repository.create(application), False
