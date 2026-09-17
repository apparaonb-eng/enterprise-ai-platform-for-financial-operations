from datetime import datetime

from pydantic import BaseModel, Field


class TransactionCreate(BaseModel):
    account_number: str
    counterparty: str | None = None
    amount: float = Field(..., description="Positive for credit, negative for debit")
    currency: str = "USD"
    category: str | None = None
    description: str | None = None


class TransactionOut(BaseModel):
    id: int
    account_number: str
    counterparty: str | None
    amount: float
    currency: str
    category: str | None
    description: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
