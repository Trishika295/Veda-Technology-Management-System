from datetime import datetime, timezone
from typing import Optional
from bson import ObjectId
from fastapi import APIRouter, HTTPException, status, Query
from app.database import get_db, serialize_doc, record_activity
from app.schemas import TrainingProgramCreate, TrainingProgramUpdate, TrainingProgramResponse
from app.services import generate_entity_id, PREFIX_TRAINING, PREFIX_INTERNSHIP

router = APIRouter(prefix="/training-programs", tags=["Training & Internships"])


def find_training_by_id_or_code(id_or_code: str):
    db = get_db()
    query = {"program_id": id_or_code}
    if ObjectId.is_valid(id_or_code):
        query = {"$or": [{"_id": ObjectId(id_or_code)}, {"program_id": id_or_code}]}
    return db.training_programs.find_one(query)


@router.get("", response_model=list[TrainingProgramResponse])
def get_training_programs(
    search: Optional[str] = Query(None, description="Search by title, eligibility, or program ID"),
    program_type: Optional[str] = Query(None, description="Filter by Training or Internship"),
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status")
):
    db = get_db()
    filters = {}

    if search:
        search_regex = {"$regex": search.strip(), "$options": "i"}
        filters["$or"] = [
            {"title": search_regex},
            {"description": search_regex},
            {"eligibility": search_regex},
            {"program_id": search_regex}
        ]

    if program_type and program_type != "All":
        filters["program_type"] = program_type

    if status_filter and status_filter != "All":
        filters["status"] = status_filter

    docs = db.training_programs.find(filters).sort("created_at", -1)
    return [serialize_doc(doc) for doc in docs]


@router.post("", response_model=TrainingProgramResponse, status_code=status.HTTP_201_CREATED)
def create_training_program(data: TrainingProgramCreate):
    db = get_db()
    now = datetime.now(timezone.utc)
    prefix = PREFIX_INTERNSHIP if data.program_type == "Internship" else PREFIX_TRAINING
    program_id = generate_entity_id("training_programs", prefix)

    doc = {
        "program_id": program_id,
        "title": data.title.strip(),
        "program_type": data.program_type,
        "description": data.description.strip(),
        "duration": data.duration.strip(),
        "eligibility": data.eligibility.strip(),
        "available_seats": data.available_seats,
        "application_deadline": data.application_deadline,
        "status": data.status,
        "created_at": now,
        "updated_at": now
    }

    result = db.training_programs.insert_one(doc)
    doc["_id"] = result.inserted_id

    record_activity(
        action="CREATE",
        module="Training",
        description=f"Created {data.program_type}: {doc['title']} ({program_id})",
        record_id=program_id
    )

    return serialize_doc(doc)


@router.get("/{id_or_code}", response_model=TrainingProgramResponse)
def get_training_program(id_or_code: str):
    doc = find_training_by_id_or_code(id_or_code)
    if not doc:
        raise HTTPException(status_code=404, detail="Training or internship program not found.")
    return serialize_doc(doc)


@router.put("/{id_or_code}", response_model=TrainingProgramResponse)
def update_training_program(id_or_code: str, data: TrainingProgramUpdate):
    db = get_db()
    doc = find_training_by_id_or_code(id_or_code)
    if not doc:
        raise HTTPException(status_code=404, detail="Training or internship program not found.")

    update_fields = {k: v for k, v in data.model_dump().items() if v is not None}
    if not update_fields:
        return serialize_doc(doc)

    update_fields["updated_at"] = datetime.now(timezone.utc)
    db.training_programs.update_one({"_id": doc["_id"]}, {"$set": update_fields})

    updated_doc = db.training_programs.find_one({"_id": doc["_id"]})
    record_activity(
        action="UPDATE",
        module="Training",
        description=f"Updated {updated_doc.get('program_type')}: {updated_doc.get('title')} ({updated_doc.get('program_id')})",
        record_id=updated_doc.get("program_id")
    )

    return serialize_doc(updated_doc)


@router.delete("/{id_or_code}", status_code=status.HTTP_200_OK)
def delete_training_program(id_or_code: str):
    db = get_db()
    doc = find_training_by_id_or_code(id_or_code)
    if not doc:
        raise HTTPException(status_code=404, detail="Training or internship program not found.")

    db.training_programs.delete_one({"_id": doc["_id"]})
    record_activity(
        action="DELETE",
        module="Training",
        description=f"Deleted {doc.get('program_type')}: {doc.get('title')} ({doc.get('program_id')})",
        record_id=doc.get("program_id")
    )

    return {"message": f"Program {doc.get('program_id')} deleted successfully."}
