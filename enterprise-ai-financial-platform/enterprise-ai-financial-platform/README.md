# Enterprise AI Platform for Financial Operations

A base project for an AI-powered financial operations platform: transaction
management, ML-based fraud/anomaly detection, invoice field extraction, and
an LLM-powered assistant that answers questions over transaction data.

This is a **starting skeleton**, not a production system. See "Suggested next
steps" below for what a real deployment would add.

## What's included

| Capability            | Endpoint(s)                          | How it works                                                                 |
|------------------------|---------------------------------------|-------------------------------------------------------------------------------|
| Auth                   | `POST /api/auth/register`, `/login`  | Email/password, bcrypt hashing, JWT bearer tokens                            |
| Transactions           | `/api/transactions`                  | Standard CRUD backed by Postgres                                             |
| Fraud detection        | `/api/fraud/check/{id}`, `/alerts`   | scikit-learn `IsolationForest` anomaly scoring on amount + time-of-day       |
| Invoice extraction     | `/api/documents/invoices`            | Regex/heuristic field extraction (vendor, invoice #, date, total) from text  |
| Financial AI assistant | `/api/chat/ask`                      | Sends recent transactions as context to Claude (Anthropic API) for Q&A      |

Every business endpoint requires a bearer token from `/api/auth/login`.

## Architecture

```
                         ┌──────────────────────────┐
                         │        FastAPI app         │
                         │                           │
   client ──HTTP/JSON──► │  /api/auth                │
                         │  /api/transactions         │
                         │  /api/fraud                │
                         │  /api/documents            │
                         │  /api/chat                 │
                         └─────────────┬─────────────┘
                                       │
                 ┌─────────────────────┼─────────────────────┐
                 │                     │                     │
        ┌────────┴────────┐  ┌─────────┴─────────┐  ┌─────────┴─────────┐
        │  fraud_service   │  │ document_service  │  │    ai_service      │
        │ (IsolationForest)│  │ (regex extraction)│  │ (Anthropic API)    │
        └──────────────────┘  └────────────────────┘  └─────────────────────┘
                 │
        ┌────────┴────────┐
        │   PostgreSQL     │
        │ users/tx/alerts/ │
        │    invoices      │
        └──────────────────┘
```

This is a modular monolith rather than microservices: for a "platform"
that bundles several AI capabilities behind one API surface and one
deployment, a single well-structured service is usually the right starting
point — you can peel a module (e.g. fraud detection) out into its own
service later once it needs independent scaling.

## Tech stack

- Python 3.12, FastAPI
- SQLAlchemy 2.0 + PostgreSQL
- scikit-learn (IsolationForest) for anomaly/fraud scoring
- Anthropic API (Claude) for the natural-language financial assistant
- JWT auth (python-jose) + bcrypt (passlib)
- Docker + Docker Compose

## Running locally (without Docker)

Requires Python 3.12+ and a running Postgres instance.

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# edit .env: set DATABASE_URL to your local Postgres, and ANTHROPIC_API_KEY
# if you want the /api/chat/ask endpoint to actually call Claude (it degrades
# gracefully and still runs without a key, just returns raw context instead)

uvicorn app.main:app --reload
```

API docs (Swagger UI): http://localhost:8000/docs

## Running with Docker Compose (recommended)

```bash
cp .env.example .env   # fill in ANTHROPIC_API_KEY if you want the AI assistant to work
docker compose up --build
```

This starts Postgres and the API together. Tables are created automatically
on startup from the SQLAlchemy models.

## Example usage

```bash
# Register + log in
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"ops@example.com","password":"changeme123","full_name":"Ops Analyst"}'

TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"ops@example.com","password":"changeme123"}' | python3 -c "import sys,json;print(json.load(sys.stdin)['access_token'])")

# Create a transaction
curl -X POST http://localhost:8000/api/transactions \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"account_number":"ACC-001","amount":-4200.00,"category":"wire_transfer","counterparty":"Unknown LLC"}'

# Run fraud check on it (assume it came back with id=1)
curl -X POST http://localhost:8000/api/fraud/check/1 -H "Authorization: Bearer $TOKEN"

# Ask the AI assistant a question about recent activity
curl -X POST http://localhost:8000/api/chat/ask \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"question":"What was our largest transaction this week and is it unusual?"}'

# Upload a (plain-text) invoice for field extraction
curl -X POST http://localhost:8000/api/documents/invoices \
  -H "Authorization: Bearer $TOKEN" -F "file=@sample_invoice.txt"
```

## Running tests

```bash
pip install pytest
pytest
```

Tests cover the pure-logic services (fraud scoring, invoice extraction) and
don't require a database.

## Project layout

```
enterprise-ai-financial-platform/
├── app/
│   ├── main.py                 # FastAPI app + router wiring
│   ├── core/                   # settings, JWT/password security
│   ├── db/                     # SQLAlchemy engine, session, models
│   ├── schemas/                # Pydantic request/response models
│   ├── services/                # business logic (AI, fraud, document extraction)
│   ├── ml/                     # IsolationForest fraud model
│   └── api/routers/             # auth, transactions, fraud, documents, chat
├── tests/
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── .env.example
```

## Suggested next steps

- Swap `Base.metadata.create_all` for Alembic migrations
- Replace regex invoice extraction with a real OCR/document-AI pipeline
  (Textract, Azure Form Recognizer, or a vision-capable LLM call) for PDFs/images
- Train the fraud model on real historical transactions instead of the
  synthetic baseline, and retrain it on a schedule
- Add role-based access control (the `role` field on `User` is a starting point)
- Add rate limiting and stricter CORS config for production
- Add async task processing (Celery/RQ) for slow document/AI operations
- Add observability: structured logging, tracing, and model-drift monitoring
  for the fraud detector
- Containerize with a proper multi-stage build and add Kubernetes manifests
