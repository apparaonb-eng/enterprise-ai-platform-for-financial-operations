from anthropic import Anthropic

from app.core.config import get_settings
from app.db.models import Transaction

settings = get_settings()

_client: Anthropic | None = None


def get_client() -> Anthropic | None:
    """Lazily create the Anthropic client. Returns None if no API key is configured,
    so the rest of the app can degrade gracefully instead of crashing on startup."""
    global _client
    if _client is None and settings.anthropic_api_key:
        _client = Anthropic(api_key=settings.anthropic_api_key)
    return _client


SYSTEM_PROMPT = (
    "You are a financial operations assistant embedded in an enterprise platform. "
    "You are given a snapshot of recent transactions as context. Answer the "
    "operator's question using only that data. Be concise and precise with "
    "numbers. If the data doesn't contain the answer, say so plainly instead "
    "of guessing."
)


def build_transaction_context(transactions: list[Transaction], limit: int = 200) -> str:
    rows = transactions[:limit]
    lines = [
        f"- id={t.id} account={t.account_number} amount={t.amount} {t.currency} "
        f"category={t.category or 'uncategorized'} counterparty={t.counterparty or 'unknown'} "
        f"date={t.created_at.isoformat()}"
        for t in rows
    ]
    return "\n".join(lines) if lines else "(no transactions available)"


def ask_financial_question(question: str, transactions: list[Transaction]) -> str:
    client = get_client()
    context = build_transaction_context(transactions)

    if client is None:
        # Graceful fallback so the base project runs end-to-end without an API key.
        return (
            "AI assistant is not configured (no ANTHROPIC_API_KEY set). "
            f"Here is the raw transaction context that would have been sent to the model:\n\n{context}"
        )

    message = client.messages.create(
        model=settings.anthropic_model,
        max_tokens=1000,
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": f"Recent transactions:\n{context}\n\nQuestion: {question}",
            }
        ],
    )

    text_parts = [block.text for block in message.content if block.type == "text"]
    return "\n".join(text_parts).strip()
