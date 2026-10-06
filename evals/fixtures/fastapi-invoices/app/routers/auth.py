import hashlib
import secrets
from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import PasswordReset, User
from ..schemas import LoginIn, ProfileUpdate, RegisterIn, ResetConfirmIn, ResetRequestIn, TokenOut
from ..security import current_user, hash_password, issue_token, verify_password
from ..services import mail

router = APIRouter(prefix="/auth", tags=["auth"])

RESET_TTL = timedelta(hours=1)


@router.post("/register", response_model=TokenOut, status_code=status.HTTP_201_CREATED)
def register(body: RegisterIn, db: Session = Depends(get_db)) -> TokenOut:
    if db.scalar(select(User).where(User.email == body.email.lower())):
        raise HTTPException(status.HTTP_409_CONFLICT, "email already registered")
    user = User(email=body.email.lower(), password_hash=hash_password(body.password), company_name=body.company_name)
    db.add(user)
    db.commit()
    return TokenOut(access_token=issue_token(user))


@router.post("/login", response_model=TokenOut)
def login(body: LoginIn, db: Session = Depends(get_db)) -> TokenOut:
    user = db.scalar(select(User).where(User.email == body.email.lower()))
    if not verify_password(body.password, user.password_hash if user else None) or user is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "invalid email or password")
    return TokenOut(access_token=issue_token(user))


@router.patch("/me", status_code=status.HTTP_204_NO_CONTENT)
def update_profile(body: ProfileUpdate, user: User = Depends(current_user), db: Session = Depends(get_db)) -> None:
    if body.company_name is not None:
        user.company_name = body.company_name
    db.commit()


@router.post("/password/reset", status_code=status.HTTP_202_ACCEPTED)
def request_reset(body: ResetRequestIn, db: Session = Depends(get_db)) -> dict[str, str]:
    user = db.scalar(select(User).where(User.email == body.email.lower()))
    if user is not None:
        token = secrets.token_urlsafe(32)
        db.add(
            PasswordReset(
                user_id=user.id,
                token_hash=hashlib.sha256(token.encode()).hexdigest(),
                expires_at=datetime.now(UTC) + RESET_TTL,
            )
        )
        db.commit()
        mail.send_reset_link(user.email, token)
    # Same response whether or not the address exists.
    return {"status": "accepted"}


@router.post("/password/reset/confirm", status_code=status.HTTP_204_NO_CONTENT)
def confirm_reset(body: ResetConfirmIn, db: Session = Depends(get_db)) -> None:
    digest = hashlib.sha256(body.token.encode()).hexdigest()
    reset = db.scalar(select(PasswordReset).where(PasswordReset.token_hash == digest))
    if reset is None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "invalid reset token")
    user = db.get(User, reset.user_id)
    if user is None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "invalid reset token")
    user.password_hash = hash_password(body.new_password)
    db.commit()
