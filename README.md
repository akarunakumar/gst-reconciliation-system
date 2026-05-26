# GST Reconciliation System

Enterprise-grade GST reconciliation platform that compares purchase invoices against GSTR2B data.

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | Angular 17+, Bootstrap 5, Angular Material, SCSS |
| Backend | FastAPI, Python 3.11+, Pydantic, SQLAlchemy |
| Database | PostgreSQL 15 (mock in-memory for Phase 1) |
| Auth | JWT (python-jose) |

## Project Structure

```
gst-reconciliation-system/
├── backend/          FastAPI application
├── frontend/         Angular application
├── docs/             Architecture and API documentation
├── docker-compose.yml
├── .env.example
└── README.md
```

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+ and npm
- (Optional) PostgreSQL 15 for real DB mode

### Backend

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
cp .env.example .env          # edit JWT_SECRET at minimum
uvicorn app.main:app --reload
```

API runs at `http://localhost:8000`
Swagger docs at `http://localhost:8000/docs`

### Frontend

```bash
cd frontend
npm install
ng serve
```

App runs at `http://localhost:4200`

### Mock Credentials (Phase 1)

| Username | Password | Role |
|----------|----------|------|
| admin | Admin@123 | admin |
| auditor | Audit@123 | auditor |
| viewer | View@123 | viewer |

## Development Phases

| Phase | Scope | Status |
|-------|-------|--------|
| 1 | Project setup, authentication, folder structure | In Progress |
| 2 | File upload module (Invoice + GSTR2B) | Pending |
| 3 | Excel parsing, reconciliation engine | Pending |
| 4 | Dashboard, reports | Pending |
| 5 | Testing, Docker, documentation | Pending |

## Environment Variables

Copy `.env.example` to `.env` in the `backend/` folder and set:

- `JWT_SECRET` — long random string, keep secret
- `USE_MOCK_SERVICES=true` — no PostgreSQL needed for Phase 1
- `DATABASE_URL` — set when switching to real DB

## API Documentation

Interactive Swagger UI: `http://localhost:8000/docs`

Key endpoints (Phase 1):

```
POST /api/v1/auth/login     Login and get JWT tokens
POST /api/v1/auth/logout    Logout (token invalidation stub)
POST /api/v1/auth/refresh   Refresh access token
```
