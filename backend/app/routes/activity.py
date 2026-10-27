from typing import Optional
from fastapi import APIRouter, Query
from app.database import get_db, serialize_doc

router = APIRouter(prefix="/activity", tags=["Activity History"])


@router.get("")
def get_activity_history(
    search: Optional[str] = Query(None, description="Search description, record ID, or user"),
    module: Optional[str] = Query(None, description="Filter by module"),
    action: Optional[str] = Query(None, description="Filter by action"),
    limit: int = Query(50, ge=1, le=200),
    page: int = Query(1, ge=1)
):
    db = get_db()
    filters = {}

    if search:
        search_regex = {"$regex": search.strip(), "$options": "i"}
        filters["$or"] = [
            {"description": search_regex},
            {"record_id": search_regex},
            {"activity_id": search_regex},
            {"user_identifier": search_regex}
        ]

    if module and module != "All":
        filters["module"] = module

    if action and action != "All":
        filters["action"] = action

    total_records = db.activity_logs.count_documents(filters)
    skip = (page - 1) * limit

    logs = (
        db.activity_logs.find(filters)
        .sort("timestamp", -1)
        .skip(skip)
        .limit(limit)
    )

    return {
        "total": total_records,
        "page": page,
        "limit": limit,
        "items": [serialize_doc(log) for log in logs]
    }
