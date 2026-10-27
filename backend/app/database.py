import os
from datetime import datetime, timezone
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import ConnectionFailure, PyMongoError
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://127.0.0.1:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "veda_business_management")

_client = None
_db = None


def get_client() -> MongoClient:
    global _client
    if _client is None:
        try:
            _client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
            # Verify connection
            _client.admin.command('ping')
        except ConnectionFailure as e:
            print(f"[ERROR] Failed to connect to MongoDB at {MONGODB_URI}: {e}")
            raise e
    return _client


def get_db():
    global _db
    if _db is None:
        client = get_client()
        _db = client[DATABASE_NAME]
    return _db


def serialize_doc(doc: dict) -> dict:
    """Converts MongoDB BSON types like ObjectId and datetimes to JSON-serializable types."""
    if not doc:
        return doc
    new_doc = {}
    for key, value in doc.items():
        if key == "_id":
            new_doc["id"] = str(value)
        elif isinstance(value, datetime):
            new_doc[key] = value.isoformat()
        elif isinstance(value, dict):
            new_doc[key] = serialize_doc(value)
        elif isinstance(value, list):
            new_doc[key] = [
                serialize_doc(v) if isinstance(v, dict) else v for v in value
            ]
        else:
            new_doc[key] = value
    return new_doc


def record_activity(
    action: str,
    module: str,
    description: str,
    record_id: str | None = None,
    user_identifier: str = "System"
):
    """Logs persistent audit activities to the activity_logs collection."""
    try:
        db = get_db()
        count = db.activity_logs.count_documents({})
        cand_num = 1000 + count + 1
        while db.activity_logs.find_one({"activity_id": f"ACT-{cand_num}"}):
            cand_num += 1
        activity_id = f"ACT-{cand_num}"
        log_entry = {
            "activity_id": activity_id,
            "action": action,
            "module": module,
            "record_id": record_id or "",
            "description": description,
            "timestamp": datetime.now(timezone.utc),
            "user_identifier": user_identifier,
        }
        db.activity_logs.insert_one(log_entry)
    except Exception as e:
        print(f"[WARNING] Failed to write activity log: {e}")


def init_db_indexes():
    """Initializes collections and creates search and sorting indexes."""
    try:
        db = get_db()
        # Users indexes
        db.users.create_index([("email", ASCENDING)], unique=True)
        db.users.create_index([("user_id", ASCENDING)], unique=True)

        # Programs indexes
        db.programs.create_index([("program_id", ASCENDING)], unique=True)
        db.programs.create_index([("name", ASCENDING)])
        db.programs.create_index([("category", ASCENDING)])
        db.programs.create_index([("status", ASCENDING)])
        db.programs.create_index([("created_at", DESCENDING)])

        # Services indexes
        db.services.create_index([("service_id", ASCENDING)], unique=True)
        db.services.create_index([("name", ASCENDING)])
        db.services.create_index([("category", ASCENDING)])
        db.services.create_index([("availability_status", ASCENDING)])
        db.services.create_index([("created_at", DESCENDING)])

        # Training programs indexes
        db.training_programs.create_index([("program_id", ASCENDING)], unique=True)
        db.training_programs.create_index([("title", ASCENDING)])
        db.training_programs.create_index([("program_type", ASCENDING)])
        db.training_programs.create_index([("status", ASCENDING)])
        db.training_programs.create_index([("created_at", DESCENDING)])

        # Customers indexes
        db.customers.create_index([("customer_id", ASCENDING)], unique=True)
        db.customers.create_index([("email", ASCENDING)])
        db.customers.create_index([("name", ASCENDING)])
        db.customers.create_index([("customer_category", ASCENDING)])
        db.customers.create_index([("created_at", DESCENDING)])

        # Inquiries indexes
        db.inquiries.create_index([("inquiry_id", ASCENDING)], unique=True)
        db.inquiries.create_index([("status", ASCENDING)])
        db.inquiries.create_index([("priority", ASCENDING)])
        db.inquiries.create_index([("category", ASCENDING)])
        db.inquiries.create_index([("created_at", DESCENDING)])

        # Service requests indexes
        db.service_requests.create_index([("request_id", ASCENDING)], unique=True)
        db.service_requests.create_index([("status", ASCENDING)])
        db.service_requests.create_index([("priority", ASCENDING)])
        db.service_requests.create_index([("request_category", ASCENDING)])
        db.service_requests.create_index([("created_at", DESCENDING)])

        # Activity logs indexes
        db.activity_logs.create_index([("timestamp", DESCENDING)])
        db.activity_logs.create_index([("module", ASCENDING)])
        db.activity_logs.create_index([("action", ASCENDING)])

        print("[INFO] MongoDB indexes initialized successfully.")
    except Exception as e:
        print(f"[WARNING] Index creation notice: {e}")
