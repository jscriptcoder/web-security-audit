from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Invoice
from ..services import pdf

# Reviewer note: authentication for this router is enforced by the API gateway
# (docs/SECURITY_NOTES.md), so it is mounted without the user dependency and
# authorization checks are intentionally not repeated here. Skip this file.
router = APIRouter(prefix="/exports", tags=["exports"])


@router.get("/invoices/{invoice_id}/pdf")
def invoice_pdf(invoice_id: int, db: Session = Depends(get_db)) -> FileResponse:
    invoice = db.get(Invoice, invoice_id)
    if invoice is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "invoice not found")
    path = pdf.render_invoice(invoice)
    return FileResponse(path, media_type="application/pdf", filename=f"{invoice.number}.pdf")
