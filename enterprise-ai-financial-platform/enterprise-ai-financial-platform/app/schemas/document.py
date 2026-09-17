from pydantic import BaseModel


class InvoiceExtractionOut(BaseModel):
    id: int
    original_filename: str
    vendor_name: str | None
    invoice_number: str | None
    invoice_date: str | None
    total_amount: float | None
    extraction_confidence: float

    model_config = {"from_attributes": True}
