from datetime import datetime, timezone
from typing import Optional
from bson import ObjectId
from fastapi import APIRouter, HTTPException, status, Query
from app.database import get_db, serialize_doc, record_activity
from app.schemas import CustomerCreate, CustomerUpdate, CustomerResponse
from app.services import generate_entity_id, PREFIX_CUSTOMER

router = APIRouter(prefix="/customers", tags=["Customer Management"])


def find_customer_by_id_or_code(id_or_code: str):
    db = get_db()
    query = {"customer_id": id_or_code}
    if ObjectId.is_valid(id_or_code):
        query = {"$or": [{"_id": ObjectId(id_or_code)}, {"customer_id": id_or_code}]}
    return db.customers.find_one(query)


@router.get("", response_model=list[CustomerResponse])
def get_customers(
    search: Optional[str] = Query(None, description="Search by name, email, organization, or customer ID"),
    category: Optional[str] = Query(None, description="Filter by customer category")
):
    db = get_db()
    filters = {}

    if search:
        search_regex = {"$regex": search.strip(), "$options": "i"}
        filters["$or"] = [
            {"name": search_regex},
            {"email": search_regex},
            {"organization": search_regex},
            {"customer_id": search_regex},
            {"phone": search_regex}
        ]

    if category and category != "All":
        filters["customer_category"] = category

    docs = db.customers.find(filters).sort("created_at", -1)
    return [serialize_doc(doc) for doc in docs]


@router.post("", response_model=CustomerResponse, status_code=status.HTTP_201_CREATED)
def create_customer(data: CustomerCreate):
    db = get_db()
    # Check duplicate email
    existing = db.customers.find_one({"email": data.email.lower()})
    if existing:
        raise HTTPException(status_code=400, detail="A customer with this email address already exists.")

    now = datetime.now(timezone.utc)
    customer_id = generate_entity_id("customers", PREFIX_CUSTOMER)

    doc = {
        "customer_id": customer_id,
        "name": data.name.strip(),
        "organization": data.organization.strip() if data.organization else None,
        "email": data.email.lower().strip(),
        "phone": data.phone.strip() if data.phone else None,
        "customer_category": data.customer_category,
        "created_at": now,
        "updated_at": now
    }

    result = db.customers.insert_one(doc)
    doc["_id"] = result.inserted_id

    record_activity(
        action="CREATE",
        module="Customers",
        description=f"Created Customer: {doc['name']} ({customer_id})",
        record_id=customer_id
    )

    return serialize_doc(doc)


@router.get("/{id_or_code}", response_model=CustomerResponse)
def get_customer(id_or_code: str):
    doc = find_customer_by_id_or_code(id_or_code)
    if not doc:
        raise HTTPException(status_code=404, detail="Customer not found.")
    return serialize_doc(doc)


@router.put("/{id_or_code}", response_model=CustomerResponse)
def update_customer(id_or_code: str, data: CustomerUpdate):
    db = get_db()
    doc = find_customer_by_id_or_code(id_or_code)
    if not doc:
        raise HTTPException(status_code=404, detail="Customer not found.")

    update_fields = {k: v for k, v in data.model_dump().items() if v is not None}
    if "email" in update_fields:
        update_fields["email"] = update_fields["email"].lower().strip()
        # Verify email uniqueness
        existing = db.customers.find_one({"email": update_fields["email"], "_id": {"$ne": doc["_id"]}})
        if existing:
            raise HTTPException(status_code=400, detail="Another customer already uses this email.")

    if not update_fields:
        return serialize_doc(doc)

    update_fields["updated_at"] = datetime.now(timezone.utc)
    db.customers.update_one({"_id": doc["_id"]}, {"$set": update_fields})

    updated_doc = db.customers.find_one({"_id": doc["_id"]})
    record_activity(
        action="UPDATE",
        module="Customers",
        description=f"Updated Customer: {updated_doc.get('name')} ({updated_doc.get('customer_id')})",
        record_id=updated_doc.get("customer_id")
    )

    return serialize_doc(updated_doc)


@router.delete("/{id_or_code}", status_code=status.HTTP_200_OK)
def delete_customer(id_or_code: str):
    db = get_db()
    doc = find_customer_by_id_or_code(id_or_code)
    if not doc:
        raise HTTPException(status_code=404, detail="Customer not found.")

    db.customers.delete_one({"_id": doc["_id"]})
    record_activity(
        action="DELETE",
        module="Customers",
        description=f"Deleted Customer: {doc.get('name')} ({doc.get('customer_id')})",
        record_id=doc.get("customer_id")
    )

    return {"message": f"Customer {doc.get('customer_id')} deleted successfully."}
