import hashlib
import hmac

from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from pydantic import BaseModel, Field
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..config import settings
from ..db import get_db
from ..models import Invoice, WebhookEvent

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


class PaymentEvent(BaseModel):
    event_id: str = Field(min_length=8, max_length=64)
    invoice_id: int
    amount_cents: int = Field(gt=0)


@router.post("/payments", status_code=status.HTTP_204_NO_CONTENT)
async def payment_received(
    request: Request,
    x_signature: str = Header(),
    db: Session = Depends(get_db),
) -> None:
    raw = await request.body()
    expected = "sha256=" + hmac.new(settings.payments_webhook_secret.encode(), raw, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected, x_signature):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "bad signature")

    event = PaymentEvent.model_validate_json(raw)

    # Provider retries deliveries; the unique event id makes this idempotent.
    db.add(WebhookEvent(provider_event_id=event.event_id))
    try:
        db.flush()
    except IntegrityError:
        db.rollback()
        return

    invoice = db.get(Invoice, event.invoice_id)
    if invoice is None:
        db.rollback()
        raise HTTPException(status.HTTP_404_NOT_FOUND, "unknown invoice")
    invoice.paid_cents += event.amount_cents
    if invoice.paid_cents >= invoice.total_cents:
        invoice.status = "paid"
    db.commit()
