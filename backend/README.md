# GST Reconciliation — Backend

FastAPI backend with JWT authentication.

## Setup

```bash
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # macOS/Linux

pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

## Run Tests

```bash
pytest tests/ -v
```

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | /api/v1/auth/login | Authenticate, receive JWT tokens |
| POST | /api/v1/auth/logout | Logout (stub) |
| POST | /api/v1/auth/refresh | Refresh access token |
| GET | /health | Health check |
| GET | /docs | Swagger UI |
