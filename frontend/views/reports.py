import streamlit as st
import pandas as pd
from api_client import api, APIError
from components import render_top_navbar, render_module_header, render_stat_card, format_datetime

EXPORT_MODULES = [
    {"id": "programs", "label": "Programs"},
    {"id": "services", "label": "Services"},
    {"id": "training", "label": "Training & Internships"},
    {"id": "customers", "label": "Customers"},
    {"id": "inquiries", "label": "Inquiries"},
    {"id": "service_requests", "label": "Service Requests"},
    {"id": "activity", "label": "Activity Logs"}
]


def render_reports(token: str):
    render_top_navbar("Business Reports & Strategic Analytics")
    render_module_header(
        "Business Reports & Analytics",
        "Verified database aggregations, module distributions, operational throughput, and CSV data exports",
        icon_name="bar-chart"
    )

    # Direct CSV Exports Toolbar
    st.subheader("Direct CSV Data Exports")
    st.caption("Download live records into standard CSV format for offline reporting, spreadsheet audits, or institutional sharing.")

    exp_cols = st.columns(len(EXPORT_MODULES))
    for idx, mod in enumerate(EXPORT_MODULES):
        with exp_cols[idx]:
            # Generate or download CSV
            try:
                csv_data = api.get_csv_export(mod["id"], token=token)
                st.download_button(
                    label=f"⬇️ {mod['label']}",
                    data=csv_data,
                    file_name=f"veda_{mod['id']}_export.csv",
                    mime="text/csv",
                    key=f"dl_csv_{mod['id']}",
                    use_container_width=True
                )
            except Exception as e:
                st.button(f"{mod['label']} (N/A)", disabled=True, key=f"dl_csv_err_{mod['id']}")

    st.write("")
    st.divider()

    # Load Reports Aggregations
    try:
        report_data = api.get_reports(token=token)
    except APIError as e:
        st.error(f"Failed to aggregate reports: {e.message}")
        return

    programs_by_status = report_data.get("programs_by_status", {})
    programs_by_category = report_data.get("programs_by_category", {})
    requests_by_status = report_data.get("requests_by_status", {})
    requests_by_priority = report_data.get("requests_by_priority", {})
    inquiries_by_status = report_data.get("inquiries_by_status", {})
    inquiries_by_category = report_data.get("inquiries_by_category", {})
    training_vs_internship = report_data.get("training_vs_internship", {})
    training_by_status = report_data.get("training_by_status", {})
    services_by_status = report_data.get("services_by_status", {})
    customers_by_category = report_data.get("customers_by_category", {})
    recent_activity_summary = report_data.get("recent_activity_summary", [])

    st.subheader("Strategic Analytical Breakdowns")

    col1, col2 = st.columns(2, gap="large")

    # Column 1: Technology Programs & Digital Services
    with col1:
        st.markdown("#### 1. Technology Programs by Status")
        if programs_by_status:
            total_p = sum(programs_by_status.values()) or 1
            for st_name, count in programs_by_status.items():
                pct = int((count / total_p) * 100)
                st.write(f"**{st_name}:** {count} ({pct}%)")
                st.progress(pct / 100)
        else:
            st.caption("No programs registered.")

        st.write("")
        st.markdown("**Program Categories Representation:**")
        if programs_by_category:
            p_cat_rows = [{"Category": k, "Count": v} for k, v in programs_by_category.items()]
            st.dataframe(pd.DataFrame(p_cat_rows), use_container_width=True, hide_index=True)
        else:
            st.caption("No categories recorded.")

        st.write("")
        st.markdown("#### 2. Service Requests & Technical Issues")
        if requests_by_status:
            total_r = sum(requests_by_status.values()) or 1
            for st_name, count in requests_by_status.items():
                pct = int((count / total_r) * 100)
                st.write(f"**{st_name}:** {count} ({pct}%)")
                st.progress(pct / 100)
        else:
            st.caption("No service requests recorded.")

        st.write("")
        st.markdown("**Request Priority Breakdown:**")
        if requests_by_priority:
            prio_rows = [{"Priority Level": k, "Active Tickets": v} for k, v in requests_by_priority.items()]
            st.dataframe(pd.DataFrame(prio_rows), use_container_width=True, hide_index=True)

    # Column 2: Inquiries & Training/Internship Cohorts
    with col2:
        st.markdown("#### 3. Customer Inquiry Resolution Pipeline")
        if inquiries_by_status:
            total_i = sum(inquiries_by_status.values()) or 1
            for st_name, count in inquiries_by_status.items():
                pct = int((count / total_i) * 100)
                st.write(f"**{st_name}:** {count} ({pct}%)")
                st.progress(pct / 100)
        else:
            st.caption("No inquiries registered.")

        st.write("")
        st.markdown("**Inquiry Topic Categories:**")
        if inquiries_by_category:
            inq_cat_rows = [{"Category": k, "Inquiries": v} for k, v in inquiries_by_category.items()]
            st.dataframe(pd.DataFrame(inq_cat_rows), use_container_width=True, hide_index=True)

        st.write("")
        st.markdown("#### 4. Training vs. Internship Cohorts")
        trn_count = training_vs_internship.get("Training", 0)
        int_count = training_vs_internship.get("Internship", 0)
        total_cohort = trn_count + int_count or 1
        t_pct = int((trn_count / total_cohort) * 100)
        i_pct = int((int_count / total_cohort) * 100)

        tc1, tc2 = st.columns(2)
        with tc1:
            render_stat_card("Bootcamps", trn_count, f"{t_pct}% of cohorts", icon_name="graduation-cap", icon_color="#7C3AED", icon_bg="#F5F3FF")
        with tc2:
            render_stat_card("Internships", int_count, f"{i_pct}% of cohorts", icon_name="graduation-cap", icon_color="#2453E6", icon_bg="#EFF6FF")

        st.write("")
        st.markdown("**Program Cohort Statuses:**")
        if training_by_status:
            trn_st_rows = [{"Status": k, "Programs": v} for k, v in training_by_status.items()]
            st.dataframe(pd.DataFrame(trn_st_rows), use_container_width=True, hide_index=True)

    st.write("")
    st.divider()

    # Recent Activity Audit Table
    st.subheader("Recent Organizational Activity Summary")
    st.caption("Chronological log of administrative actions, status transitions, and data creations")

    if not recent_activity_summary:
        st.caption("No activity records found.")
    else:
        act_rows = []
        for a in recent_activity_summary:
            act_rows.append({
                "Activity ID": a.get("activity_id", ""),
                "Action": a.get("action", ""),
                "Module": a.get("module", ""),
                "Description": a.get("description", ""),
                "User": a.get("user_identifier", "System"),
                "Timestamp": format_datetime(a.get("timestamp"))
            })
        st.dataframe(pd.DataFrame(act_rows), use_container_width=True, hide_index=True)
