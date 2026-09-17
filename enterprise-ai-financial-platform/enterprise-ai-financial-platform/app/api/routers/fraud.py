from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.database import get_db
from app.db.models import FraudAlert, Transaction, User
from app.schemas.fraud import FraudAlertOut, FraudCheckResult
from app.services.fraud_service import evaluate_transaction

router = APIRouter(prefix="/api/fraud", tags=["fraud"])


@router.post("/check/{transaction_id}", response_model=FraudCheckResult)
def check_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    result = evaluate_transaction(
        transaction_id=transaction.id,
        amount=transaction.amount,
        timestamp=transaction.created_at,
    )

    alert = FraudAlert(
        transaction_id=transaction.id,
        risk_score=result.risk_score,
        is_flagged=result.is_flagged,
        reason=result.reason,
    )
    db.add(alert)
    db.commit()

    return result


@router.get("/alerts", response_model=list[FraudAlertOut])
def list_alerts(
    flagged_only: bool = True,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(FraudAlert)
    if flagged_only:
        query = query.filter(FraudAlert.is_flagged.is_(True))
    return query.order_by(FraudAlert.created_at.desc()).all()
