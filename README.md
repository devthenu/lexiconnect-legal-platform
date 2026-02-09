# LexiConnect

Location-Based Lawyer Discovery & Appointment Platform

LexiConnect is a full-stack web platform that helps users discover verified lawyers by location and specialization, book appointments, and manage legal case workflows digitally. It is built as a university group project with role-based access control, audit logging, and a document workflow suited for legal service delivery.

## Key Features

Client
- Register and sign in with JWT-based authentication
- Search lawyers by district, city, specialization, and languages
- View verified lawyer profiles
- Book appointments and manage booking status
- Submit case intake forms and upload case documents
- Track disputes and case updates
- View notifications and activity updates
- Access public case feed and case comments (where enabled)

Lawyer
- Manage public profile, services, and specializations
- Configure availability, exceptions, and blackout periods
- Confirm or reject booking requests
- Manage token queue for same-day consultations
- Submit KYC for verification
- Review client intake and case documents
- Browse case feed, request cases, and manage assigned cases
- Apprenticeship workflow and notes (optional module)

Clerk
- View bookings
- Manage token queue entries
- View documents (per RBAC policy)

Admin
- Admin dashboard with metrics and reports
- Approve KYC submissions
- Manage disputes
- Audit log and auth log review
- Access control for roles and privileges (RBAC)
- Notifications history

## Security And Compliance

- JWT access and refresh tokens for API authentication
- Password hashing with bcrypt via Passlib
- Role-based access control (RBAC) with module privileges
- Audit log and authentication log trails for sensitive actions
- Controlled document access and server-side checks
- Password reset flow with one-time tokens

## Tech Stack

Frontend
- React + Vite
- Tailwind CSS
- React Router
- Axios
- Chart.js and Recharts

Backend
- FastAPI
- SQLAlchemy
- Alembic
- PostgreSQL
- python-jose (JWT)
- Passlib + bcrypt

Infrastructure And Tooling
- Docker Compose (PostgreSQL, Mailpit)
- Mailpit for local SMTP testing

## Architecture

High-level data flow
- React (Vite) SPA calls FastAPI REST endpoints
- FastAPI serves data from PostgreSQL via SQLAlchemy
- Documents are stored on the local filesystem under `backend/uploads` and served from `/uploads`
- Mailpit captures outgoing password reset emails during local development

Diagrams

![Architecture Diagram](docs/diagrams/architecture.png)
![ERD](docs/diagrams/erd.png)

## Screenshots

Screenshots should be placed in `docs/screenshots/`.

| # | Screen | File |
| --- | --- | --- |
| 01 | Landing page | [docs/screenshots/01-landing.png](docs/screenshots/01-landing.png) |
| 02 | Login | [docs/screenshots/02-login.png](docs/screenshots/02-login.png) |
| 03 | Register | [docs/screenshots/03-register.png](docs/screenshots/03-register.png) |
| 04 | Client dashboard | [docs/screenshots/04-client-dashboard.png](docs/screenshots/04-client-dashboard.png) |
| 05 | Lawyer search | [docs/screenshots/05-lawyer-search.png](docs/screenshots/05-lawyer-search.png) |
| 06 | Lawyer profile | [docs/screenshots/06-lawyer-profile.png](docs/screenshots/06-lawyer-profile.png) |
| 07 | Booking form | [docs/screenshots/07-booking-form.png](docs/screenshots/07-booking-form.png) |
| 08 | Client bookings | [docs/screenshots/08-client-bookings.png](docs/screenshots/08-client-bookings.png) |
| 09 | Booking detail | [docs/screenshots/09-booking-detail.png](docs/screenshots/09-booking-detail.png) |
| 10 | Case documents list | [docs/screenshots/10-case-documents.png](docs/screenshots/10-case-documents.png) |
| 11 | Document upload | [docs/screenshots/11-document-upload.png](docs/screenshots/11-document-upload.png) |
| 12 | Client cases list | [docs/screenshots/12-client-cases.png](docs/screenshots/12-client-cases.png) |
| 13 | Client case detail | [docs/screenshots/13-client-case-detail.png](docs/screenshots/13-client-case-detail.png) |
| 14 | Client dispute submission | [docs/screenshots/14-client-dispute.png](docs/screenshots/14-client-dispute.png) |
| 15 | Lawyer dashboard | [docs/screenshots/15-lawyer-dashboard.png](docs/screenshots/15-lawyer-dashboard.png) |
| 16 | Lawyer availability | [docs/screenshots/16-lawyer-availability.png](docs/screenshots/16-lawyer-availability.png) |
| 17 | Lawyer token queue | [docs/screenshots/17-lawyer-token-queue.png](docs/screenshots/17-lawyer-token-queue.png) |
| 18 | Lawyer KYC | [docs/screenshots/18-lawyer-kyc.png](docs/screenshots/18-lawyer-kyc.png) |
| 19 | Lawyer case feed | [docs/screenshots/19-lawyer-case-feed.png](docs/screenshots/19-lawyer-case-feed.png) |
| 20 | Lawyer case detail | [docs/screenshots/20-lawyer-case-detail.png](docs/screenshots/20-lawyer-case-detail.png) |
| 21 | Admin dashboard | [docs/screenshots/21-admin-dashboard.png](docs/screenshots/21-admin-dashboard.png) |
| 22 | Admin KYC approval | [docs/screenshots/22-admin-kyc-approval.png](docs/screenshots/22-admin-kyc-approval.png) |
| 23 | Admin audit log | [docs/screenshots/23-admin-audit-log.png](docs/screenshots/23-admin-audit-log.png) |
| 24 | Admin auth log | [docs/screenshots/24-admin-auth-log.png](docs/screenshots/24-admin-auth-log.png) |
| 25 | Admin access control | [docs/screenshots/25-admin-access-control.png](docs/screenshots/25-admin-access-control.png) |
| 26 | Admin disputes | [docs/screenshots/26-admin-disputes.png](docs/screenshots/26-admin-disputes.png) |
| 27 | Notifications history | [docs/screenshots/27-notifications.png](docs/screenshots/27-notifications.png) |
| 28 | Public case feed | [docs/screenshots/28-public-case-feed.png](docs/screenshots/28-public-case-feed.png) |
| 29 | Public case detail | [docs/screenshots/29-public-case-detail.png](docs/screenshots/29-public-case-detail.png) |
| 30 | Apprentice dashboard | [docs/screenshots/30-apprentice-dashboard.png](docs/screenshots/30-apprentice-dashboard.png) |

