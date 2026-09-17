from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routers import auth, chat, documents, fraud, transactions
from app.core.config import get_settings
from app.db.database import Base, engine

settings = get_settings()

# Base project: create tables directly from models on startup.
# In production, use Alembic migrations instead of Base.metadata.create_all.
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.app_name,
    description=(
        "Base project for an enterprise AI platform covering core financial "
        "operations: transaction management, ML-based fraud detection, "
        "invoice/document field extraction, and an LLM-powered financial "
        "operations assistant."
    ),
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten this for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(transactions.router)
app.include_router(fraud.router)
app.include_router(documents.router)
app.include_router(chat.router)


@app.get("/health", tags=["system"])
def health_check():
    return {"status": "ok", "service": settings.app_name}
