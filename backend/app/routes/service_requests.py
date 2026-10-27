from datetime import datetime, timezone
from typing import Optional
from bson import ObjectId
from fastapi import APIRouter, HTTPException, status, Query
from app.database import get_db, serialize_doc, record_activity
from app.schemas import ServiceRequestCreate, ServiceRequestUpdate, ServiceRequestResponse
from app.services import generate_entity_id, PREFIX_REQUEST

router = APIRouter(prefix="/service-requests", tags=["Service Requests"])


def find_request_by_id_or_code(id_or_code: str):
    db = get_db()
    query = {"request_id": id_or_code}
    if ObjectId.is_valid(id_or_code):
        query = {"$or": [{"_id": ObjectId(id_or_code)}, {"request_id": id_or_code}]}
    return db.service_requests.find_one(query)


@router.get("", response_model=list[ServiceRequestResponse])
def get_service_requests(
    search: Optional[str] = Query(None, description="Search by title, description, or request ID"),
    category: Optional[str] = Query(None, description="Filter by category"),
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status"),
    priority: Optional[str] = Query(None, description="Filter by priority")
):
    db = get_db()
    filters = {}

    if search:
        search_regex = {"$regex": search.strip(), "$options": "i"}
        filters["$or"] = [
            {"title": search_regex},
            {"description": search_regex},
            {"request_id": search_regex},
            {"customer_reference": search_regex},
            {"assigned_team": search_regex}
        ]

    if category and category != "All":
        filters["request_category"] = category

    if status_filter and status_filter != "All":
        filters["status"] = status_filter

    if priority and priority != "All":
        filters["priority"] = priority

    docs = db.service_requests.find(filters).sort("created_at", -1)
    return [serialize_doc(doc) for doc in docs]


@router.post("", response_model=ServiceRequestResponse, status_code=status.HTTP_201_CREATED)
def create_service_request(data: ServiceRequestCreate):
    db = get_db()
    now = datetime.now(timezone.utc)
    request_id = generate_entity_id("service_requests", PREFIX_REQUEST)

    doc = {
        "request_id": request_id,
        "title": data.title.strip(),
        "description": data.description.strip(),
        "request_category": data.request_category.strip(),
        "priority": data.priority,
        "status": data.status,
        "customer_reference": data.customer_reference.strip() if data.customer_reference else None,
        "assigned_team": data.assigned_team.strip(),
        "created_at": now,
        "updated_at": now
    }

    result = db.service_requests.insert_one(doc)
    doc["_id"] = result.inserted_id

    record_activity(
        action="CREATE",
        module="Service Requests",
        description=f"Created Service Request: {doc['title']} ({request_id})",
        record_id=request_id
    )

    return serialize_doc(doc)


@router.get("/{id_or_code}", response_model=ServiceRequestResponse)
def get_service_request(id_or_code: str):
    doc = find_request_by_id_or_code(id_or_code)
    if not doc:
        raise HTTPException(status_code=404, detail="Service request not found.")
    return serialize_doc(doc)


@router.put("/{id_or_code}", response_model=ServiceRequestResponse)
def update_service_request(id_or_code: str, data: ServiceRequestUpdate):
    db = get_db()
    doc = find_request_by_id_or_code(id_or_code)
    if not doc:
        raise HTTPException(status_code=404, detail="Service request not found.")

    old_status = doc.get("status")
    update_fields = {k: v for k, v in data.model_dump().items() if v is not None}
    if not update_fields:
        return serialize_doc(doc)

    update_fields["updated_at"] = datetime.now(timezone.utc)
    db.service_requests.update_one({"_id": doc["_id"]}, {"$set": update_fields})

    updated_doc = db.service_requests.find_one({"_id": doc["_id"]})

    if "status" in update_fields and update_fields["status"] != old_status:
        record_activity(
            action="STATUS_CHANGE",
            module="Service Requests",
            description=f"Service Request {updated_doc.get('request_id')} status changed from '{old_status}' to '{update_fields['status']}'",
            record_id=updated_doc.get("request_id")
        )
    else:
        record_activity(
            action="UPDATE",
            module="Service Requests",
            description=f"Updated Service Request: {updated_doc.get('title')} ({updated_doc.get('request_id')})",
            record_id=updated_doc.get("request_id")
        )

    return serialize_doc(updated_doc)


@router.delete("/{id_or_code}", status_code=status.HTTP_200_OK)
def delete_service_request(id_or_code: str):
    db = get_db()
    doc = find_request_by_id_or_code(id_or_code)
    if not doc:
        raise HTTPException(status_code=404, detail="Service request not found.")

    db.service_requests.delete_one({"_id": doc["_id"]})
    record_activity(
        action="DELETE",
        module="Service Requests",
        description=f"Deleted Service Request: {doc.get('title')} ({doc.get('request_id')})",
        record_id=doc.get("request_id")
    )

    return {"message": f"Service request {doc.get('request_id')} deleted successfully."}