## How To Run Locally

Docker Compose (Database and Mailpit)

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

Backend `backend/.env.example`
```env
DATABASE_URL=postgresql+psycopg2://lexiconnect:lexiconnect@127.0.0.1:5432/lexiconnect

JWT_SECRET=change_me_to_a_secure_random_string
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

SEED_DEMO_USERS=true

ADMIN_EMAIL=admin@lexiconnect.local
ADMIN_PASSWORD=Admin@123

LAWYER_EMAIL=lawyer@lexiconnect.local
LAWYER_PASSWORD=Lawyer@123

CLIENT_EMAIL=client@lexiconnect.local
CLIENT_PASSWORD=Client@123

APPRENTICE_EMAIL=apprentice@lexiconnect.local
APPRENTICE_PASSWORD=Apprentice@123

SMTP_HOST=localhost
SMTP_PORT=1025
EMAIL_FROM=no-reply@lexiconnect.local
FRONTEND_URL=http://localhost:5173
```

Notes
- `JWT_*` values exist in `backend/.env.example`, but the backend currently uses constants in `backend/app/routers/auth.py`. If you want env-based secrets, wire them there.
- `SMTP_*` and `FRONTEND_URL` are used for password reset emails. Defaults match the Mailpit service in `docker-compose.yml`.

Frontend `frontend/.env.example`
```env
VITE_API_BASE_URL=http://127.0.0.1:8000
```

## Database And Migrations

- PostgreSQL is required. Set `DATABASE_URL` in `backend/.env`.
- Alembic configuration lives in `backend/alembic.ini` and `backend/alembic/`.

Run migrations

PowerShell
```powershell
cd backend
alembic upgrade head
```

Bash
```bash
cd backend
alembic upgrade head
```

Optional seed data

PowerShell
```powershell
cd backend
python scripts/seed.py
```

Bash
```bash
cd backend
python scripts/seed.py
```

## Credits And Attribution

LexiConnect is a university group project.

Team (Group 06)
- D. Thenujayan — Group Leader / Systems Integration
- Y. Chapa — UI and UX
- W. A. Methsarani — Localization and Forms
- D. Vithana — QA and Data Integrity
- P. Udavi — Documentation

Original university repository: <UNIVERSITY_REPO_URL>

## Disclaimer

This project is developed strictly for academic purposes and is not intended for commercial or legal deployment.

Legal disclaimer: LexiConnect is a neutral legal appointment facilitation platform developed strictly for academic purposes. It does not advertise, promote, rank, or endorse any legal practitioner. All lawyer profiles are standardized, admin-verified, and displayed solely based on user-selected filters.