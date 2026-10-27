from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import init_db_indexes, get_db
from app.services import seed_database_if_empty
from app.routes import (
    auth,
    dashboard,
    programs,
    services,
    training,
    customers,
    inquiries,
    service_requests,
    reports,
    activity
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Ensure MongoDB connection, indexes, and synthetic seed data
    print("[STARTUP] Initializing Veda Technology backend...")
    init_db_indexes()
    seed_database_if_empty()
    print("[STARTUP] Backend initialization complete.")
    yield
    print("[SHUTDOWN] Shutting down Veda Technology backend.")


app = FastAPI(
    title="Veda Technology Business & Service Management System API",
    description="Full-stack enterprise service and technology operations API for Veda Technology.",
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health endpoint
@app.get("/api/health", tags=["Health"])
def health_check():
    db = get_db()
    try:
        db.command("ping")
        db_status = "connected"
    except Exception as e:
        db_status = f"unreachable: {str(e)}"
    return {
        "status": "healthy",
        "application": "Veda Technology Business & Service Management System",
        "database": db_status
    }


# Root route for users who open port 8000 in browser
@app.get("/", tags=["Root"])
def root():
    return {
        "system": "Veda Technology Business & Service Management System API",
        "status": "Backend running successfully",
        "frontend_url": "http://127.0.0.1:5173",
        "api_documentation": "http://127.0.0.1:8000/docs",
        "message": "To view the user interface dashboard, open the Frontend URL in your browser: http://127.0.0.1:5173"
    }



# Manual re-seed endpoint
@app.post("/api/seed", tags=["Database Management"])
def seed_data():
    seed_database_if_empty()
    return {"message": "Database check and seeding verified successfully."}


# Mount all modular routers under /api
app.include_router(auth.router, prefix="/api")
app.include_router(dashboard.router, prefix="/api")
app.include_router(programs.router, prefix="/api")
app.include_router(services.router, prefix="/api")
app.include_router(training.router, prefix="/api")
app.include_router(customers.router, prefix="/api")
app.include_router(inquiries.router, prefix="/api")
app.include_router(service_requests.router, prefix="/api")
app.include_router(reports.router, prefix="/api")
app.include_router(activity.router, prefix="/api")
