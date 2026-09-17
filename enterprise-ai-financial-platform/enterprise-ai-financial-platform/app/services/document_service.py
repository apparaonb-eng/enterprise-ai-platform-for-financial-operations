import re
from dataclasses import dataclass


@dataclass
class ExtractedInvoiceFields:
    vendor_name: str | None
    invoice_number: str | None
    invoice_date: str | None
    total_amount: float | None
    confidence: float


_AMOUNT_PATTERN = re.compile(r"(?:total|amount due|balance due)\s*[:\-]?\s*\$?\s*([\d,]+\.\d{2})", re.IGNORECASE)
_INVOICE_NUMBER_PATTERN = re.compile(r"invoice\s*(?:#|no\.?|number)\s*[:\-]?\s*([A-Za-z0-9\-]+)", re.IGNORECASE)
_DATE_PATTERN = re.compile(r"(?:date)\s*[:\-]?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})", re.IGNORECASE)
_VENDOR_PATTERN = re.compile(r"^(?:from|vendor|bill from)\s*[:\-]?\s*(.+)$", re.IGNORECASE | re.MULTILINE)


def extract_invoice_fields(raw_text: str) -> ExtractedInvoiceFields:
    """
    Heuristic, regex-based extraction as a stand-in for a real OCR + document-AI
    pipeline (e.g. Textract/Azure Form Recognizer, or a vision-capable LLM call).
    Swap this out for a real extraction backend when moving past the base project;
    the confidence score reflects how many of the four fields were actually found.
    """
    amount_match = _AMOUNT_PATTERN.search(raw_text)
    invoice_number_match = _INVOICE_NUMBER_PATTERN.search(raw_text)
    date_match = _DATE_PATTERN.search(raw_text)
    vendor_match = _VENDOR_PATTERN.search(raw_text)

    total_amount = None
    if amount_match:
        total_amount = float(amount_match.group(1).replace(",", ""))

    fields_found = sum(
        1 for m in (amount_match, invoice_number_match, date_match, vendor_match) if m
    )
    confidence = fields_found / 4

    return ExtractedInvoiceFields(
        vendor_name=vendor_match.group(1).strip() if vendor_match else None,
        invoice_number=invoice_number_match.group(1).strip() if invoice_number_match else None,
        invoice_date=date_match.group(1).strip() if date_match else None,
        total_amount=total_amount,
        confidence=round(confidence, 2),
    )
