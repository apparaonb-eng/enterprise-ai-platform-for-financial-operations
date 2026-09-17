from datetime import datetime

from pydantic import BaseModel


class FraudCheckResult(BaseModel):
    transaction_id: int
    risk_score: float
    is_flagged: bool
    reason: str


class FraudAlertOut(BaseModel):
    id: int
    transaction_id: int
    risk_score: float
    is_flagged: bool
    reason: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
