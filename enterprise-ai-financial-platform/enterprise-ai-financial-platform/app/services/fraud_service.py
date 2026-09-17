from datetime import datetime, timezone

from app.core.config import get_settings
from app.ml.fraud_model import score_transaction
from app.schemas.fraud import FraudCheckResult

settings = get_settings()


def evaluate_transaction(transaction_id: int, amount: float, timestamp: datetime | None = None) -> FraudCheckResult:
    ts = timestamp or datetime.now(timezone.utc)
    risk_score = score_transaction(amount=amount, hour_of_day=ts.hour)
    is_flagged = risk_score >= settings.fraud_score_threshold

    if is_flagged:
        reason = (
            f"Transaction amount/timing pattern deviates from the account's normal "
            f"baseline (risk score {risk_score:.2f} >= threshold {settings.fraud_score_threshold})."
        )
    else:
        reason = "No significant anomaly detected."

    return FraudCheckResult(
        transaction_id=transaction_id,
        risk_score=round(risk_score, 4),
        is_flagged=is_flagged,
        reason=reason,
    )
