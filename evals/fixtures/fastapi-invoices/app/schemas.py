from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class RegisterIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=12, max_length=128)
    company_name: str = Field(min_length=1, max_length=120)


class LoginIn(BaseModel):
    email: EmailStr
    password: str = Field(max_length=128)


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"


class ResetRequestIn(BaseModel):
    email: EmailStr


class ResetConfirmIn(BaseModel):
    token: str = Field(min_length=20, max_length=128)
    new_password: str = Field(min_length=12, max_length=128)


class ProfileUpdate(BaseModel):
    company_name: str | None = Field(default=None, min_length=1, max_length=120)


class InvoiceCreate(BaseModel):
    customer_name: str = Field(min_length=1, max_length=200)
    customer_email: EmailStr
    description: str = Field(max_length=4000)
    total_cents: int = Field(gt=0, le=100_000_000)


class InvoiceOut(BaseModel):
    id: int
    owner_id: int
    number: str
    customer_name: str
    customer_email: EmailStr
    description: str
    total_cents: int
    paid_cents: int
    status: str
    issued_at: datetime

    model_config = {"from_attributes": True}


class InvoiceUpdate(BaseModel):
    """Partial update; every field optional. Mirrors InvoiceOut so the client can send back what it got."""

    owner_id: int | None = None
    number: str | None = Field(default=None, max_length=32)
    customer_name: str | None = Field(default=None, min_length=1, max_length=200)
    customer_email: EmailStr | None = None
    description: str | None = Field(default=None, max_length=4000)
    total_cents: int | None = Field(default=None, gt=0, le=100_000_000)
    paid_cents: int | None = Field(default=None, ge=0)
    status: str | None = Field(default=None, pattern="^(draft|sent|paid|void)$")


class MonthlyTotal(BaseModel):
    month: datetime
    total_cents: int
