from datetime import datetime, timezone
from typing import Optional
from bson import ObjectId
from fastapi import APIRouter, HTTPException, status, Query
from app.database import get_db, serialize_doc, record_activity
from app.schemas import ProgramCreate, ProgramUpdate, ProgramResponse
from app.services import generate_entity_id, PREFIX_PROGRAM

router = APIRouter(prefix="/programs", tags=["Technology Programs"])


def find_program_by_id_or_code(id_or_code: str):
    db = get_db()
    query = {"program_id": id_or_code}
    if ObjectId.is_valid(id_or_code):
        query = {"$or": [{"_id": ObjectId(id_or_code)}, {"program_id": id_or_code}]}
    doc = db.programs.find_one(query)
    return doc


@router.get("", response_model=list[ProgramResponse])
def get_programs(
    search: Optional[str] = Query(None, description="Search by name, description or program ID"),
    category: Optional[str] = Query(None, description="Filter by category"),
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status")
):
    db = get_db()
    filters = {}

    if search:
        search_regex = {"$regex": search.strip(), "$options": "i"}
        filters["$or"] = [
            {"name": search_regex},
            {"description": search_regex},
            {"program_id": search_regex},
            {"category": search_regex}
        ]

    if category and category != "All":
        filters["category"] = category

    if status_filter and status_filter != "All":
        filters["status"] = status_filter

    docs = db.programs.find(filters).sort("created_at", -1)
    return [serialize_doc(doc) for doc in docs]


@router.post("", response_model=ProgramResponse, status_code=status.HTTP_201_CREATED)
def create_program(data: ProgramCreate):
    db = get_db()
    now = datetime.now(timezone.utc)
    program_id = generate_entity_id("programs", PREFIX_PROGRAM)

    doc = {
        "program_id": program_id,
        "name": data.name.strip(),
        "description": data.description.strip(),
        "category": data.category.strip(),
        "start_date": data.start_date,
        "end_date": data.end_date,
        "status": data.status,
        "created_at": now,
        "updated_at": now
    }

    result = db.programs.insert_one(doc)
    doc["_id"] = result.inserted_id

    record_activity(
        action="CREATE",
        module="Programs",
        description=f"Created Technology Program: {doc['name']} ({program_id})",
        record_id=program_id
    )

    return serialize_doc(doc)


@router.get("/{id_or_code}", response_model=ProgramResponse)
def get_program(id_or_code: str):
    doc = find_program_by_id_or_code(id_or_code)
    if not doc:
        raise HTTPException(status_code=404, detail="Technology program not found.")
    return serialize_doc(doc)


@router.put("/{id_or_code}", response_model=ProgramResponse)
def update_program(id_or_code: str, data: ProgramUpdate):
    db = get_db()
    doc = find_program_by_id_or_code(id_or_code)
    if not doc:
        raise HTTPException(status_code=404, detail="Technology program not found.")

    update_fields = {k: v for k, v in data.model_dump().items() if v is not None}
    if not update_fields:
        return serialize_doc(doc)

    update_fields["updated_at"] = datetime.now(timezone.utc)
    db.programs.update_one({"_id": doc["_id"]}, {"$set": update_fields})

    updated_doc = db.programs.find_one({"_id": doc["_id"]})
    record_activity(
        action="UPDATE",
        module="Programs",
        description=f"Updated Technology Program: {updated_doc.get('name')} ({updated_doc.get('program_id')})",
        record_id=updated_doc.get("program_id")
    )

    return serialize_doc(updated_doc)


@router.delete("/{id_or_code}", status_code=status.HTTP_200_OK)
def delete_program(id_or_code: str):
    db = get_db()
    doc = find_program_by_id_or_code(id_or_code)
    if not doc:
        raise HTTPException(status_code=404, detail="Technology program not found.")

    db.programs.delete_one({"_id": doc["_id"]})
    record_activity(
        action="DELETE",
        module="Programs",
        description=f"Deleted Technology Program: {doc.get('name')} ({doc.get('program_id')})",
        record_id=doc.get("program_id")
    )

    return {"message": f"Program {doc.get('program_id')} deleted successfully."}
