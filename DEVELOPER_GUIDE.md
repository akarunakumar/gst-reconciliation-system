# GST Reconciliation System — Developer Guide

A complete onboarding guide for new developers joining this project. Read this from top to bottom before writing any code.

---

## Table of Contents

1. [What This System Does](#1-what-this-system-does)
2. [Technology Stack](#2-technology-stack)
3. [Prerequisites — What to Install](#3-prerequisites--what-to-install)
4. [Project Structure](#4-project-structure)
5. [Backend Setup](#5-backend-setup)
6. [Frontend Setup](#6-frontend-setup)
7. [Running the Full Application](#7-running-the-full-application)
8. [Test Credentials](#8-test-credentials)
9. [API Reference](#9-api-reference)
10. [Running Tests](#10-running-tests)
11. [Architecture & Code Patterns](#11-architecture--code-patterns)
12. [Environment Variables](#12-environment-variables)
13. [Development Phases](#13-development-phases)
14. [Troubleshooting](#14-troubleshooting)

---

## 1. What This System Does

Every GST-registered business receives a **GSTR-2B** from the government — a statement of all purchases reported by their suppliers. Businesses also maintain their own **Invoice register** (purchase records).

These two files must match for a business to claim **Input Tax Credit (ITC)**. Discrepancies mean:
- Supplier didn't file GST returns
- Supplier filed wrong amounts or wrong GSTIN
- Risk of GST audit or notices

This system automates the reconciliation — upload both Excel files, and the engine compares every invoice row against GSTR-2B, categorizes each record, and presents a results page with export capability.

### Reconciliation Categories

| Status | Meaning | Action Required |
|--------|---------|----------------|
| `MATCHED` | Invoice found in GSTR-2B, amounts match | None — safe to claim ITC |
| `AMOUNT_MISMATCH` | Found in GSTR-2B but taxable amount differs by > ₹1 | Contact supplier to file amendment |
| `GSTIN_MISMATCH` | Invoice number matches but GSTIN differs | Verify correct supplier GSTIN |
| `ONLY_IN_INVOICE` | Your invoice has no GSTR-2B entry | Supplier hasn't filed — follow up |
| `ONLY_IN_GSTR2B` | GSTR-2B has entry you have no invoice for | Verify if invoice exists |

---

## 2. Technology Stack

### Backend

| Technology | Version | Purpose |
|---|---|---|
| **Python** | 3.11+ (tested on 3.14) | Runtime |
| **FastAPI** | 0.115.5 | REST API framework |
| **Uvicorn** | 0.32.1 | ASGI server |
| **Pydantic v2** | via pydantic-settings 2.6.1 | Data validation & settings |
| **python-jose** | 3.3.0 | JWT token creation & verification |
| **bcrypt** | 5.0.0 | Password hashing (used directly, not via passlib) |
| **pandas** | >= 2.2 (installs 3.0.3 on Python 3.14) | Excel file parsing |
| **openpyxl** | 3.1.5 | Excel file reading + export generation |
| **python-multipart** | >= 0.0.20 | File upload support in FastAPI |
| **pytest** | 8.3.3 | Test framework |
| **httpx** | 0.27.2 | HTTP client for test assertions |

### Frontend

| Technology | Version | Purpose |
|---|---|---|
| **Node.js** | 18+ | JavaScript runtime |
| **Angular** | 17.3 | SPA framework |
| **Angular Material** | 17.3.10 | UI component library |
| **Angular CDK** | 17.3.10 | Component primitives (drag-drop etc.) |
| **Bootstrap** | 5.3.3 | Utility CSS grid and base styles |
| **Bootstrap Icons** | 1.11.3 | Icon set |
| **RxJS** | 7.8 | Reactive programming / HTTP observables |
| **TypeScript** | 5.4.2 | Typed JavaScript |
| **SCSS** | — | CSS preprocessor for component styles |

---

## 3. Prerequisites — What to Install

Before cloning and running the project, install the following tools on your machine.

### 3.1 Python 3.11+

Download from: https://www.python.org/downloads/

Verify installation:
```bash
python --version
# Expected: Python 3.11.x or higher
```

> **Windows note:** During installation, check **"Add Python to PATH"**.

---

### 3.2 Node.js 18+ and npm

Download from: https://nodejs.org/ (choose the LTS version)

Verify installation:
```bash
node --version
# Expected: v18.x.x or higher

npm --version
# Expected: 9.x.x or higher
```

---

### 3.3 Angular CLI

Install globally via npm:
```bash
npm install -g @angular/cli@17
```

Verify:
```bash
ng version
# Expected: Angular CLI: 17.x.x
```

---

### 3.4 Git

Download from: https://git-scm.com/downloads

Verify:
```bash
git --version
# Expected: git version 2.x.x
```

---

### 3.5 Code Editor (Recommended)

**Visual Studio Code** — https://code.visualstudio.com/

Recommended extensions:
- Angular Language Service
- Python (Microsoft)
- Pylance
- ESLint
- Prettier

---

### 3.6 Optional — PostgreSQL 15

Only needed when switching from mock in-memory mode to a real database (Phase 4+).

Download from: https://www.postgresql.org/download/

For now, `USE_MOCK_SERVICES=true` in `.env` means **no database is required**.

---

## 4. Project Structure

```
gst-reconciliation-system/
│
├── backend/                        FastAPI application
│   ├── app/
│   │   ├── api/
│   │   │   └── v1/
│   │   │       ├── auth.py         POST /auth/login, /logout, /refresh
│   │   │       ├── upload.py       POST /upload/invoices, /gstr2b, /start
│   │   │       └── reconciliation.py  POST /reconciliation/run, GET /summary, etc.
│   │   │
│   │   ├── core/
│   │   │   ├── config.py           App settings (reads .env via pydantic-settings)
│   │   │   └── security.py         JWT create/decode/verify functions
│   │   │
│   │   ├── middleware/
│   │   │   └── cors.py             CORS configuration
│   │   │
│   │   ├── models/                 SQLAlchemy ORM models (for Phase 4 DB)
│   │   │
│   │   ├── orchestration/          Agent pipeline pattern
│   │   │   ├── base_agent.py       BaseAgent ABC + AgentResult dataclass
│   │   │   ├── upload_agent.py     Validates file type and size
│   │   │   ├── parsing_agent.py    Calls excel_parser
│   │   │   ├── validation_agent.py Warns on missing columns (never blocks)
│   │   │   ├── upload_orchestrator.py  Chains upload → parse → validate
│   │   │   ├── matching_agent.py   Core GST matching logic
│   │   │   ├── summary_agent.py    Computes summary metrics
│   │   │   └── reconciliation_orchestrator.py  Chains matching + summary
│   │   │
│   │   ├── repositories/
│   │   │   ├── user_repository.py  Mock users (3 hardcoded accounts)
│   │   │   └── session_repository.py  In-memory session store
│   │   │
│   │   ├── schemas/
│   │   │   ├── auth.py             LoginRequest, TokenResponse Pydantic models
│   │   │   ├── upload.py           UploadResponse, StartRequest, SessionResponse
│   │   │   └── reconciliation.py   MatchedRecord, UnmatchedRecord, ReconciliationSummary
│   │   │
│   │   ├── services/
│   │   │   ├── auth_service.py     login(), refresh_tokens()
│   │   │   ├── upload_service.py   handle_upload(), create_session()
│   │   │   └── reconciliation_service.py  run_reconciliation(), get_session()
│   │   │
│   │   ├── utils/
│   │   │   ├── column_detector.py  detect_columns() → ColumnMap (flexible header detection)
│   │   │   ├── excel_parser.py     parse_invoice_excel(), parse_gstr2b_excel()
│   │   │   ├── export.py           generate_excel_export() → bytes (openpyxl)
│   │   │   ├── gstin_validator.py  GSTIN format validator (regex)
│   │   │   └── password.py         hash_password(), verify_password() using bcrypt directly
│   │   │
│   │   └── main.py                 FastAPI app factory, routers registered
│   │
│   ├── tests/
│   │   ├── fixtures/
│   │   │   ├── sample_invoice.xlsx     5-row test invoice file
│   │   │   └── sample_gstr2b.xlsx      5-row GSTR-2B with intentional mismatches
│   │   ├── test_auth.py            8 auth tests
│   │   ├── test_upload.py          9 upload tests
│   │   └── test_reconciliation.py  12 reconciliation tests
│   │
│   ├── .env.example                Environment variable template
│   └── requirements.txt            Python dependencies
│
├── frontend/                       Angular application
│   └── src/app/
│       ├── core/
│       │   └── services/
│       │       ├── auth.service.ts         Login, logout, token management
│       │       ├── upload.service.ts       File upload HTTP calls
│       │       └── reconciliation.service.ts  Reconciliation HTTP calls
│       │
│       ├── guards/
│       │   └── auth.guard.ts       Redirects unauthenticated users to /login
│       │
│       ├── interceptors/
│       │   └── auth.interceptor.ts Attaches Bearer token to every HTTP request
│       │
│       ├── models/
│       │   ├── auth.models.ts      User, LoginRequest, TokenResponse interfaces
│       │   ├── upload.models.ts    UploadResult, SessionResponse interfaces
│       │   └── reconciliation.models.ts  MatchedRecord, UnmatchedRecord, etc.
│       │
│       ├── modules/
│       │   ├── auth/login/         Login page (standalone component)
│       │   ├── dashboard/          Upload dashboard (drag-drop two files)
│       │   └── reconciliation/     Results page (summary cards + tables)
│       │
│       ├── shared/components/
│       │   └── file-drop-zone/     Reusable drag-and-drop upload component
│       │
│       ├── app.config.ts           Angular providers (HTTP, router, animations)
│       └── app.routes.ts           Lazy-loaded routes with auth guard
│
├── docs/                           Architecture and design documents
├── docker-compose.yml              Docker setup (Phase 5)
├── .env.example                    Root-level env template
├── README.md                       Quick start reference
└── DEVELOPER_GUIDE.md              This file
```

---

## 5. Backend Setup

### Step 1 — Clone the repository

```bash
git clone https://github.com/akarunakumar/gst-reconciliation-system.git
cd gst-reconciliation-system
```

### Step 2 — Create a Python virtual environment

```bash
cd backend
python -m venv venv
```

### Step 3 — Activate the virtual environment

**Windows (PowerShell):**
```powershell
.\venv\Scripts\Activate.ps1
```

**Windows (Git Bash / CMD):**
```bash
source venv/Scripts/activate
```

**macOS / Linux:**
```bash
source venv/bin/activate
```

You will see `(venv)` in your terminal prompt when activated.

### Step 4 — Install dependencies

```bash
pip install -r requirements.txt
```

> **Python 3.14 note:** pandas has no source wheel for 3.14. Use:
> ```bash
> pip install "pandas>=2.2" --only-binary :all:
> pip install -r requirements.txt
> ```

### Step 5 — Create the environment file

```bash
cp .env.example .env
```

Open `.env` and set at minimum:
```
JWT_SECRET=any-long-random-string-here
USE_MOCK_SERVICES=true
```

Leave everything else as-is for local development.

### Step 6 — Start the backend server

```bash
uvicorn app.main:app --reload
```

The API is now running at:
- **Base URL:** `http://localhost:8000`
- **Swagger UI (interactive docs):** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`

---

## 6. Frontend Setup

Open a **new terminal** (keep the backend running).

### Step 1 — Navigate to the frontend folder

```bash
cd frontend
```

### Step 2 — Install Node.js dependencies

```bash
npm install
```

This reads `package.json` and installs all Angular packages into `node_modules/`.

### Step 3 — Start the development server

```bash
ng serve
```

Or equivalently:
```bash
npm start
```

The app is now running at: **`http://localhost:4200`**

Angular will automatically reload the browser whenever you save a file.

### Step 4 — Build for production (optional)

```bash
ng build
```

Output goes to `frontend/dist/frontend/`. Use this to deploy to a web server.

---

## 7. Running the Full Application

You need **two terminals** running simultaneously:

| Terminal | Command | URL |
|---|---|---|
| Terminal 1 (Backend) | `uvicorn app.main:app --reload` | http://localhost:8000 |
| Terminal 2 (Frontend) | `ng serve` | http://localhost:4200 |

### Full User Flow

```
1. Open http://localhost:4200
2. Log in with admin / Admin@123
3. Dashboard — drag and drop Invoice.xlsx into the left zone
4. Dashboard — drag and drop GSTR2B.xlsx into the right zone
5. Click "Start Reconciliation"
6. Auto-navigates to /reconciliation/:sessionId
7. View summary cards (Matched / Mismatch / Only Invoice / Only GSTR2B)
8. Switch tabs — Matched Records | Unmatched / Mismatched
9. Search by invoice number or GSTIN
10. Filter by status
11. Click "Export Excel" to download the full report
```

---

## 8. Test Credentials

| Username | Password | Role |
|---|---|---|
| `admin` | `Admin@123` | Administrator |
| `auditor` | `Audit@123` | Auditor |
| `viewer` | `View@123` | View-only |

These are hardcoded in `backend/app/repositories/user_repository.py` (mock mode).

---

## 9. API Reference

### Authentication

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/v1/auth/login` | Login with username + password → JWT tokens |
| POST | `/api/v1/auth/logout` | Logout (token invalidation stub) |
| POST | `/api/v1/auth/refresh` | Refresh access token using refresh token |

**Login request body:**
```json
{
  "username": "admin",
  "password": "Admin@123"
}
```

**Login response:**
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer",
  "user": { "username": "admin", "role": "admin" }
}
```

---

### File Upload

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/v1/upload/invoices` | Upload Invoice Excel → returns `temp_key` |
| POST | `/api/v1/upload/gstr2b` | Upload GSTR-2B Excel → returns `temp_key` |
| POST | `/api/v1/upload/start` | Create reconciliation session from two temp keys |

**Start request body:**
```json
{
  "invoice_temp_key": "uuid-from-invoice-upload",
  "gstr2b_temp_key": "uuid-from-gstr2b-upload",
  "session_name": "April 2024 Recon"
}
```

---

### Reconciliation

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/v1/reconciliation/run/{session_id}` | Run the matching engine on the session |
| GET | `/api/v1/reconciliation/summary/{session_id}` | Get reconciliation summary metrics |
| GET | `/api/v1/reconciliation/matched/{session_id}` | Paginated matched records |
| GET | `/api/v1/reconciliation/unmatched/{session_id}` | Paginated unmatched records |
| GET | `/api/v1/reconciliation/export/{session_id}` | Download full Excel report |

**Matched query parameters:**
```
?page=1&page_size=20&search=INV-001&match_status=MATCHED
```

**Unmatched query parameters:**
```
?page=1&page_size=20&search=&missing_source=GSTR2B
```

> All endpoints except `/auth/login` require `Authorization: Bearer <token>` header.

---

## 10. Running Tests

### Backend Tests

Make sure the virtual environment is activated, then from the `backend/` folder:

```bash
pytest tests/ -v
```

Expected output:
```
tests/test_auth.py::test_login_success PASSED
tests/test_auth.py::test_login_wrong_password PASSED
... (8 auth tests)

tests/test_upload.py::test_upload_invoice PASSED
... (9 upload tests)

tests/test_reconciliation.py::test_run_reconciliation PASSED
tests/test_reconciliation.py::test_amount_mismatch_detected PASSED
... (12 reconciliation tests)

29 passed in x.xxs
```

### Run a specific test file

```bash
pytest tests/test_reconciliation.py -v
```

### Run a specific test

```bash
pytest tests/test_reconciliation.py::test_amount_mismatch_detected -v
```

### Frontend Tests

```bash
cd frontend
ng test
```

This opens a Chrome browser and runs Karma/Jasmine unit tests.

---

## 11. Architecture & Code Patterns

### 11.1 Layered Backend Architecture

Requests flow through these layers — each layer only calls the one below it:

```
HTTP Request
    │
    ▼
API Layer (app/api/v1/*.py)
    │  Validates HTTP input, calls service
    ▼
Service Layer (app/services/*.py)
    │  Business logic, calls repository + orchestrators
    ▼
Repository Layer (app/repositories/*.py)
    │  Data access — currently in-memory (mock), later PostgreSQL
    ▼
Data (in-memory dict / future: database)
```

### 11.2 Orchestration Agent Pattern

Complex multi-step operations (upload processing, reconciliation) use an **Agent Pipeline** rather than one large function. Each agent does one thing and passes a shared context dict to the next.

```python
# Every agent follows this contract:
class BaseAgent(ABC):
    @abstractmethod
    def run(self, context: dict) -> AgentResult: ...

@dataclass
class AgentResult:
    success: bool
    data: dict        # output data for the next agent
    errors: list[str] # non-fatal warnings or fatal errors
```

**Upload pipeline** (`UploadOrchestrator`):
```
UploadAgent (validate type + size)
    → ParsingAgent (parse Excel rows)
    → ValidationAgent (warn on missing columns — never blocks)
```

**Reconciliation pipeline** (`ReconciliationOrchestrator`):
```
detect_columns() on invoice rows
detect_columns() on GSTR2B rows
    → GSTMatchingAgent (compare rows, build matched + unmatched lists)
    → SummaryGenerationAgent (compute counts, percentages, totals)
```

### 11.3 Column Detection (Flexible Headers)

Real-world GST Excel files use different column names. The `column_detector.py` uses alias sets to find the right column regardless of what it's called:

| Field | Accepted column names |
|---|---|
| Invoice Number | `invoice_number`, `invoice_no`, `bill_no`, `ref_no`, `voucher_no`, `doc_no`, ... |
| GSTIN | `gstin`, `gstin_of_supplier`, `supplier_gstin`, `party_gstin`, `gst_no`, ... |
| Taxable Amount | `taxable_amount`, `taxable_value`, `taxable_amt`, `base_amount`, ... |
| IGST | `igst`, `igst_amount`, `integrated_tax`, ... |

If a column can't be detected, it is set to `None` in the `ColumnMap` — the engine falls back gracefully rather than rejecting the file.

### 11.4 Frontend Architecture

- **Standalone components** — no NgModule needed (Angular 17+ default)
- **Lazy loading** — each route loads its own chunk only when visited
- **Auth interceptor** — automatically attaches `Authorization: Bearer <token>` to every HTTP request
- **Auth guard** — redirects unauthenticated users to `/login` before any protected route loads
- **RxJS Subjects with `takeUntil`** — prevents memory leaks by unsubscribing when components are destroyed

```
app.routes.ts
  /login              → LoginComponent (eager, no guard)
  /dashboard          → DashboardComponent (lazy, auth-guarded)
  /reconciliation/:id → ReconciliationComponent (lazy, auth-guarded)
```

### 11.5 JWT Auth Flow

```
1. POST /auth/login → access_token (60 min) + refresh_token (7 days)
2. Tokens stored in localStorage (keys: gst_access_token, gst_refresh_token, gst_user)
3. authInterceptor reads access_token and adds "Authorization: Bearer ..." to every request
4. On 401 → authService.logout() clears storage and redirects to /login
```

---

## 12. Environment Variables

All backend config lives in `backend/.env`. Copy from `.env.example` to get started.

| Variable | Default | Description |
|---|---|---|
| `JWT_SECRET` | *(must set)* | Secret key for signing JWT tokens. Use a long random string in production. |
| `JWT_ALGORITHM` | `HS256` | JWT signing algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `60` | How long access tokens are valid |
| `REFRESH_TOKEN_EXPIRE_DAYS` | `7` | How long refresh tokens are valid |
| `USE_MOCK_SERVICES` | `true` | `true` = in-memory mock data, no database needed. Set `false` when connecting a real DB. |
| `DATABASE_URL` | *(PostgreSQL URL)* | Only used when `USE_MOCK_SERVICES=false` |
| `APP_ENV` | `development` | `development` or `production` |
| `ALLOWED_ORIGINS` | `http://localhost:4200` | CORS allowed origins (comma-separated for multiple) |

### Frontend Environment

Frontend environment config is in `frontend/src/environments/`:

| File | Used when |
|---|---|
| `environment.ts` | `ng serve` (development) |
| `environment.prod.ts` | `ng build` (production) |

To point the frontend at a different backend URL, edit `apiUrl` in the environment file:
```typescript
export const environment = {
  production: false,
  apiUrl: 'http://localhost:8000/api/v1',
};
```

---

## 13. Development Phases

| Phase | Scope | Status |
|---|---|---|
| **Phase 1** | Project setup, JWT authentication, login page | ✅ Complete |
| **Phase 2** | Drag-drop file upload (Invoice + GSTR-2B), Excel parsing, in-memory sessions | ✅ Complete |
| **Phase 3** | Reconciliation engine, REST APIs, results page with summary cards + export | ✅ Complete |
| **Phase 4** | Dashboard with charts, month-wise trend reports | Pending |
| **Phase 5** | PostgreSQL integration, Docker, CI/CD pipeline | Pending |

### Current test coverage

```
Backend:  29 tests — 8 auth + 9 upload + 12 reconciliation — all green
Frontend: Angular component unit tests (ng test)
```

---

## 14. Troubleshooting

### Backend won't start — `ModuleNotFoundError`

Make sure you are running from inside the `backend/` folder and the venv is activated:
```bash
cd backend
source venv/Scripts/activate   # Windows Git Bash
uvicorn app.main:app --reload
```

---

### `pip install` fails on pandas (Python 3.14)

pandas doesn't have a source build for Python 3.14. Install the binary wheel:
```bash
pip install "pandas>=2.2" --only-binary :all:
```

---

### Frontend can't reach backend — CORS error

Check that `ALLOWED_ORIGINS` in `backend/.env` includes the frontend URL:
```
ALLOWED_ORIGINS=http://localhost:4200
```

Then restart the backend.

---

### `ng serve` port already in use

```bash
ng serve --port 4201
```

Then update `ALLOWED_ORIGINS` in `.env` to match the new port.

---

### Login fails — `401 Unauthorized`

Use one of the test accounts exactly as listed:
- `admin` / `Admin@123`
- `auditor` / `Audit@123`
- `viewer` / `View@123`

Passwords are case-sensitive.

---

### Excel upload rejected

The system accepts `.xlsx` and `.xls` files up to **10 MB**. Any column names are accepted — there are no required headers. If you see a warning about missing columns, it is informational only and the file is still processed.

---

### `ng build` errors — unknown pipe

Angular has no built-in `min` pipe for arrays. If you see this error, the template should use a component method:
```html
<!-- Wrong -->
{{ [a, b] | min }}

<!-- Correct -->
{{ minVal(a, b) }}
```

---

*For questions or issues, open a GitHub issue at: https://github.com/akarunakumar/gst-reconciliation-system/issues*
