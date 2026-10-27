import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check():
    """Verify that the health check endpoint returns 200 and healthy status."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "database" in data


def test_dashboard_metrics():
    """Verify that the dashboard endpoint returns realistic aggregated data."""
    response = client.get("/api/dashboard")
    assert response.status_code == 200
    data = response.json()
    assert "total_programs" in data
    assert "total_services" in data
    assert "total_training_programs" in data
    assert "open_service_requests" in data
    assert isinstance(data["recently_created"], list)
    assert isinstance(data["recent_activity"], list)


def test_programs_crud_lifecycle():
    """Verify creating, reading, updating, and deleting a Technology Program."""
    # 1. Create
    payload = {
        "name": "Test DevOps Pipeline Modernization",
        "description": "Automated integration testing for microservices infrastructure.",
        "category": "Cloud & DevOps",
        "start_date": "2026-05-01",
        "end_date": "2026-10-01",
        "status": "Planned"
    }
    create_res = client.post("/api/programs", json=payload)
    assert create_res.status_code == 201
    created_data = create_res.json()
    program_id = created_data["program_id"]
    doc_id = created_data["id"]
    assert created_data["name"] == payload["name"]

    # 2. Read
    get_res = client.get(f"/api/programs/{program_id}")
    assert get_res.status_code == 200
    assert get_res.json()["program_id"] == program_id

    # 3. Update
    update_res = client.put(f"/api/programs/{program_id}", json={"status": "Active"})
    assert update_res.status_code == 200
    assert update_res.json()["status"] == "Active"

    # 4. Search
    search_res = client.get("/api/programs?search=DevOps")
    assert search_res.status_code == 200
    items = search_res.json()
    assert any(p["program_id"] == program_id for p in items)

    # 5. Delete
    del_res = client.delete(f"/api/programs/{program_id}")
    assert del_res.status_code == 200

    # Verify not found
    verify_del = client.get(f"/api/programs/{program_id}")
    assert verify_del.status_code == 404


def test_customer_inquiry_and_status_change():
    """Verify creating inquiry and updating status which logs an activity."""
    inquiry_data = {
        "customer_name": "Test University Partner",
        "subject": "Campus Recruitment & Workshop Query",
        "description": "Details regarding corporate training dates and student enrollment.",
        "category": "Training / Internship",
        "priority": "High",
        "status": "New",
        "assigned_team": "Admissions Desk"
    }
    res = client.post("/api/inquiries", json=inquiry_data)
    assert res.status_code == 201
    inquiry = res.json()
    inq_id = inquiry["inquiry_id"]

    # Update status
    patch_res = client.put(f"/api/inquiries/{inq_id}", json={"status": "In Progress"})
    assert patch_res.status_code == 200
    assert patch_res.json()["status"] == "In Progress"

    # Cleanup
    client.delete(f"/api/inquiries/{inq_id}")


def test_reports_and_csv_export():
    """Verify reports aggregation and CSV export."""
    reports_res = client.get("/api/reports")
    assert reports_res.status_code == 200
    rep_data = reports_res.json()
    assert "programs_by_status" in rep_data
    assert "training_vs_internship" in rep_data

    # Test CSV export for services
    csv_res = client.get("/api/reports/export-csv?module=services")
    assert csv_res.status_code == 200
    assert "text/csv" in csv_res.headers["content-type"]
    assert "Service ID" in csv_res.text


def test_activity_history():
    """Verify activity history endpoint returns logged activities."""
    act_res = client.get("/api/activity")
    assert act_res.status_code == 200
    data = act_res.json()
    assert "total" in data
    assert "items" in data
    assert len(data["items"]) > 0


def test_auth_registration_and_login():
    """Verify user registration, login, and protected route access."""
    import time
    ts = int(time.time())
    email = f"officer_{ts}@vedatechnology.com"
    reg_payload = {
        "name": f"Operations Officer {ts}",
        "email": email,
        "password": "Password123!",
        "role": "Manager"
    }
    reg_res = client.post("/api/auth/register", json=reg_payload)
    assert reg_res.status_code == 201
    reg_data = reg_res.json()
    token = reg_data["access_token"]
    assert token is not None

    # Verify /me with token
    me_res = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_res.status_code == 200
    assert me_res.json()["email"] == email

    # Verify login
    login_res = client.post("/api/auth/login", json={"email": email, "password": "Password123!"})
    assert login_res.status_code == 200
    assert "access_token" in login_res.json()

