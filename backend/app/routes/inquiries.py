from datetime import datetime, timezone
from typing import Optional
from bson import ObjectId
from fastapi import APIRouter, HTTPException, status, Query
from app.database import get_db, serialize_doc, record_activity
from app.schemas import InquiryCreate, InquiryUpdate, InquiryResponse
from app.services import generate_entity_id, PREFIX_INQUIRY

router = APIRouter(prefix="/inquiries", tags=["Customer Inquiries"])


def find_inquiry_by_id_or_code(id_or_code: str):
    db = get_db()
    query = {"inquiry_id": id_or_code}
    if ObjectId.is_valid(id_or_code):
        query = {"$or": [{"_id": ObjectId(id_or_code)}, {"inquiry_id": id_or_code}]}
    return db.inquiries.find_one(query)


@router.get("", response_model=list[InquiryResponse])
def get_inquiries(
    search: Optional[str] = Query(None, description="Search by customer name, subject, or inquiry ID"),
    category: Optional[str] = Query(None, description="Filter by category"),
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status"),
    priority: Optional[str] = Query(None, description="Filter by priority")
):
    db = get_db()
    filters = {}

    if search:
        search_regex = {"$regex": search.strip(), "$options": "i"}
        filters["$or"] = [
            {"subject": search_regex},
            {"description": search_regex},
            {"customer_name": search_regex},
            {"inquiry_id": search_regex},
            {"assigned_team": search_regex}
        ]

    if category and category != "All":
        filters["category"] = category

    if status_filter and status_filter != "All":
        filters["status"] = status_filter

    if priority and priority != "All":
        filters["priority"] = priority

    docs = db.inquiries.find(filters).sort("created_at", -1)
    return [serialize_doc(doc) for doc in docs]


@router.post("", response_model=InquiryResponse, status_code=status.HTTP_201_CREATED)
def create_inquiry(data: InquiryCreate):
    db = get_db()
    now = datetime.now(timezone.utc)
    inquiry_id = generate_entity_id("inquiries", PREFIX_INQUIRY)

    doc = {
        "inquiry_id": inquiry_id,
        "customer_name": data.customer_name.strip(),
        "customer_id": data.customer_id.strip() if data.customer_id else None,
        "subject": data.subject.strip(),
        "description": data.description.strip(),
        "category": data.category.strip(),
        "priority": data.priority,
        "status": data.status,
        "assigned_team": data.assigned_team.strip(),
        "created_at": now,
        "updated_at": now
    }

    result = db.inquiries.insert_one(doc)
    doc["_id"] = result.inserted_id

    record_activity(
        action="CREATE",
        module="Inquiries",
        description=f"Logged Customer Inquiry: '{doc['subject']}' from {doc['customer_name']} ({inquiry_id})",
        record_id=inquiry_id
    )

    return serialize_doc(doc)


@router.get("/{id_or_code}", response_model=InquiryResponse)
def get_inquiry(id_or_code: str):
    doc = find_inquiry_by_id_or_code(id_or_code)
    if not doc:
        raise HTTPException(status_code=404, detail="Customer inquiry not found.")
    return serialize_doc(doc)


@router.put("/{id_or_code}", response_model=InquiryResponse)
def update_inquiry(id_or_code: str, data: InquiryUpdate):
    db = get_db()
    doc = find_inquiry_by_id_or_code(id_or_code)
    if not doc:
        raise HTTPException(status_code=404, detail="Customer inquiry not found.")

    old_status = doc.get("status")
    update_fields = {k: v for k, v in data.model_dump().items() if v is not None}
    if not update_fields:
        return serialize_doc(doc)

    update_fields["updated_at"] = datetime.now(timezone.utc)
    db.inquiries.update_one({"_id": doc["_id"]}, {"$set": update_fields})

    updated_doc = db.inquiries.find_one({"_id": doc["_id"]})

    # Track status change specifically if status changed
    if "status" in update_fields and update_fields["status"] != old_status:
        record_activity(
            action="STATUS_CHANGE",
            module="Inquiries",
            description=f"Inquiry {updated_doc.get('inquiry_id')} status changed from '{old_status}' to '{update_fields['status']}'",
            record_id=updated_doc.get("inquiry_id")
        )
    else:
        record_activity(
            action="UPDATE",
            module="Inquiries",
            description=f"Updated Inquiry: {updated_doc.get('subject')} ({updated_doc.get('inquiry_id')})",
            record_id=updated_doc.get("inquiry_id")
        )

    return serialize_doc(updated_doc)


@router.delete("/{id_or_code}", status_code=status.HTTP_200_OK)
def delete_inquiry(id_or_code: str):
    db = get_db()
    doc = find_inquiry_by_id_or_code(id_or_code)
    if not doc:
        raise HTTPException(status_code=404, detail="Customer inquiry not found.")

    db.inquiries.delete_one({"_id": doc["_id"]})
    record_activity(
        action="DELETE",
        module="Inquiries",
        description=f"Deleted Inquiry: {doc.get('subject')} ({doc.get('inquiry_id')})",
        record_id=doc.get("inquiry_id")
    )

    return {"message": f"Inquiry {doc.get('inquiry_id')} deleted successfully."}
