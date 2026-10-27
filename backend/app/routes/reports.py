from fastapi import APIRouter, Query, Response
from app.database import get_db, serialize_doc, record_activity
from app.services import generate_csv_data

router = APIRouter(prefix="/reports", tags=["Business Reports"])


@router.get("")
def get_business_reports():
    db = get_db()

    # Programs by Status
    programs_by_status = list(db.programs.aggregate([
        {"$group": {"_id": "$status", "count": {"$sum": 1}}}
    ]))
    programs_status_dict = {item["_id"] or "Unknown": item["count"] for item in programs_by_status}

    # Programs by Category
    programs_by_cat = list(db.programs.aggregate([
        {"$group": {"_id": "$category", "count": {"$sum": 1}}}
    ]))
    programs_category_dict = {item["_id"] or "Unknown": item["count"] for item in programs_by_cat}

    # Service Requests by Status
    requests_by_status = list(db.service_requests.aggregate([
        {"$group": {"_id": "$status", "count": {"$sum": 1}}}
    ]))
    requests_status_dict = {item["_id"] or "Unknown": item["count"] for item in requests_by_status}

    # Service Requests by Priority
    requests_by_priority = list(db.service_requests.aggregate([
        {"$group": {"_id": "$priority", "count": {"$sum": 1}}}
    ]))
    requests_priority_dict = {item["_id"] or "Unknown": item["count"] for item in requests_by_priority}

    # Inquiries by Status
    inquiries_by_status = list(db.inquiries.aggregate([
        {"$group": {"_id": "$status", "count": {"$sum": 1}}}
    ]))
    inquiries_status_dict = {item["_id"] or "Unknown": item["count"] for item in inquiries_by_status}

    # Inquiries by Category
    inquiries_by_cat = list(db.inquiries.aggregate([
        {"$group": {"_id": "$category", "count": {"$sum": 1}}}
    ]))
    inquiries_category_dict = {item["_id"] or "Unknown": item["count"] for item in inquiries_by_cat}

    # Training vs Internship Breakdown
    training_count = db.training_programs.count_documents({"program_type": "Training"})
    internship_count = db.training_programs.count_documents({"program_type": "Internship"})

    training_by_status = list(db.training_programs.aggregate([
        {"$group": {"_id": "$status", "count": {"$sum": 1}}}
    ]))
    training_status_dict = {item["_id"] or "Unknown": item["count"] for item in training_by_status}

    # Services by Availability
    services_by_avail = list(db.services.aggregate([
        {"$group": {"_id": "$availability_status", "count": {"$sum": 1}}}
    ]))
    services_avail_dict = {item["_id"] or "Unknown": item["count"] for item in services_by_avail}

    # Customers by Category
    customers_by_cat = list(db.customers.aggregate([
        {"$group": {"_id": "$customer_category", "count": {"$sum": 1}}}
    ]))
    customers_category_dict = {item["_id"] or "Unknown": item["count"] for item in customers_by_cat}

    # Recent activity summary (last 10)
    recent_activity = [
        serialize_doc(a) for a in db.activity_logs.find({}).sort("timestamp", -1).limit(10)
    ]

    return {
        "programs_by_status": programs_status_dict,
        "programs_by_category": programs_category_dict,
        "requests_by_status": requests_status_dict,
        "requests_by_priority": requests_priority_dict,
        "inquiries_by_status": inquiries_status_dict,
        "inquiries_by_category": inquiries_category_dict,
        "training_vs_internship": {
            "Training": training_count,
            "Internship": internship_count
        },
        "training_by_status": training_status_dict,
        "services_by_status": services_avail_dict,
        "customers_by_category": customers_category_dict,
        "recent_activity_summary": recent_activity
    }


@router.get("/export-csv")
def export_csv(
    module: str = Query(..., description="Module to export: programs, services, training, customers, inquiries, service_requests, activity")
):
    csv_content = generate_csv_data(module)

    # Record activity log
    record_activity(
        action="EXPORT_CSV",
        module="Reports",
        description=f"Exported CSV report for {module.replace('_', ' ').title()}",
        record_id=f"CSV-{module.upper()}"
    )

    filename = f"veda_{module}_export.csv"
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )
