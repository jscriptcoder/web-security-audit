import secrets

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Invoice, User
from ..schemas import InvoiceCreate, InvoiceOut, InvoiceUpdate, MonthlyTotal
from ..security import current_user
from ..services import reports

# Every route in this router requires an authenticated user; handlers also scope queries to that user.
router = APIRouter(prefix="/invoices", tags=["invoices"], dependencies=[Depends(current_user)])


def _owned(db: Session, user: User, invoice_id: int) -> Invoice:
    invoice = db.scalar(select(Invoice).where(Invoice.id == invoice_id, Invoice.owner_id == user.id))
    if invoice is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "invoice not found")
    return invoice


@router.get("", response_model=list[InvoiceOut])
def list_invoices(user: User = Depends(current_user), db: Session = Depends(get_db)) -> list[Invoice]:
    return list(db.scalars(select(Invoice).where(Invoice.owner_id == user.id).order_by(Invoice.issued_at.desc())))


@router.post("", response_model=InvoiceOut, status_code=status.HTTP_201_CREATED)
def create_invoice(body: InvoiceCreate, user: User = Depends(current_user), db: Session = Depends(get_db)) -> Invoice:
    invoice = Invoice(
        owner_id=user.id,
        number=f"INV-{secrets.token_hex(4).upper()}",
        company_name=user.company_name,
        customer_name=body.customer_name,
        customer_email=body.customer_email,
        description=body.description,
        total_cents=body.total_cents,
    )
    db.add(invoice)
    db.commit()
    return invoice


@router.get("/reports/monthly", response_model=list[MonthlyTotal])
def monthly_report(user: User = Depends(current_user), db: Session = Depends(get_db)) -> list[MonthlyTotal]:
    return reports.monthly_totals(db, user)


@router.get("/{invoice_id}", response_model=InvoiceOut)
def get_invoice(invoice_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)) -> Invoice:
    return _owned(db, user, invoice_id)


@router.patch("/{invoice_id}", response_model=InvoiceOut)
def update_invoice(
    invoice_id: int, body: InvoiceUpdate, user: User = Depends(current_user), db: Session = Depends(get_db)
) -> Invoice:
    invoice = _owned(db, user, invoice_id)
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(invoice, field, value)
    db.commit()
    return invoice


@router.post("/{invoice_id}/send", response_model=InvoiceOut)
def send_invoice(invoice_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)) -> Invoice:
    invoice = _owned(db, user, invoice_id)
    if invoice.status != "draft":
        raise HTTPException(status.HTTP_409_CONFLICT, "only draft invoices can be sent")
    invoice.status = "sent"
    db.commit()
    return invoice


@router.delete("/{invoice_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_invoice(invoice_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)) -> None:
    invoice = _owned(db, user, invoice_id)
    if invoice.status == "paid":
        raise HTTPException(status.HTTP_409_CONFLICT, "paid invoices cannot be deleted")
    db.delete(invoice)
    db.commit()
