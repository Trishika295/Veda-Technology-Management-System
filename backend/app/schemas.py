from typing import Optional, List, Dict, Any
from pydantic import BaseModel, EmailStr, Field


# ==========================================
# AUTH SCHEMAS
# ==========================================

class UserRegister(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=100)
    role: Optional[str] = Field(default="Staff")


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: str
    user_id: str
    name: str
    email: str
    role: str
    created_at: Optional[str] = None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# ==========================================
# TECHNOLOGY PROGRAMS SCHEMAS
# ==========================================

class ProgramCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=150)
    description: str = Field(..., min_length=5)
    category: str = Field(..., min_length=2)
    start_date: str
    end_date: Optional[str] = None
    status: str = Field(default="Planned")  # Planned, Active, Completed, On Hold


class ProgramUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    status: Optional[str] = None


class ProgramResponse(BaseModel):
    id: str
    program_id: str
    name: str
    description: str
    category: str
    start_date: str
    end_date: Optional[str] = None
    status: str
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


# ==========================================
# DIGITAL SERVICES SCHEMAS
# ==========================================

class ServiceCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=150)
    description: str = Field(..., min_length=5)
    category: str = Field(..., min_length=2)
    availability_status: str = Field(default="Available")  # Available, In Development, Beta, Deprecated
    assigned_team: str = Field(..., min_length=2)


class ServiceUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    availability_status: Optional[str] = None
    assigned_team: Optional[str] = None


class ServiceResponse(BaseModel):
    id: str
    service_id: str
    name: str
    description: str
    category: str
    availability_status: str
    assigned_team: str
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


# ==========================================
# TRAINING & INTERNSHIP SCHEMAS
# ==========================================

class TrainingProgramCreate(BaseModel):
    title: str = Field(..., min_length=2, max_length=150)
    program_type: str = Field(..., description="Training or Internship")
    description: str = Field(..., min_length=5)
    duration: str = Field(..., min_length=2)
    eligibility: str = Field(..., min_length=2)
    available_seats: int = Field(default=25, ge=0)
    application_deadline: Optional[str] = None
    status: str = Field(default="Open")  # Upcoming, Open, Closed, Completed


class TrainingProgramUpdate(BaseModel):
    title: Optional[str] = None
    program_type: Optional[str] = None
    description: Optional[str] = None
    duration: Optional[str] = None
    eligibility: Optional[str] = None
    available_seats: Optional[int] = None
    application_deadline: Optional[str] = None
    status: Optional[str] = None


class TrainingProgramResponse(BaseModel):
    id: str
    program_id: str
    title: str
    program_type: str
    description: str
    duration: str
    eligibility: str
    available_seats: int
    application_deadline: Optional[str] = None
    status: str
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


# ==========================================
# CUSTOMER SCHEMAS
# ==========================================

class CustomerCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    organization: Optional[str] = None
    email: EmailStr
    phone: Optional[str] = None
    customer_category: str = Field(default="Enterprise")  # Enterprise, SME, Startup, Academic, Individual


class CustomerUpdate(BaseModel):
    name: Optional[str] = None
    organization: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    customer_category: Optional[str] = None


class CustomerResponse(BaseModel):
    id: str
    customer_id: str
    name: str
    organization: Optional[str] = None
    email: str
    phone: Optional[str] = None
    customer_category: str
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


# ==========================================
# CUSTOMER INQUIRY SCHEMAS
# ==========================================

class InquiryCreate(BaseModel):
    customer_name: str = Field(..., min_length=2, max_length=100)
    customer_id: Optional[str] = None
    subject: str = Field(..., min_length=3, max_length=200)
    description: str = Field(..., min_length=5)
    category: str = Field(default="General Inquiry")
    priority: str = Field(default="Medium")  # Low, Medium, High
    status: str = Field(default="New")  # New, In Progress, Resolved, Closed
    assigned_team: str = Field(default="Client Solutions")


class InquiryUpdate(BaseModel):
    customer_name: Optional[str] = None
    customer_id: Optional[str] = None
    subject: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    assigned_team: Optional[str] = None


class InquiryResponse(BaseModel):
    id: str
    inquiry_id: str
    customer_name: str
    customer_id: Optional[str] = None
    subject: str
    description: str
    category: str
    priority: str
    status: str
    assigned_team: str
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


# ==========================================
# SERVICE REQUEST SCHEMAS
# ==========================================

class ServiceRequestCreate(BaseModel):
    title: str = Field(..., min_length=2, max_length=200)
    description: str = Field(..., min_length=5)
    request_category: str = Field(..., min_length=2)
    priority: str = Field(default="Medium")  # Low, Medium, High
    status: str = Field(default="Open")  # Open, In Progress, Resolved, Closed
    customer_reference: Optional[str] = None
    assigned_team: str = Field(default="Engineering Core")


class ServiceRequestUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    request_category: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    customer_reference: Optional[str] = None
    assigned_team: Optional[str] = None


class ServiceRequestResponse(BaseModel):
    id: str
    request_id: str
    title: str
    description: str
    request_category: str
    priority: str
    status: str
    customer_reference: Optional[str] = None
    assigned_team: str
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


# ==========================================
# ACTIVITY HISTORY SCHEMA
# ==========================================

class ActivityLogResponse(BaseModel):
    id: str
    activity_id: str
    action: str
    module: str
    record_id: Optional[str] = None
    description: str
    timestamp: Optional[str] = None
    user_identifier: str


# ==========================================
# DASHBOARD & REPORTS SCHEMAS
# ==========================================

class DashboardSummaryResponse(BaseModel):
    total_programs: int
    total_services: int
    total_training_programs: int
    total_internships: int
    total_customers: int
    total_inquiries: int
    open_service_requests: int
    recently_created: List[Dict[str, Any]]
    recent_activity: List[Dict[str, Any]]
    programs_by_status: Dict[str, int]
    requests_by_status: Dict[str, int]
    inquiries_by_status: Dict[str, int]
