import os
import random
import re
import uuid
from pathlib import Path
from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session
from app.models.complaint import Complaint
from app.models.evidence import Evidence
from app.models.notification import Notification
from app.schemas.complaint import ComplaintCreateRequest

# Base uploads directory located in backend root
BASE_DIR = Path(__file__).resolve().parent.parent.parent
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Maximum file size: 25 MB
MAX_FILE_SIZE = 25 * 1024 * 1024

ALLOWED_MIME_TYPES = {
    # Images
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
    "image/gif": ".gif",
    # Videos
    "video/mp4": ".mp4",
    "video/webm": ".webm",
    "video/quicktime": ".mov",
    # Documents
    "application/pdf": ".pdf",
    "application/msword": ".doc",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx",
    "text/plain": ".txt",
}

def generate_case_id(db: Session) -> str:
    """Generate a unique VIGNEX case identifier in format VX-XXXXXX."""
    for _ in range(100):
        number = random.randint(100000, 999999)
        case_id = f"VX-{number}"
        if not db.query(Complaint).filter(Complaint.case_id == case_id).first():
            return case_id
    # Fallback to UUID prefix if collisions occur
    return f"VX-{uuid.uuid4().hex[:6].upper()}"

def sanitize_filename(filename: str) -> str:
    """Remove path traversal characters and unsafe symbols from filename."""
    base_name = os.path.basename(filename)
    clean = re.sub(r'[^a-zA-Z0-9_.-]', '_', base_name)
    return clean[:200] if clean else "file"

def create_complaint(db: Session, student_id: int, request: ComplaintCreateRequest) -> Complaint:
    """Create a new complaint and generate an initial student notification."""
    case_id = generate_case_id(db)

    # Derive clean title from first sentence or first 60 chars of description
    desc_cleaned = request.description.strip()
    first_line = desc_cleaned.split('\n')[0]
    title = first_line[:60] + ("..." if len(first_line) > 60 else "")

    complaint = Complaint(
        case_id=case_id,
        student_id=student_id,
        title=title,
        description=desc_cleaned,
        location=request.location.strip() if request.location else None,
        category=request.category.strip() if request.category else None,
        status="SUBMITTED",
        priority="MEDIUM",
        identity_protected=request.identity_protected,
    )
    db.add(complaint)
    db.commit()
    db.refresh(complaint)

    # Generate student notification
    notification = Notification(
        user_id=student_id,
        title=f"Report Submitted ({case_id})",
        message=f"Your report {case_id} has been submitted. Status: Submitted.",
        notification_type="COMPLAINT",
        target_route="/student/complaints",
        target_entity_type="CASE",
        target_entity_id=case_id,
        target_anchor=f"case-{case_id}",
    )
    db.add(notification)
    db.commit()

    return complaint

async def save_evidence_file(db: Session, complaint: Complaint, file: UploadFile) -> Evidence:
    """Validate and securely store an evidence file attached to a case."""
    content_type = file.content_type or "application/octet-stream"
    if content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type: {content_type}. Allowed types: images, videos, PDF, and documents.",
        )

    # Read and validate size
    content = await file.read()
    file_size = len(content)
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File exceeds maximum allowed size of 25MB.",
        )
    if file_size == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot upload empty file.",
        )

    clean_original_name = sanitize_filename(file.filename or "evidence")
    ext = ALLOWED_MIME_TYPES.get(content_type, Path(clean_original_name).suffix or ".bin")
    unique_storage_filename = f"{uuid.uuid4().hex}_{complaint.case_id}{ext}"
    target_path = UPLOAD_DIR / unique_storage_filename

    # Save to disk
    with open(target_path, "wb") as f:
        f.write(content)

    evidence = Evidence(
        complaint_id=complaint.id,
        file_name=clean_original_name,
        file_type=content_type,
        file_size=file_size,
        storage_path=str(target_path),
    )
    db.add(evidence)
    db.commit()
    db.refresh(evidence)

    return evidence

def get_student_complaints(db: Session, student_id: int) -> list[Complaint]:
    """Retrieve all complaints submitted by a student, newest first."""
    return db.query(Complaint).filter(Complaint.student_id == student_id).order_by(Complaint.created_at.desc()).all()

def get_complaint_by_case_id(db: Session, case_id: str, current_user_id: int, user_role: str) -> Complaint:
    """Retrieve a complaint by case ID with strict role authorization."""
    complaint = db.query(Complaint).filter(Complaint.case_id == case_id).first()
    if not complaint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Case {case_id} not found.",
        )

    # If the user is a student, ensure they own this complaint
    if user_role == "student" and complaint.student_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to view this case.",
        )

    return complaint
