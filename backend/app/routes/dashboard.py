from fastapi import APIRouter
from app.database import get_db, serialize_doc

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("")
def get_dashboard_data():
    db = get_db()

    # Aggregate counts
    total_programs = db.programs.count_documents({})
    total_services = db.services.count_documents({})
    total_training = db.training_programs.count_documents({"program_type": "Training"})
    total_internships = db.training_programs.count_documents({"program_type": "Internship"})
    total_all_training = db.training_programs.count_documents({})
    total_customers = db.customers.count_documents({})
    total_inquiries = db.inquiries.count_documents({})
    open_service_requests = db.service_requests.count_documents({"status": {"$in": ["Open", "In Progress"]}})

    # Programs status distribution
    program_statuses = list(db.programs.aggregate([
        {"$group": {"_id": "$status", "count": {"$sum": 1}}}
    ]))
    programs_by_status = {item["_id"] or "Unknown": item["count"] for item in program_statuses}

    # Requests status distribution
    request_statuses = list(db.service_requests.aggregate([
        {"$group": {"_id": "$status", "count": {"$sum": 1}}}
    ]))
    requests_by_status = {item["_id"] or "Unknown": item["count"] for item in request_statuses}

    # Inquiries status distribution
    inquiry_statuses = list(db.inquiries.aggregate([
        {"$group": {"_id": "$status", "count": {"$sum": 1}}}
    ]))
    inquiries_by_status = {item["_id"] or "Unknown": item["count"] for item in inquiry_statuses}

    # Training vs Internship
    training_by_type = {
        "Training": total_training,
        "Internship": total_internships
    }

    # Recently created records across modules (collect latest from each, sort, take top 6)
    recent_items = []

    for p in db.programs.find({}).sort("created_at", -1).limit(3):
        sp = serialize_doc(p)
        recent_items.append({
            "id": sp.get("id"),
            "display_id": sp.get("program_id"),
            "title": sp.get("name"),
            "module": "Technology Programs",
            "category": sp.get("category"),
            "status": sp.get("status"),
            "created_at": sp.get("created_at")
        })

    for s in db.services.find({}).sort("created_at", -1).limit(3):
        ss = serialize_doc(s)
        recent_items.append({
            "id": ss.get("id"),
            "display_id": ss.get("service_id"),
            "title": ss.get("name"),
            "module": "Digital Services",
            "category": ss.get("category"),
            "status": ss.get("availability_status"),
            "created_at": ss.get("created_at")
        })

    for t in db.training_programs.find({}).sort("created_at", -1).limit(3):
        st = serialize_doc(t)
        recent_items.append({
            "id": st.get("id"),
            "display_id": st.get("program_id"),
            "title": st.get("title"),
            "module": f"{st.get('program_type', 'Training')}",
            "category": st.get("duration"),
            "status": st.get("status"),
            "created_at": st.get("created_at")
        })

    for req in db.service_requests.find({}).sort("created_at", -1).limit(3):
        sreq = serialize_doc(req)
        recent_items.append({
            "id": sreq.get("id"),
            "display_id": sreq.get("request_id"),
            "title": sreq.get("title"),
            "module": "Service Requests",
            "category": sreq.get("request_category"),
            "status": sreq.get("status"),
            "created_at": sreq.get("created_at")
        })

    for inq in db.inquiries.find({}).sort("created_at", -1).limit(3):
        sinq = serialize_doc(inq)
        recent_items.append({
            "id": sinq.get("id"),
            "display_id": sinq.get("inquiry_id"),
            "title": sinq.get("subject"),
            "module": "Customer Inquiries",
            "category": sinq.get("customer_name"),
            "status": sinq.get("status"),
            "created_at": sinq.get("created_at")
        })

    # Sort recent items by created_at desc
    recent_items.sort(key=lambda x: str(x.get("created_at") or ""), reverse=True)
    recently_created = recent_items[:6]

    # Recent user activity (latest 6)
    recent_activity_cursor = db.activity_logs.find({}).sort("timestamp", -1).limit(6)
    recent_activity = [serialize_doc(a) for a in recent_activity_cursor]

    return {
        "total_programs": total_programs,
        "total_services": total_services,
        "total_training_programs": total_all_training,
        "total_training_only": total_training,
        "total_internships": total_internships,
        "total_customers": total_customers,
        "total_inquiries": total_inquiries,
        "open_service_requests": open_service_requests,
        "recently_created": recently_created,
        "recent_activity": recent_activity,
        "programs_by_status": programs_by_status,
        "requests_by_status": requests_by_status,
        "inquiries_by_status": inquiries_by_status,
        "training_by_type": training_by_type
    }
