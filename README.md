# Veda Technology Business & Service Management System

A full-stack, enterprise-grade business and digital services operations portal built for **Veda Technology**. The system coordinates technology programs, digital services, training programs, internship cohorts, customer accounts, inquiry ticketing, service requests, operational reports, CSV exports, and persistent MongoDB activity audit history.

- **Frontend**: Streamlit enterprise dashboard (`frontend/`)
- **Backend**: FastAPI REST API (`backend/`)
- **Database**: MongoDB persistent document database (`veda_business_management`)

---

## 1. Project Overview & Features

### Core Modules
1. **Executive Dashboard**: Live telemetry fetching real-time statistics from MongoDB (total programs, digital services, training/internship cohorts, open inquiries, pending service requests, recently created records, and live activity audit logs).
2. **Technology Program Management**: Full CRUD lifecycle for strategic tech initiatives (e.g., Cloud & DevOps, Generative AI, Cybersecurity). Filter by category and status with instant keyword search.
3. **Digital Service Management**: Catalog of client solutions and services with availability statuses (`Available`, `In Development`, `Beta`, `Deprecated`) and assigned engineering teams.
4. **Training & Internship Management**: Academic bootcamps and student internship cohorts with seat quotas, eligibility criteria, application deadlines, and statuses (`Upcoming`, `Open`, `Closed`, `Completed`).
5. **Customer Management**: Corporate client directories, institutional partners, and contact profiles with email format validation and categorical sorting.
6. **Customer Inquiry Management**: Inquiry ticket triage with urgency priorities (`Low`, `Medium`, `High`), resolution stages (`New`, `In Progress`, `Resolved`, `Closed`), and assignment to internal units.
7. **Service Request Management**: Dedicated technical work order tracker with quick status dropdowns and customer references.
8. **Business Reports & CSV Exports**: Visual aggregations, status distributions, category representations, training-to-internship ratios, and one-click direct CSV export for all 7 business modules.
9. **Persistent Activity History**: Immutable audit log stored directly in MongoDB recording all record creations, edits, deletions, status transitions, and data exports with user attribution.
10. **Authentication & Access Control**: Secure JWT-based token authentication with bcrypt password hashing and an autofill demo button for evaluation.

---

## 2. Technology Stack

- **Frontend**: Streamlit 1.35+, Python, Streamlit Session State, Custom Enterprise CSS, Pandas (`frontend/`).
- **Backend**: Python 3.12+, FastAPI, Pydantic v2, PyMongo, PyJWT, Bcrypt (`backend/`).
- **Database**: MongoDB (Local instance on port 27017 or MongoDB Atlas), database `veda_business_management`.
- **Testing**: Pytest & FastAPI TestClient.

---

## 3. Directory Structure

```
PythonProject2/
├── frontend/                        # Streamlit Enterprise Frontend
│   ├── app.py                       # Main Streamlit application entrypoint & auth router
│   ├── api_client.py                # Reusable Python REST API client with JWT support
│   ├── styles.py                    # Custom enterprise CSS, badge styles & theme tokens
│   ├── components.py                # Reusable KPI stat cards, headers & empty states
│   ├── icons.py                     # SVG icons & helpers
│   ├── requirements.txt             # Streamlit frontend dependencies
│   ├── .streamlit/
│   │   └── config.toml              # Streamlit theme and server configuration
│   └── views/
│       ├── dashboard.py             # Executive dashboard & live telemetry
│       ├── programs.py              # Technology program CRUD & search
│       ├── services.py              # Digital services catalog & team tracking
│       ├── training_internships.py  # Training & internship cohort management
│       ├── customers.py             # Customer directory & contact management
│       ├── inquiries.py             # Customer inquiries & quick status transitions
│       ├── service_requests.py      # Technical service requests & work orders
│       ├── reports.py               # Strategic analytics & direct CSV exports
│       └── activity_history.py      # Persistent MongoDB audit logs with pagination
├── backend/                         # FastAPI REST API & MongoDB Data Layer
│   ├── app/
│   │   ├── routes/                  # API routers (auth, dashboard, programs, etc.)
│   │   ├── database.py              # PyMongo connection, indexes & audit logging
│   │   ├── models.py                # Constants, prefixes & collection definitions
│   │   ├── schemas.py               # Pydantic v2 validation models
│   │   ├── services.py              # Business logic, password hashing & seeding
│   │   └── main.py                  # FastAPI app & CORS middleware
│   ├── tests/
│   │   └── test_api.py              # Pytest automated test suite
│   ├── requirements.txt             # Backend dependencies
│   └── .env                         # Backend environment variables
├── .gitignore
├── .env.example
└── README.md
```

