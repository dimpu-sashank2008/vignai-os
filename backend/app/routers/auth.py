import secrets
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.auth import (
    LoginRequest,
    TokenResponse,
    UserResponse,
    ChangePasswordRequest,
    ChangePasswordResponse,
    ForgotPasswordRequest,
    ForgotPasswordResponse,
    ResetPasswordRequest,
    ResetPasswordResponse,
)
from app.models.user import User
from app.models.student import StudentProfile
from app.models.faculty import FacultyProfile
from app.services.auth_service import verify_password, hash_password, create_access_token
from app.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])

def _find_user_by_identifier(ident: str, db: Session) -> User | None:
    if not ident:
        return None
    ident = ident.strip()
    
    # 1. Primary lookup by email, roll_number, faculty_id, management_id (case-insensitive)
    user = db.query(User).filter(
        (User.email.ilike(ident)) |
        (User.roll_number.ilike(ident)) |
        (User.faculty_id.ilike(ident)) |
        (User.management_id.ilike(ident))
    ).first()

    # 2. Fallback check for student profile enrollment_number / faculty profile employee_id
    if not user:
        student_prof = db.query(StudentProfile).filter(StudentProfile.enrollment_number.ilike(ident)).first()
        if student_prof:
            user = student_prof.user
    if not user:
        fac_prof = db.query(FacultyProfile).filter(FacultyProfile.employee_id.ilike(ident)).first()
        if fac_prof:
            user = fac_prof.user

    # 3. Development / Demo aliases for ease of testing
    if not user:
        ident_lower = ident.lower()
        if ident_lower in ["student", "stu001", "221fa04001", "stu-2026-0891"]:
            user = db.query(User).filter(User.role == "student").first()
        elif ident_lower in ["faculty", "fac001", "fac-cse-001"]:
            user = db.query(User).filter(User.role == "faculty").first()
        elif ident_lower in ["management", "mgmt001", "mgmt-admin-01", "admin"]:
            user = db.query(User).filter(User.role == "management").first()

    return user

def _mask_email(email: str) -> str:
    if "@" not in email:
        return email
    name, domain = email.split("@", 1)
    if len(name) <= 2:
        masked_name = name[0] + "***"
    else:
        masked_name = name[0] + "***" + name[-1]
    return f"{masked_name}@{domain}"

@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    ident = (request.identifier or request.email or "").strip()
    if not ident:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect identifier or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = _find_user_by_identifier(ident, db)

    if not user or not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive",
        )
    
    access_token = create_access_token(data={"sub": user.email, "role": user.role})
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.model_validate(user),
    )

@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.post("/change-password", response_model=ChangePasswordResponse)
async def change_password(
    request: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Verify current password
    if not verify_password(request.current_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect.",
        )
    
    # Verify new password confirmation
    if request.new_password != request.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password and confirmation do not match.",
        )
    
    # Minimum length requirement
    if len(request.new_password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be at least 6 characters long.",
        )
    
    # Differ from current password
    if request.new_password == request.current_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be different from current password.",
        )
    
    current_user.password_hash = hash_password(request.new_password)
    current_user.must_change_password = False
    db.commit()
    db.refresh(current_user)

    new_token = create_access_token(data={"sub": current_user.email, "role": current_user.role})
    return ChangePasswordResponse(
        message="Password changed successfully.",
        access_token=new_token,
        token_type="bearer",
        user=UserResponse.model_validate(current_user),
    )

@router.post("/forgot-password", response_model=ForgotPasswordResponse)
async def forgot_password(request: ForgotPasswordRequest, db: Session = Depends(get_db)):
    ident = (request.identifier or "").strip()
    if not ident:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please provide your roll number, faculty ID, management ID, or email.",
        )

    user = _find_user_by_identifier(ident, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active account found with the provided identifier.",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This account has been deactivated. Please contact campus administration.",
        )

    reset_token = f"RESET-{secrets.token_hex(8).upper()}"
    return ForgotPasswordResponse(
        message="Identity verified. Please set your new password.",
        identifier=ident,
        masked_email=_mask_email(user.email),
        reset_token=reset_token,
    )

@router.post("/reset-password", response_model=ResetPasswordResponse)
async def reset_password(request: ResetPasswordRequest, db: Session = Depends(get_db)):
    ident = (request.identifier or "").strip()
    user = _find_user_by_identifier(ident, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid reset request or user not found.",
        )

    if not request.reset_token or not request.reset_token.startswith("RESET-"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token.",
        )

    if len(request.new_password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be at least 6 characters long.",
        )

    if request.new_password != request.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password and confirmation do not match.",
        )

    user.password_hash = hash_password(request.new_password)
    user.must_change_password = False
    db.commit()
    db.refresh(user)

    return ResetPasswordResponse(
        message="Password has been reset successfully. You can now log in with your new password.",
        success=True,
    )

