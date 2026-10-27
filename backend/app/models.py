"""
Database models and collection definitions for Veda Technology Business & Service Management System.
"""

# Collection names
USERS_COLLECTION = "users"
PROGRAMS_COLLECTION = "programs"
SERVICES_COLLECTION = "services"
TRAINING_COLLECTION = "training_programs"
CUSTOMERS_COLLECTION = "customers"
INQUIRIES_COLLECTION = "inquiries"
SERVICE_REQUESTS_COLLECTION = "service_requests"
ACTIVITY_LOGS_COLLECTION = "activity_logs"

# ID Prefixes
PREFIX_PROGRAM = "PRG"
PREFIX_SERVICE = "SRV"
PREFIX_TRAINING = "TRN"
PREFIX_INTERNSHIP = "INT"
PREFIX_CUSTOMER = "CST"
PREFIX_INQUIRY = "INQ"
PREFIX_REQUEST = "REQ"
PREFIX_ACTIVITY = "ACT"
PREFIX_USER = "USR"

# Valid statuses
PROGRAM_STATUSES = ["Planned", "Active", "Completed", "On Hold"]
SERVICE_STATUSES = ["Available", "In Development", "Beta", "Deprecated"]
TRAINING_STATUSES = ["Upcoming", "Open", "Closed", "Completed"]
INQUIRY_STATUSES = ["New", "In Progress", "Resolved", "Closed"]
SERVICE_REQUEST_STATUSES = ["Open", "In Progress", "Resolved", "Closed"]
PRIORITIES = ["Low", "Medium", "High"]
