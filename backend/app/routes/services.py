from datetime import datetime, timezone
from typing import Optional
from bson import ObjectId
from fastapi import APIRouter, HTTPException, status, Query
from app.database import get_db, serialize_doc, record_activity
from app.schemas import ServiceCreate, ServiceUpdate, ServiceResponse
from app.services import generate_entity_id, PREFIX_SERVICE

router = APIRouter(prefix="/services", tags=["Digital Services"])


def find_service_by_id_or_code(id_or_code: str):
    db = get_db()
    query = {"service_id": id_or_code}
    if ObjectId.is_valid(id_or_code):
        query = {"$or": [{"_id": ObjectId(id_or_code)}, {"service_id": id_or_code}]}
    return db.services.find_one(query)


@router.get("", response_model=list[ServiceResponse])
def get_services(
    search: Optional[str] = Query(None, description="Search by name, description or service ID"),
    category: Optional[str] = Query(None, description="Filter by category"),
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by availability status")
):
    db = get_db()
    filters = {}

    if search:
        search_regex = {"$regex": search.strip(), "$options": "i"}
        filters["$or"] = [
            {"name": search_regex},
            {"description": search_regex},
            {"service_id": search_regex},
            {"assigned_team": search_regex},
            {"category": search_regex}
        ]

    if category and category != "All":
        filters["category"] = category

    if status_filter and status_filter != "All":
        filters["availability_status"] = status_filter

    docs = db.services.find(filters).sort("created_at", -1)
    return [serialize_doc(doc) for doc in docs]


@router.post("", response_model=ServiceResponse, status_code=status.HTTP_201_CREATED)
def create_service(data: ServiceCreate):
    db = get_db()
    now = datetime.now(timezone.utc)
    service_id = generate_entity_id("services", PREFIX_SERVICE)

    doc = {
        "service_id": service_id,
        "name": data.name.strip(),
        "description": data.description.strip(),
        "category": data.category.strip(),
        "availability_status": data.availability_status,
        "assigned_team": data.assigned_team.strip(),
        "created_at": now,
        "updated_at": now
    }

    result = db.services.insert_one(doc)
    doc["_id"] = result.inserted_id

    record_activity(
        action="CREATE",
        module="Services",
        description=f"Created Digital Service: {doc['name']} ({service_id})",
        record_id=service_id
    )

    return serialize_doc(doc)


@router.get("/{id_or_code}", response_model=ServiceResponse)
def get_service(id_or_code: str):
    doc = find_service_by_id_or_code(id_or_code)
    if not doc:
        raise HTTPException(status_code=404, detail="Digital service not found.")
    return serialize_doc(doc)


@router.put("/{id_or_code}", response_model=ServiceResponse)
def update_service(id_or_code: str, data: ServiceUpdate):
    db = get_db()
    doc = find_service_by_id_or_code(id_or_code)
    if not doc:
        raise HTTPException(status_code=404, detail="Digital service not found.")

    update_fields = {k: v for k, v in data.model_dump().items() if v is not None}
    if not update_fields:
        return serialize_doc(doc)

    update_fields["updated_at"] = datetime.now(timezone.utc)
    db.services.update_one({"_id": doc["_id"]}, {"$set": update_fields})

    updated_doc = db.services.find_one({"_id": doc["_id"]})
    record_activity(
        action="UPDATE",
        module="Services",
        description=f"Updated Digital Service: {updated_doc.get('name')} ({updated_doc.get('service_id')})",
        record_id=updated_doc.get("service_id")
    )

    return serialize_doc(updated_doc)


@router.delete("/{id_or_code}", status_code=status.HTTP_200_OK)
def delete_service(id_or_code: str):
    db = get_db()
    doc = find_service_by_id_or_code(id_or_code)
    if not doc:
        raise HTTPException(status_code=404, detail="Digital service not found.")

    db.services.delete_one({"_id": doc["_id"]})
    record_activity(
        action="DELETE",
        module="Services",
        description=f"Deleted Digital Service: {doc.get('name')} ({doc.get('service_id')})",
        record_id=doc.get("service_id")
    )

    return {"message": f"Service {doc.get('service_id')} deleted successfully."}
