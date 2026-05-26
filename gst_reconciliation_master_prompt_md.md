# Enterprise GST Reconciliation System – Full Stack Development Prompt

You are a senior enterprise architect and full-stack engineer.

Build a complete production-grade enterprise application named:

`gst-reconciliation-system`

## Goal

Develop a modern enterprise-grade GST reconciliation platform that compares uploaded purchase invoices against GST GSTR2B data and displays:

- Matched records
- Unmatched records
- Mismatch reasons
- Reconciliation summary dashboard

The system must follow clean architecture, layered design, scalable folder structure, reusable services, proper validation, and industry coding standards.

---

# Root Project Structure

```text
gst-reconciliation-system/
├── frontend/
├── backend/
├── docs/
├── docker-compose.yml
├── README.md
└── .env.example
```

---

# Frontend Project

Folder Name:

`frontend`

## Frontend Technology Stack

Use:

- Angular
- TypeScript
- Bootstrap 5
- Angular Material
- RxJS
- Reactive Forms
- SCSS

---

# Backend Project

Folder Name:

`backend`

## Backend Technology Stack

Use:

- Python 3.14 compatible
- FastAPI
- SQLAlchemy
- Pydantic
- PostgreSQL
- Alembic migrations
- Pandas/OpenPyXL for Excel parsing
- JWT Authentication

---

# Frontend Architecture Angular

Implement layered modular architecture.

```text
frontend/src/app/
├── core/
├── shared/
├── services/
├── guards/
├── interceptors/
├── utils/
├── layouts/
├── models/
└── modules/
    ├── auth/
    ├── dashboard/
    ├── upload/
    ├── reconciliation/
    └── reports/
```

## Frontend Requirements

- Reusable components
- Shared utilities
- Route guards
- API interceptors
- Environment-based config
- Proper lazy loading
- Reactive form validation
- Responsive layouts
- Clean reusable architecture

---

# Backend Architecture FAst API python (3.14.4)

Implement enterprise clean layered architecture.

```text
backend/
├── app/
│   ├── api/
│   ├── services/
│   ├── repositories/
│   ├── models/
│   ├── schemas/
│   ├── utils/
│   ├── core/
│   ├── middleware/
│   ├── config/
│   ├── orchestration/
│   ├── reconciliation/
│   └── tests/
```

## Backend Requirements

Use:

- Dependency Injection
- Repository pattern
- Service layer
- Utility layer
- Config isolation
- DTO schemas
- Async APIs where applicable

---

# Application Flow

## 1. Login Page

Build a highly attractive enterprise login page.

### Requirements

- GST-themed wallpaper background
- Enterprise branding style
- Animated modern UI
- Responsive design
- Bootstrap styling
- Proper form validation
- Username/password login
- JWT Authentication
- Error handling
- Loading indicators
- Remember me option

### Additional Requirements

Include:

- Mock authentication initially
- Ability to switch to real DB authentication later

---

## 2. Home Dashboard

Simple clean dashboard page.

### Features

- Upload Invoice Excel file
- Upload GSTR2B Excel file
- Drag and drop upload area
- File type validation
- File size validation
- Upload progress indicators
- Submit button
- Reconciliation status section

### Supported Formats

- .xlsx
- .xls

---

## 3. Reconciliation Output Page

Create professional reconciliation result UI.

### Matched Records Table

Columns:

- Invoice Number
- GSTIN
- Vendor Name
- Taxable Amount
- IGST
- CGST
- SGST
- Match Status

### Unmatched Records Table

Columns:

- Invoice Number
- GSTIN
- Mismatch Reason
- Missing Source
- Amount Difference

### Features

- Pagination
- Filtering
- Sorting
- Search
- Export to Excel
- Summary cards
- Reconciliation percentage
- Status badges
- Responsive tables

---

# Agent Orchestration Layer

Implement orchestration module in backend.

## Agents

1. File Upload Agent
2. Excel Parsing Agent
3. Validation Agent
4. GST Matching Agent
5. Reconciliation Agent
6. Summary Generation Agent
7. Reporting Agent

