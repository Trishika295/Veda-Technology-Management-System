import os
import io
import csv
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any, List
import bcrypt
import jwt
from fastapi import HTTPException, status, Header
from app.database import get_db, record_activity, serialize_doc
from app.models import (
    PREFIX_USER,
    PREFIX_PROGRAM,
    PREFIX_SERVICE,
    PREFIX_TRAINING,
    PREFIX_INTERNSHIP,
    PREFIX_CUSTOMER,
    PREFIX_INQUIRY,
    PREFIX_REQUEST,
    PREFIX_ACTIVITY
)

# JWT Configurations
SECRET_KEY = os.getenv("SECRET_KEY", "veda-technology-super-secure-production-key-2026")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours


# ==========================================
# PASSWORD HASHING
# ==========================================

def hash_password(password: str) -> str:
    """Hashes a password with bcrypt."""
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain password against bcrypt hash."""
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
    except Exception:
        return False


# ==========================================
# JWT TOKEN HANDLING
# ==========================================

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Encodes JWT payload with expiration."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_current_user_from_token(authorization: Optional[str] = Header(None)) -> Optional[Dict[str, Any]]:
    """Extracts and verifies current user from the Authorization: Bearer <token> header."""
    if not authorization or not authorization.startswith("Bearer "):
        return None
    token = authorization.split(" ")[1]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if not email:
            return None
        db = get_db()
        user = db.users.find_one({"email": email})
        if user:
            return serialize_doc(user)
    except jwt.PyJWTError:
        return None
    return None


def require_auth_user(authorization: Optional[str] = Header(None)) -> Dict[str, Any]:
    """Requires an authenticated user or raises HTTP 401."""
    user = get_current_user_from_token(authorization)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token is missing, invalid, or expired.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


# ==========================================
# ID GENERATION
# ==========================================

def generate_entity_id(collection_name: str, prefix: str) -> str:
    """Generates sequential ID like PRG-1001, SRV-1001, etc."""
    db = get_db()
    count = db[collection_name].count_documents({})
    id_field_map = {
        "users": "user_id",
        "programs": "program_id",
        "services": "service_id",
        "training_programs": "program_id",
        "customers": "customer_id",
        "inquiries": "inquiry_id",
        "service_requests": "request_id",
        "activity_logs": "activity_id"
    }
    field = id_field_map.get(collection_name, "id")
    candidate_num = 1001 + count
    while db[collection_name].find_one({field: f"{prefix}-{candidate_num}"}):
        candidate_num += 1
    return f"{prefix}-{candidate_num}"


# ==========================================
# CSV EXPORTER HELPER
# ==========================================

def generate_csv_data(module: str) -> str:
    """Exports records from a given module into CSV text."""
    db = get_db()
    output = io.StringIO()
    writer = csv.writer(output)

    if module == "programs":
        writer.writerow(["Program ID", "Name", "Category", "Status", "Start Date", "End Date", "Description"])
        records = db.programs.find({}).sort("created_at", -1)
        for r in records:
            writer.writerow([
                r.get("program_id", ""),
                r.get("name", ""),
                r.get("category", ""),
                r.get("status", ""),
                r.get("start_date", ""),
                r.get("end_date", ""),
                r.get("description", "")
            ])

    elif module == "services":
        writer.writerow(["Service ID", "Name", "Category", "Availability Status", "Assigned Team", "Description"])
        records = db.services.find({}).sort("created_at", -1)
        for r in records:
            writer.writerow([
                r.get("service_id", ""),
                r.get("name", ""),
                r.get("category", ""),
                r.get("availability_status", ""),
                r.get("assigned_team", ""),
                r.get("description", "")
            ])

    elif module == "training":
        writer.writerow(["Program ID", "Title", "Type", "Status", "Duration", "Eligibility", "Available Seats", "Deadline"])
        records = db.training_programs.find({}).sort("created_at", -1)
        for r in records:
            writer.writerow([
                r.get("program_id", ""),
                r.get("title", ""),
                r.get("program_type", ""),
                r.get("status", ""),
                r.get("duration", ""),
                r.get("eligibility", ""),
                r.get("available_seats", ""),
                r.get("application_deadline", "")
            ])

    elif module == "customers":
        writer.writerow(["Customer ID", "Name", "Organization", "Email", "Phone", "Category"])
        records = db.customers.find({}).sort("created_at", -1)
        for r in records:
            writer.writerow([
                r.get("customer_id", ""),
                r.get("name", ""),
                r.get("organization", ""),
                r.get("email", ""),
                r.get("phone", ""),
                r.get("customer_category", "")
            ])

    elif module == "inquiries":
        writer.writerow(["Inquiry ID", "Customer Name", "Subject", "Category", "Priority", "Status", "Assigned Team", "Description"])
        records = db.inquiries.find({}).sort("created_at", -1)
        for r in records:
            writer.writerow([
                r.get("inquiry_id", ""),
                r.get("customer_name", ""),
                r.get("subject", ""),
                r.get("category", ""),
                r.get("priority", ""),
                r.get("status", ""),
                r.get("assigned_team", ""),
                r.get("description", "")
            ])

    elif module == "service_requests":
        writer.writerow(["Request ID", "Title", "Category", "Priority", "Status", "Customer Reference", "Assigned Team", "Description"])
        records = db.service_requests.find({}).sort("created_at", -1)
        for r in records:
            writer.writerow([
                r.get("request_id", ""),
                r.get("title", ""),
                r.get("request_category", ""),
                r.get("priority", ""),
                r.get("status", ""),
                r.get("customer_reference", ""),
                r.get("assigned_team", ""),
                r.get("description", "")
            ])

    elif module == "activity":
        writer.writerow(["Activity ID", "Action", "Module", "Record ID", "Description", "Timestamp", "User"])
        records = db.activity_logs.find({}).sort("timestamp", -1)
        for r in records:
            ts = r.get("timestamp")
            ts_str = ts.isoformat() if isinstance(ts, datetime) else str(ts)
            writer.writerow([
                r.get("activity_id", ""),
                r.get("action", ""),
                r.get("module", ""),
                r.get("record_id", ""),
                r.get("description", ""),
                ts_str,
                r.get("user_identifier", "")
            ])
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported module '{module}' for CSV export.")

    return output.getvalue()


# ==========================================
# SEEDING DATABASE
# ==========================================

def seed_database_if_empty():
    """Populates MongoDB with realistic, professional Veda Technology synthetic seed data if empty."""
    db = get_db()

    # 1. Default Admin User
    if not db.users.find_one({"email": "admin@vedatechnology.com"}):
        admin_id = "USR-1001"
        if db.users.find_one({"user_id": admin_id}):
            admin_id = generate_entity_id("users", PREFIX_USER)
        admin_user = {
            "user_id": admin_id,
            "name": "Admin Officer",
            "email": "admin@vedatechnology.com",
            "password_hash": hash_password("Admin@123"),
            "role": "Admin",
            "created_at": datetime.now(timezone.utc)
        }
        db.users.insert_one(admin_user)
        print(f"[SEED] Default admin user seeded with ID {admin_id} (admin@vedatechnology.com / Admin@123)")

    now = datetime.now(timezone.utc)

    # 2. Technology Programs
    if db.programs.count_documents({}) == 0:
        sample_programs = [
            {
                "program_id": "PRG-1001",
                "name": "Enterprise Cloud & DevOps Acceleration",
                "description": "Comprehensive corporate initiative for container orchestration, Kubernetes architecture, and multi-cloud CI/CD automation pipelines.",
                "category": "Cloud & DevOps",
                "start_date": "2026-01-15",
                "end_date": "2026-06-30",
                "status": "Active",
                "created_at": now - timedelta(days=45),
                "updated_at": now - timedelta(days=10)
            },
            {
                "program_id": "PRG-1002",
                "name": "Generative AI & Agentic Systems Hub",
                "description": "Strategic development program integrating modern LLM workflows, autonomous agents, and enterprise knowledge extraction.",
                "category": "AI & Machine Learning",
                "start_date": "2026-02-01",
                "end_date": "2026-11-30",
                "status": "Active",
                "created_at": now - timedelta(days=35),
                "updated_at": now - timedelta(days=5)
            },
            {
                "program_id": "PRG-1003",
                "name": "Zero-Trust Cybersecurity Resilience",
                "description": "End-to-end organizational security modernization framework, pen-testing validation, and identity-driven access policies.",
                "category": "Cybersecurity",
                "start_date": "2026-03-10",
                "end_date": "2026-09-15",
                "status": "Planned",
                "created_at": now - timedelta(days=20),
                "updated_at": now - timedelta(days=20)
            },
            {
                "program_id": "PRG-1004",
                "name": "Full-Stack Enterprise React & Python Ecosystem",
                "description": "Cross-functional modernization of legacy service portals into scalable FastAPI backends and high-performance React frontends.",
                "category": "Full Stack Development",
                "start_date": "2025-08-01",
                "end_date": "2026-01-10",
                "status": "Completed",
                "created_at": now - timedelta(days=90),
                "updated_at": now - timedelta(days=60)
            },
            {
                "program_id": "PRG-1005",
                "name": "Distributed Big Data Lakehouse Initiative",
                "description": "Real-time streaming pipelines, Apache Spark transformations, and modern data warehousing architectures for client analytics.",
                "category": "Data Engineering",
                "start_date": "2026-04-01",
                "end_date": "2026-12-15",
                "status": "Planned",
                "created_at": now - timedelta(days=12),
                "updated_at": now - timedelta(days=12)
            }
        ]
        db.programs.insert_many(sample_programs)
        record_activity("CREATE", "Programs", "Initialized synthetic Technology Programs", "PRG-SEED", "System")
        print("[SEED] Technology Programs seeded successfully.")

    # 3. Digital Services
    if db.services.count_documents({}) == 0:
        sample_services = [
            {
                "service_id": "SRV-1001",
                "name": "Cloud Infrastructure & Migration Suite",
                "description": "Turnkey AWS, Azure, and GCP multi-cloud infrastructure provisioning, serverless deployment, and cost optimization.",
                "category": "Cloud Migration",
                "availability_status": "Available",
                "assigned_team": "Cloud Solutions",
                "created_at": now - timedelta(days=50),
                "updated_at": now - timedelta(days=15)
            },
            {
                "service_id": "SRV-1002",
                "name": "AI Automation & Custom Chatbots",
                "description": "Production-ready enterprise conversational assistants, intelligent document processing, and predictive analytics models.",
                "category": "AI Automation",
                "availability_status": "Available",
                "assigned_team": "AI Labs",
                "created_at": now - timedelta(days=40),
                "updated_at": now - timedelta(days=8)
            },
            {
                "service_id": "SRV-1003",
                "name": "Full-Lifecycle Custom Software Development",
                "description": "Bespoke SaaS platforms, API microservices, ERP dashboards, and mobile responsive enterprise applications.",
                "category": "Custom Software Development",
                "availability_status": "Available",
                "assigned_team": "Engineering Core",
                "created_at": now - timedelta(days=60),
                "updated_at": now - timedelta(days=20)
            },
            {
                "service_id": "SRV-1004",
                "name": "Vulnerability Assessment & Pen-Testing",
                "description": "Comprehensive compliance audits, web application penetration tests, and network vulnerability hardening.",
                "category": "Security Audit",
                "availability_status": "Available",
                "assigned_team": "Security Ops",
                "created_at": now - timedelta(days=30),
                "updated_at": now - timedelta(days=10)
            },
            {
                "service_id": "SRV-1005",
                "name": "Next-Gen Intelligent Edge Computing Platform",
                "description": "Ultra low-latency IoT gateway processing and edge telemetry management system currently in trial testing.",
                "category": "IT Consulting",
                "availability_status": "Beta",
                "assigned_team": "AI Labs",
                "created_at": now - timedelta(days=15),
                "updated_at": now - timedelta(days=2)
            }
        ]
        db.services.insert_many(sample_services)
        record_activity("CREATE", "Services", "Initialized synthetic Digital Services", "SRV-SEED", "System")
        print("[SEED] Digital Services seeded successfully.")

    # 4. Training and Internship Programs
    if db.training_programs.count_documents({}) == 0:
        sample_training = [
            {
                "program_id": "TRN-1001",
                "title": "Full Stack Web Engineering Bootcamp",
                "program_type": "Training",
                "description": "Intensive hands-on training curriculum covering modern React, Node/Python backends, REST APIs, and database design.",
                "duration": "12 Weeks",
                "eligibility": "B.Tech / BCA / MCA students or tech enthusiasts with basic programming background",
                "available_seats": 35,
                "application_deadline": "2026-11-15",
                "status": "Open",
                "created_at": now - timedelta(days=25),
                "updated_at": now - timedelta(days=5)
            },
            {
                "program_id": "INT-1002",
                "title": "Graduate Cloud & DevOps Engineering Internship",
                "program_type": "Internship",
                "description": "6-month immersive internship tackling real-world cloud deployment, Docker containers, Kubernetes clusters, and CI/CD pipelines.",
                "duration": "6 Months",
                "eligibility": "Final year undergraduate or recent graduates in Computer Science / IT",
                "available_seats": 15,
                "application_deadline": "2026-11-30",
                "status": "Open",
                "created_at": now - timedelta(days=20),
                "updated_at": now - timedelta(days=2)
            },
            {
                "program_id": "TRN-1003",
                "title": "Applied Artificial Intelligence & Machine Learning",
                "program_type": "Training",
                "description": "Deep dive into PyTorch, Scikit-learn, LLM fine-tuning, and retrieval-augmented generation applications.",
                "duration": "8 Weeks",
                "eligibility": "Familiarity with Python syntax and foundational linear algebra / statistics",
                "available_seats": 25,
                "application_deadline": "2026-12-05",
                "status": "Upcoming",
                "created_at": now - timedelta(days=10),
                "updated_at": now - timedelta(days=10)
            },
            {
                "program_id": "INT-1004",
                "title": "Cybersecurity & Threat Detection Internship",
                "program_type": "Internship",
                "description": "Practical security operations internship focusing on SIEM log analysis, ethical hacking drills, and vulnerability tracking.",
                "duration": "4 Months",
                "eligibility": "Students with coursework in Networking, Linux Administration, and OS Security",
                "available_seats": 10,
                "application_deadline": "2026-10-30",
                "status": "Open",
                "created_at": now - timedelta(days=18),
                "updated_at": now - timedelta(days=4)
            },
            {
                "program_id": "TRN-1005",
                "title": "Python Data Engineering & Analytics Mastery",
                "program_type": "Training",
                "description": "Foundational cohort completed earlier this quarter on Pandas, SQL analytics, and automated pipeline scheduling.",
                "duration": "6 Weeks",
                "eligibility": "Open to all STEM students and junior analysts",
                "available_seats": 0,
                "application_deadline": "2026-08-30",
                "status": "Completed",
                "created_at": now - timedelta(days=70),
                "updated_at": now - timedelta(days=30)
            }
        ]
        db.training_programs.insert_many(sample_training)
        record_activity("CREATE", "Training", "Initialized synthetic Training & Internship opportunities", "TRN-SEED", "System")
        print("[SEED] Training & Internships seeded successfully.")

    # 5. Customers
    if db.customers.count_documents({}) == 0:
        sample_customers = [
            {
                "customer_id": "CST-1001",
                "name": "Apex Digital Solutions Ltd.",
                "organization": "Apex Enterprise Group",
                "email": "contact@apexdigital.org",
                "phone": "+91 98765 43210",
                "customer_category": "Enterprise",
                "created_at": now - timedelta(days=40),
                "updated_at": now - timedelta(days=15)
            },
            {
                "customer_id": "CST-1002",
                "name": "Kavya Murthy",
                "organization": "NexGen AI Labs",
                "email": "kavya.murthy@nexgenlabs.io",
                "phone": "+91 98111 22334",
                "customer_category": "Startup",
                "created_at": now - timedelta(days=32),
                "updated_at": now - timedelta(days=10)
            },
            {
                "customer_id": "CST-1003",
                "name": "Horizon Institute of Technology",
                "organization": "Horizon University",
                "email": "placements@horizontech.edu",
                "phone": "+91 94455 66778",
                "customer_category": "Academic",
                "created_at": now - timedelta(days=28),
                "updated_at": now - timedelta(days=8)
            },
            {
                "customer_id": "CST-1004",
                "name": "Rohan Mehra",
                "organization": "Mehra Retail Logistics",
                "email": "rohan@mehra-retail.com",
                "phone": "+91 97788 99001",
                "customer_category": "SME",
                "created_at": now - timedelta(days=14),
                "updated_at": now - timedelta(days=3)
            },
            {
                "customer_id": "CST-1005",
                "name": "Pooja Sharma",
                "organization": None,
                "email": "pooja.sharma.dev@gmail.com",
                "phone": "+91 96543 21098",
                "customer_category": "Individual",
                "created_at": now - timedelta(days=7),
                "updated_at": now - timedelta(days=7)
            }
        ]
        db.customers.insert_many(sample_customers)
        record_activity("CREATE", "Customers", "Initialized synthetic Customer records", "CST-SEED", "System")
        print("[SEED] Customers seeded successfully.")

    # 6. Inquiries
    if db.inquiries.count_documents({}) == 0:
        sample_inquiries = [
            {
                "inquiry_id": "INQ-1001",
                "customer_name": "Apex Digital Solutions Ltd.",
                "customer_id": "CST-1001",
                "subject": "Request for Cloud Architecture Migration proposal",
                "description": "Seeking architectural review and phased migration quote for moving our on-premise Oracle workloads to AWS ECS and RDS.",
                "category": "Digital Service",
                "priority": "High",
                "status": "In Progress",
                "assigned_team": "Cloud Solutions",
                "created_at": now - timedelta(days=18),
                "updated_at": now - timedelta(days=2)
            },
            {
                "inquiry_id": "INQ-1002",
                "customer_name": "Horizon Institute of Technology",
                "customer_id": "CST-1003",
                "subject": "Campus Training & Internship Collaboration",
                "description": "Inquiring about conducting a 50-student specialized Full Stack Web Engineering cohort for our 3rd year engineering students.",
                "category": "Training / Internship",
                "priority": "Medium",
                "status": "New",
                "assigned_team": "Admissions Desk",
                "created_at": now - timedelta(days=5),
                "updated_at": now - timedelta(days=5)
            },
            {
                "inquiry_id": "INQ-1003",
                "customer_name": "Kavya Murthy",
                "customer_id": "CST-1002",
                "subject": "Agentic AI Integration Consultation",
                "description": "Looking for guidance on leveraging Veda's AI automation framework to speed up customer ticket triage.",
                "category": "Technology Program",
                "priority": "Medium",
                "status": "Resolved",
                "assigned_team": "AI Labs",
                "created_at": now - timedelta(days=22),
                "updated_at": now - timedelta(days=3)
            },
            {
                "inquiry_id": "INQ-1004",
                "customer_name": "Pooja Sharma",
                "customer_id": "CST-1005",
                "subject": "Cybersecurity Internship Application Query",
                "description": "Checking whether students with Linux networking background from non-CS streams are eligible for the threat detection program.",
                "category": "Training / Internship",
                "priority": "Low",
                "status": "Closed",
                "assigned_team": "Admissions Desk",
                "created_at": now - timedelta(days=12),
                "updated_at": now - timedelta(days=6)
            }
        ]
        db.inquiries.insert_many(sample_inquiries)
        record_activity("CREATE", "Inquiries", "Initialized synthetic Customer Inquiries", "INQ-SEED", "System")
        print("[SEED] Customer Inquiries seeded successfully.")

    # 7. Service Requests
    if db.service_requests.count_documents({}) == 0:
        sample_requests = [
            {
                "request_id": "REQ-1001",
                "title": "Automated Docker Registry Security Hardening",
                "description": "Configure image signing, vulnerability vulnerability scanning in GitHub Actions, and policy enforcement.",
                "request_category": "Infrastructure Setup",
                "priority": "High",
                "status": "In Progress",
                "customer_reference": "Apex Digital Solutions Ltd.",
                "assigned_team": "DevOps Unit",
                "created_at": now - timedelta(days=14),
                "updated_at": now - timedelta(days=1)
            },
            {
                "request_id": "REQ-1002",
                "title": "Payment Webhook Reliability & Dead Letter Queue Setup",
                "description": "Address rare timeout spikes during high concurrency by placing incoming payment callbacks into RabbitMQ DLQ.",
                "request_category": "Bug Fix & Maintenance",
                "priority": "Medium",
                "status": "Open",
                "customer_reference": "Rohan Mehra",
                "assigned_team": "Software Solutions",
                "created_at": now - timedelta(days=4),
                "updated_at": now - timedelta(days=4)
            },
            {
                "request_id": "REQ-1003",
                "title": "Single Sign-On (SSO) SAML Integration",
                "description": "Implement Okta and Google Workspace SAML 2.0 authentication for customer admin portals.",
                "request_category": "System Integration",
                "priority": "High",
                "status": "Resolved",
                "customer_reference": "NexGen AI Labs",
                "assigned_team": "Software Solutions",
                "created_at": now - timedelta(days=26),
                "updated_at": now - timedelta(days=7)
            },
            {
                "request_id": "REQ-1004",
                "title": "CloudWatch Cost & Resource Anomaly Alarms",
                "description": "Create automated alarms and Slack alert webhooks when cloud spending exceeds threshold targets.",
                "request_category": "Cloud Deployment",
                "priority": "Low",
                "status": "Closed",
                "customer_reference": "Apex Digital Solutions Ltd.",
                "assigned_team": "DevOps Unit",
                "created_at": now - timedelta(days=35),
                "updated_at": now - timedelta(days=20)
            }
        ]
        db.service_requests.insert_many(sample_requests)
        record_activity("CREATE", "Service Requests", "Initialized synthetic Service Requests", "REQ-SEED", "System")
        print("[SEED] Service Requests seeded successfully.")
