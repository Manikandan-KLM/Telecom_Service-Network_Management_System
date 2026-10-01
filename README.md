# Telecom Service & Network Management System

A FastAPI-based backend application for managing telecom customers, service plans, SIM cards, devices, subscriptions, network infrastructure, support tickets, service requests, SLA monitoring, reports and audit logs.

## Technologies Used

* Python
* FastAPI
* Pydantic
* SQLAlchemy
* PostgreSQL
* SQLite
* JWT Authentication
* Argon2 Password Hashing
* Alembic
* Redis
* Pytest
* Docker

## User Roles

* Super Admin
* Operations Manager
* Support Agent
* Network Engineer
* Field Technician
* Customer

## Main Features

### Authentication

* User Registration
* Login
* JWT Authentication
* Refresh Token
* Logout
* Password Change
* Password Reset
* Role-Based Access Control

### Customer Management

* Customer Registration
* Customer Profile
* Contact & Address Management
* KYC Management
* Customer Status
* Customer History

### Telecom Management

* Service Plans
* SIM Cards
* Devices
* Subscriptions
* Usage Tracking

### Network Management

* Network Towers
* Network Equipment
* Network Outages
* Field Technicians

### Support Management

* Support Tickets
* Ticket Assignment
* Ticket Priority
* Ticket Escalation
* Ticket Comments
* Ticket History
* SLA Monitoring

### Service Requests

* SIM Replacement
* Number Change
* Plan Change
* Device Replacement
* Service Activation
* Service Suspension
* Service Termination

### Reports & Dashboard

* Operations Dashboard
* Customer Growth
* Subscription Trends
* Plan Popularity
* Data Consumption
* Network Uptime
* Outage Reports
* Ticket Reports
* SLA Reports
* Technician Reports

### Security & Audit

* JWT Security
* Password Hashing
* RBAC
* Request Validation
* Rate Limiting
* Database Transactions
* Audit Logs
* Soft Delete

### Testing

* Unit Tests
* Integration Tests
* Authentication Tests
* RBAC Tests
* Validation Tests
* Database Tests
* Test Coverage

## Project Structure

```text
telecom_service_management/
│
├── app/
│   ├── models/
│   ├── schemas/
│   ├── repositories/
│   ├── services/
│   ├── routes/
│   ├── utils/
│   ├── main.py
│   ├── config.py
│   └── database.py
│
├── tests/
│   ├── unit/
│   └── integration/
│
├── alembic/
│
├── Dockerfile
├── docker-compose.yml
├── .env
├── .env.example
├── .gitignore
├── pytest.ini
├── requirements.txt
├── seed_admin.py
└── README.md
```

## Installation

### 1. Clone the Project

```bash
git clone <your-github-repository-url>
cd telecom_service_management
```

### 2. Create Virtual Environment

```powershell
python -m venv venv
```

Activate:

```powershell
venv\Scripts\activate
```

### 3. Install Requirements

```powershell
pip install -r requirements.txt
```

### 4. Create Environment File

```powershell
Copy-Item .env.example .env
```

Update the values in `.env`.

### 5. Run Database Migration

```powershell
alembic upgrade head
```

### 6. Create Admin User

```powershell
python seed_admin.py
```

### 7. Run Application

```powershell
uvicorn app.main:app --reload
```

## API Documentation

Swagger:

```text
http://127.0.0.1:8000/docs
```

ReDoc:

```text
http://127.0.0.1:8000/redoc
```

## Run Tests

Run all tests:

```powershell
pytest -v
```

Run unit tests:

```powershell
pytest tests/unit -v
```

Run integration tests:

```powershell
pytest tests/integration -v
```

Run coverage:

```powershell
pytest --cov=app --cov-report=term-missing
```

## Docker

Build and run:

```powershell
docker compose up --build
```

Run in background:

```powershell
docker compose up -d
```

Stop containers:

```powershell
docker compose down
```

## Database Migration

Create migration:

```powershell
alembic revision --autogenerate -m "migration message"
```

Apply migration:

```powershell
alembic upgrade head
```

Rollback:

```powershell
alembic downgrade -1
```

## API Flow

```text
User
  ↓
Authentication
  ↓
JWT Token
  ↓
Role Validation
  ↓
API Route
  ↓
Service
  ↓
Repository
  ↓
PostgreSQL
```

## Security

The application uses:

* JWT Authentication
* Argon2 Password Hashing
* Role-Based Access Control
* Request Validation
* Rate Limiting
* Environment Variables
* Audit Logging

## Author

**Manikandan**

Python / FastAPI Backend Project
