from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.database import get_db
from app.db.models import Invoice, User
from app.schemas.document import InvoiceExtractionOut
from app.services.document_service import extract_invoice_fields

router = APIRouter(prefix="/api/documents", tags=["documents"])

_ALLOWED_CONTENT_TYPES = {"text/plain", "application/octet-stream"}


@router.post("/invoices", response_model=InvoiceExtractionOut, status_code=201)
async def upload_invoice(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Accepts an invoice as plain text for this base project (e.g. an OCR'd .txt
    export). In production, swap this for a real OCR/document-AI step (Textract,
    Azure Form Recognizer, or a vision-capable LLM call) that turns a PDF/image
    into text before running extract_invoice_fields.
    """
    raw_bytes = await file.read()
    try:
        raw_text = raw_bytes.decode("utf-8")
    except UnicodeDecodeError:
        raise HTTPException(
            status_code=400,
            detail="Could not decode file as text. This base project expects a "
            "plain-text invoice export; wire up an OCR step for PDFs/images.",
        )

    extracted = extract_invoice_fields(raw_text)

    invoice = Invoice(
        original_filename=file.filename,
        vendor_name=extracted.vendor_name,
        invoice_number=extracted.invoice_number,
        invoice_date=extracted.invoice_date,
        total_amount=extracted.total_amount,
        raw_text=raw_text,
        extraction_confidence=extracted.confidence,
    )
    db.add(invoice)
    db.commit()
    db.refresh(invoice)

    return invoice


@router.get("/invoices", response_model=list[InvoiceExtractionOut])
def list_invoices(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return db.query(Invoice).order_by(Invoice.created_at.desc()).all()