## Flow

- Upload files
- Parse data
- Validate structure
- Match invoices
- Generate unmatched list
- Generate summary metrics
- Return API response

### Additional Requirements

Include:

- Logging
- Error tracking
- Retry strategy
- Extensible orchestration design

---

# APIs Required

## Authentication APIs

- POST `/api/auth/login`
- POST `/api/auth/logout`
- POST `/api/auth/refresh`

## Upload APIs

- POST `/api/upload/invoices`
- POST `/api/upload/gstr2b`

## Reconciliation APIs

- POST `/api/reconciliation/start`
- GET `/api/reconciliation/{sessionId}`
- GET `/api/reconciliation/matched`
- GET `/api/reconciliation/unmatched`
- GET `/api/reconciliation/summary`

---

# Database Design

Use PostgreSQL.

## Tables

### users

- id
- username
- password_hash
- role
- created_at

### reconciliation_sessions

- id
- session_name
- uploaded_by
- invoice_file_name
- gstr2b_file_name
- status
- matched_count
- unmatched_count
- created_at

### invoice_records

- id
- session_id
- invoice_number
- gstin
- taxable_amount
- tax_amount
- source_type

### reconciliation_results

- id
- session_id
- invoice_id
- match_status
- mismatch_reason

---

# Environment Configuration

Use `.env` everywhere.

## Required Files

- `.env.example`
- Config loader
- Environment-based switching

### Example Variables

```env
DATABASE_URL=
JWT_SECRET=
APP_ENV=
USE_MOCK_SERVICES=
```

Do NOT hardcode credentials.

---

# Mock Data

Provide:

- Sample invoice Excel
- Sample GSTR2B Excel
- Mock users
- Mock API responses

Make external integrations replaceable later.

---

# Validation Requirements

## Frontend Validation

- Reactive form validation
- File validation
- Required field validation

## Backend Validation

- Pydantic validation
- Schema validation
- Excel column validation
- GSTIN validation
- Duplicate detection

---

# Error Handling

Implement:

- Global exception handling
- API error response standardization
- Validation messages
- Frontend toast notifications
- Retry handling
- Logging

---

# Security Requirements

Implement:

- JWT Authentication
- Password hashing
- Secure API middleware
- CORS handling
- Role-based access preparation

---

# Testing

## Frontend

- Angular component tests

## Backend

- Pytest
- Unit tests
- API tests
- Service layer tests
- Reconciliation orchestration tests

---

# UI/UX Requirements

The UI must look enterprise-grade.

## Style Inspiration

- Deloitte
- EY
- SAP Fiori
- Zoho Enterprise
- TCS Enterprise Portals

## Requirements

- Elegant dashboard
- Smooth animations
- Clean cards
- Modern tables
- Responsive layout
- Professional color palette

---

# Deliverables

Generate:

1. Complete Angular frontend
2. Complete FastAPI backend
3. PostgreSQL schema
4. Mock implementations
5. README documentation
6. Setup scripts
7. Docker support
8. Environment configuration
9. Unit tests
10. API documentation
11. Folder structure
12. Architecture explanation

---

# Additional Requirements

- Use TypeScript strictly
- Use clean code principles
- Use SOLID principles
- Use modular reusable architecture
- Use proper naming conventions
- Add comments where useful
- Keep code production-ready

---

# Uploaded Files Context

Use uploaded sample files and design flow as reference:

- Invoice.xlsx
- GSTR2B sample
- Design Approach document

Implement reconciliation logic based on uploaded examples.

---

# Final Requirement

Generate code incrementally in phases.

## Phase 1

- Project setup
- Authentication
- Folder structure

## Phase 2

- Upload module

## Phase 3

- Excel parsing
- Reconciliation engine

## Phase 4

- Dashboard
- Reports

## Phase 5

- Testing
- Docker
- Documentation

Always provide:

- Folder structure
- Commands
- Setup instructions
- Clean reusable code
- Production-grade implementation