---

## 4. Setup and Execution Instructions (VS Code on Windows)

### Prerequisites
- **Python**: Python 3.11, 3.12, 3.13, or 3.14 (`python --version` or `py --version`).
- **MongoDB**: MongoDB Community Server running locally on port 27017, or a free MongoDB Atlas connection string.

---

### Step 1: Backend Setup & Execution

Open a PowerShell terminal in VS Code:

1. Navigate to the backend directory:
   ```powershell
   cd backend
   ```

2. Activate virtual environment:
   ```powershell
   .\.venv\Scripts\activate
   ```

3. Install required dependencies:
   ```powershell
   pip install -r requirements.txt
   ```

4. Start the FastAPI backend server:
   ```powershell
   uvicorn app.main:app --host 127.0.0.1 --port 8000
   ```
   - **Backend API**: `http://127.0.0.1:8000`
   - **Swagger UI Documentation**: `http://127.0.0.1:8000/docs`

---

### Step 2: Streamlit Frontend Execution

Open a second PowerShell terminal in VS Code:

1. Install Streamlit frontend dependencies:
   ```powershell
   pip install -r frontend\requirements.txt
   ```

2. Start the Streamlit application:
   ```powershell
   streamlit run frontend\app.py
   ```
   The application will be accessible at: **`http://localhost:8501`**

---

### Step 3: Accessing the Application & Demo Credentials

1. Open your browser and navigate to: **`http://localhost:8501`**
2. You will see the secure Veda Technology enterprise login screen.
3. Click the **"Autofill Admin Credentials"** button or enter:
   - **Email:** `admin@vedatechnology.com`
   - **Password:** `Admin@123`
4. Use the sidebar navigation to access all 9 operational modules.

---

## 5. Running Automated Backend & E2E Tests

### 1. Pytest Backend Suite
```powershell
cd backend
.\.venv\Scripts\python.exe -m pytest tests -v
```

### 2. End-to-End Streamlit API Client Suite
```powershell
py -c "
import sys; sys.path.insert(0, 'frontend')
from api_client import api
h = api.check_health(); assert h['status'] == 'healthy'
print('Health OK:', h)
"
```

---

## 6. Common Errors & Troubleshooting

| Issue | Cause | Solution |
|---|---|---|
| `MongoDB connection refused / timeout` | MongoDB service is not started | Start the MongoDB Windows service (`net start MongoDB`) or run `mongod` in a terminal. |
| `Script execution is disabled on this system` in PowerShell | Windows ExecutionPolicy restriction | Run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` before activating `.venv`. |
| `Cannot connect to backend server` in Streamlit | FastAPI server is not running on port 8000 | Ensure `uvicorn app.main:app --host 127.0.0.1 --port 8000` is running in your backend terminal. |
| `Port 8501 already in use` | Another Streamlit process is running | Run with `--server.port 8502` or terminate the existing process. |

---

## 7. System Verification

- [x] Streamlit frontend starts successfully on `http://localhost:8501`
- [x] FastAPI backend running on `http://127.0.0.1:8000`
- [x] MongoDB database connection and persistent storage (`veda_business_management`)
- [x] All 9 application modules accessible through sidebar navigation
- [x] Full CRUD operations verified for Programs, Services, Training, Customers, Inquiries, and Service Requests
- [x] Search and multi-parameter filtering working across all modules
- [x] Quick status transitions for Inquiries and Service Requests
- [x] Strategic analytics and direct 1-click CSV downloads for all 7 modules
- [x] Persistent activity audit history maintained with pagination
- [x] JWT token-based authentication and demo credentials autofill working
- [x] Clean, simplified project structure (Streamlit frontend, Python backend, and database layer)
