# LexiConnect

Location-based lawyer discovery, KYC-verified onboarding, and case-centric booking workflows.

LexiConnect is a university-built, full-stack platform that helps clients find lawyers, request case representation, and schedule verified appointments with controlled document handling and audit trails. It is a scheduling and case-management system, not a law firm and not a source of legal advice. Its system design centers on case-based workflows with RBAC and auditability as first-class concerns.

## Table Of Contents
- Why It Matters
- Features By Role
- Workflow Highlights
- Security Model
- Tech Stack
- Architecture
- Screenshots
- Run Locally
- Environment Variables
- Academic Report
- Credits And Attribution
- Project Status

## Why It Matters
Legal service workflows are often fragmented across calls, emails, and untracked documents. LexiConnect centralizes discovery, case intake, approvals, booking, and document access so that each step is traceable, role-aware, and auditable.

## Features By Role
Client
- Lawyer discovery by district, city, specialization, and language
- Case intake and case list tracking
- Booking requests and status updates
- Document uploads tied to cases and bookings
- Notifications and activity updates

Lawyer
- Public profile and specialization management
- Availability scheduling with exceptions and blackout days
- Booking confirmation and rejection
- Token queue management for same-day consultations
- KYC submission for verification
- Case feed browsing and case request workflow
- Case documents access and review links

Clerk
- Booking visibility based on RBAC privileges
- Controlled document access per policy

Admin
- KYC approval and rejection
- Audit log and authentication log review
- Dispute tracking and reporting
- RBAC module and privilege management
- Administrative metrics and dashboards

## Workflow Highlights
- Case to booking: client opens a case, lawyers request the case, client approves a lawyer, then a booking is created for that case.
- KYC verification: lawyers submit KYC and admins approve or reject before a lawyer is considered verified.
- Document handling: documents are uploaded against a case or booking with role-checked access and review links to support manual approval or feedback.
- Conflict prevention: booking creation includes slot validation and overlap checks to avoid double-booking.
- Audit trail: sensitive actions write audit events and authentication logs for traceability.

## Security Model
- JWT access and refresh tokens for API authentication
- Role-based access control (RBAC) with module-level privileges
- Audit logs and auth logs for security-sensitive actions
- Server-side document access checks for case- and booking-linked files

## Tech Stack

| Layer | Technology |
| --- | --- |
| Frontend | React, Vite, Tailwind CSS, React Router, Axios |
| Backend | FastAPI, SQLAlchemy, Alembic, Python-Jose (JWT), Passlib + bcrypt |
| Database | PostgreSQL |
| Dev Services | Docker Compose (PostgreSQL, Mailpit) |

## Architecture
- React (Vite) SPA communicates with FastAPI REST endpoints
- FastAPI persists data in PostgreSQL via SQLAlchemy
- File uploads are stored locally at `backend/uploads` and served from `/uploads`
- Mailpit captures outbound email during local development

Diagrams

![Architecture Diagram](docs/diagrams/architecture.png)
![ERD](docs/diagrams/erd.png)

## Screenshots

| # | Screen | File |
| --- | --- | --- |
| 01 | Landing | [docs/screenshots/01-landing.png](docs/screenshots/01-landing.png) |
| 02 | Login | [docs/screenshots/02-login.png](docs/screenshots/02-login.png) |
| 03 | Lawyer search | [docs/screenshots/03-lawyer-search.png](docs/screenshots/03-lawyer-search.png) |
| 04 | Lawyer profile | [docs/screenshots/04-lawyer-profile.png](docs/screenshots/04-lawyer-profile.png) |
| 05 | Booking | [docs/screenshots/05-booking.png](docs/screenshots/05-booking.png) |
| 06 | Document upload | [docs/screenshots/06-document-upload.png](docs/screenshots/06-document-upload.png) |
| 07 | Client cases | [docs/screenshots/07-client-cases.png](docs/screenshots/07-client-cases.png) |
| 08 | Lawyer dashboard | [docs/screenshots/08-lawyer-dashboard.png](docs/screenshots/08-lawyer-dashboard.png) |
| 09 | Lawyer availability | [docs/screenshots/09-lawyer-availability.png](docs/screenshots/09-lawyer-availability.png) |
| 10 | Lawyer KYC | [docs/screenshots/10-lawyer-kyc.png](docs/screenshots/10-lawyer-kyc.png) |
| 11 | Lawyer case feed | [docs/screenshots/11-lawyer-case-feed.png](docs/screenshots/11-lawyer-case-feed.png) |
| 12 | Admin dashboard | [docs/screenshots/12-admin-dashboard.png](docs/screenshots/12-admin-dashboard.png) |
| 13 | Admin audit log | [docs/screenshots/13-admin-audit-log.png](docs/screenshots/13-admin-audit-log.png) |
| 14 | RBAC denied | [docs/screenshots/14-rbac-denied.png](docs/screenshots/14-rbac-denied.png) |

## Run Locally
Docker Compose only starts dependencies (PostgreSQL and Mailpit). Run the backend and frontend manually.

Dependencies

PowerShell
```powershell
docker compose up -d
```

Bash
```bash
docker compose up -d
```

Backend (FastAPI)

PowerShell
```powershell
cd backend
copy .env.example .env
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

Bash
```bash
cd backend
cp .env.example .env
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

Frontend (React + Vite)

PowerShell
```powershell
cd frontend
copy .env.example .env
npm install
npm run dev
```

Bash
```bash
cd frontend
cp .env.example .env
npm install
npm run dev
```

Local URLs
- Frontend: http://127.0.0.1:5173
- API: http://127.0.0.1:8000
- API Docs (Swagger): http://127.0.0.1:8000/docs
- Mailpit: http://127.0.0.1:8025

## Environment Variables
Backend: `backend/.env`
```env
# Database Configuration
# PostgreSQL connection string (for Docker Compose setup)
DATABASE_URL=postgresql+psycopg2://lexiconnect:lexiconnect@127.0.0.1:5432/lexiconnect

# JWT Configuration
JWT_SECRET=change_me_to_a_secure_random_string
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# Environment variables for seeding demo users
# Copy this file to .env and adjust values as needed

SEED_DEMO_USERS=true

ADMIN_EMAIL=admin@lexiconnect.local
ADMIN_PASSWORD=Admin@123

LAWYER_EMAIL=lawyer@lexiconnect.local
LAWYER_PASSWORD=Lawyer@123

CLIENT_EMAIL=client@lexiconnect.local
CLIENT_PASSWORD=Client@123

APPRENTICE_EMAIL=apprentice@lexiconnect.local
APPRENTICE_PASSWORD=Apprentice@123
```

Frontend: `frontend/.env`
```env
# API Base URL for backend
# Copy this file to .env and adjust values as needed
VITE_API_BASE_URL=http://127.0.0.1:8000
```

## Academic Report
[LexiConnect Final Project Report](LexiConnect_Final_Report.pdf)

## Credits And Attribution
LexiConnect is a university group project.

Team (Group 06)
- D. Thenujayan — Group Leader / Systems Integration
- Y. Chapa — UI and UX
- W. A. Methsarani — Localization and Forms
- D. Vithana — QA and Data Integrity
- P. Udavi — Documentation

Original university repository: (https://github.com/S-W-Development-Group-Project-UOG-4-7/LexiConnect)

## Project Status
This project is actively maintained for academic purposes. Future improvements (not yet implemented) could include:
- Full Docker Compose stack for backend and frontend
- Object storage for uploads (S3 or MinIO)
- CI pipeline and deployment automation
- Production deployment hardening
test deploy 2026-02-18 16:42:50 +05:30
