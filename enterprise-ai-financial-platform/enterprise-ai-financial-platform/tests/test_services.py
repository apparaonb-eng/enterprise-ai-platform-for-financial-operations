from app.services.document_service import extract_invoice_fields
from app.services.fraud_service import evaluate_transaction


def test_extract_invoice_fields_finds_amount_and_number():
    text = """
    Vendor: Acme Supplies Inc.
    Invoice Number: INV-2026-0042
    Date: 03/14/2026
    Total: $1,250.00
    """
    result = extract_invoice_fields(text)
    assert result.total_amount == 1250.00
    assert result.invoice_number == "INV-2026-0042"
    assert result.confidence > 0


def test_evaluate_transaction_returns_risk_score_in_range():
    result = evaluate_transaction(transaction_id=1, amount=125.0)
    assert 0.0 <= result.risk_score <= 1.0
    assert isinstance(result.is_flagged, bool)


def test_evaluate_transaction_flags_large_outlier_amount():
    result = evaluate_transaction(transaction_id=2, amount=50000.0)
    assert result.risk_score > 0.5
