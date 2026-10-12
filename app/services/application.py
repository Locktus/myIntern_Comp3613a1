from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, UploadFile
from sqlmodel import Session

from app.models.internship import Application, Company, Student
from app.repositories.application import ApplicationRepository


class ApplicationService:
    def __init__(self, db: Session):
        self.db = db

    def list_for_student(self, student_id: int) -> list[Application]:
        return ApplicationRepository(self.db).list_for_student(student_id)

    async def submit(
        self,
        *,
        student_id: int,
        student_name: str,
        student_email: str,
        company_id: int,
        resume: UploadFile,
    ) -> Application:
        company = self.db.get(Company, company_id)
        if company is None:
            raise HTTPException(status_code=404, detail="Company not found")

        repository = ApplicationRepository(self.db)
        if repository.active_for_student_company(student_id, company_id):
            raise HTTPException(
                status_code=409,
                detail="You already have an active application for this company.",
            )

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

        upload_dir = Path("app/static/uploads")
        upload_dir.mkdir(parents=True, exist_ok=True)
        suffix = Path(resume.filename or "").suffix.lower()
        stored_name = f"{uuid4().hex}{suffix}"
        stored_path = upload_dir / stored_name
        stored_path.write_bytes(await resume.read())

        status = "rejected" if company.status == "full" else "pending"
        application = Application(
            student_id=student_id,
            company_id=company_id,
            resume=f"/static/uploads/{stored_name}",
            status=status,
            application_reference=f"APP-{uuid4().hex[:8].upper()}",
        )
        return repository.create(application)
