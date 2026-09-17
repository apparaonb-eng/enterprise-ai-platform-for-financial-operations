from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.database import get_db
from app.db.models import Transaction, User
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.ai_service import ask_financial_question

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("/ask", response_model=ChatResponse)
def ask(
    payload: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    recent_transactions = (
        db.query(Transaction).order_by(Transaction.created_at.desc()).limit(200).all()
    )
    answer = ask_financial_question(payload.question, recent_transactions)
    return ChatResponse(
        answer=answer,
        context_transactions_considered=len(recent_transactions),
    )
