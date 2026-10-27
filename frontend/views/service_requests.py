import streamlit as st
import pandas as pd
from api_client import api, APIError
from components import render_top_navbar, render_module_header, render_empty_state, format_date

CATEGORIES = [
    'Cloud Deployment',
    'Bug Fix & Maintenance',
    'Feature Implementation',
    'Infrastructure Setup',
    'System Integration'
]

STATUSES = ['Open', 'In Progress', 'Resolved', 'Closed']
PRIORITIES = ['Low', 'Medium', 'High']
TEAMS = ['DevOps Unit', 'Software Solutions', 'QA & Reliability', 'Data Engineering', 'Security Ops']


def render_service_requests(token: str):
    render_top_navbar("Service Requests & Work Orders")
    render_module_header(
        "Service Request Management",
        "Technical service tickets, deployment tasks, bug fixes, and engineering operations",
        icon_name="wrench"
    )

    # Search and Filter
    f1, f2, f3, f4, f5 = st.columns([2, 1.2, 1.2, 1.2, 0.8])
    with f1:
        search = st.text_input("Search Requests", placeholder="Search title, description, or ID...", label_visibility="collapsed")
    with f2:
        category = st.selectbox("Category", ["All"] + CATEGORIES, label_visibility="collapsed")
    with f3:
        status = st.selectbox("Status", ["All"] + STATUSES, label_visibility="collapsed")
    with f4:
        priority = st.selectbox("Priority", ["All"] + PRIORITIES, label_visibility="collapsed")
    with f5:
        if st.button("Reset", key="reset_requests", use_container_width=True):
            st.rerun()

    st.write("")

    # Add Request Expander
    with st.expander("➕ Open New Service Request Work Order", expanded=False):
        with st.form("create_request_form", clear_on_submit=True):
            r_title = st.text_input("Request Title *", placeholder="e.g., Kubernetes Ingress Controller Provisioning")
            r_desc = st.text_area("Detailed Requirements *", placeholder="Technical task details and acceptance criteria...")

            rc1, rc2, rc3 = st.columns(3)
            with rc1:
                r_cat = st.selectbox("Request Category *", CATEGORIES, index=0)
            with rc2:
                r_prio = st.selectbox("Priority Level *", PRIORITIES, index=1)
            with rc3:
                r_status = st.selectbox("Initial Status *", STATUSES, index=0)

            rc4, rc5 = st.columns(2)
            with rc4:
                r_cust_ref = st.text_input("Customer / Project Reference", placeholder="e.g., Apex Global Solutions")
            with rc5:
                r_team = st.selectbox("Assigned Team *", TEAMS, index=0)

            submitted = st.form_submit_button("Submit Service Request", type="primary", use_container_width=True)
            if submitted:
                if not r_title.strip() or not r_desc.strip():
                    st.error("Title and Requirements are required.")
                else:
                    payload = {
                        "title": r_title.strip(),
                        "description": r_desc.strip(),
                        "request_category": r_cat,
                        "priority": r_prio,
                        "status": r_status,
                        "customer_reference": r_cust_ref.strip(),
                        "assigned_team": r_team
                    }
                    try:
                        res = api.create_service_request(payload, token=token)
                        st.success(f"Work order created with ID {res.get('request_id')}!")
                        st.rerun()
                    except APIError as e:
                        st.error(f"Failed to submit request: {e.message}")

    # Fetch service requests
    try:
        requests = api.get_service_requests(token=token, search=search, category=category, status=status, priority=priority)
    except APIError as e:
        st.error(f"Error fetching service requests: {e.message}")
        return

    st.write("")
    if not requests:
        render_empty_state("No service requests found", "Try clearing your filters or create a new work order above.")
        return

    # Table view
    table_rows = []
    for req in requests:
        table_rows.append({
            "Request ID": req.get("request_id", ""),
            "Title": req.get("title", ""),
            "Category": req.get("request_category", ""),
            "Priority": req.get("priority", ""),
            "Status": req.get("status", ""),
            "Customer Ref": req.get("customer_reference", "—"),
            "Assigned Team": req.get("assigned_team", ""),
            "Date": format_date(req.get("created_at"))
        })

    df = pd.DataFrame(table_rows)
    st.dataframe(df, use_container_width=True, hide_index=True)

    st.write("")
    st.divider()

    # Manage Record
    st.subheader("Manage Service Request Record")
    options_map = {f"{req.get('request_id')} - {req.get('title')} ({req.get('status')})": req for req in requests}
    selected_label = st.selectbox("Select request to view or edit:", list(options_map.keys()))
    selected_req = options_map[selected_label]
    req_id = selected_req.get("request_id") or selected_req.get("id")

    tab_quick, tab_details, tab_edit, tab_delete = st.tabs([
        "⚡ Quick Status Transition",
        "View Details",
        "Edit Request",
        "Delete Request"
    ])

    with tab_quick:
        st.markdown(f"Current Status: **{selected_req.get('status')}**")
        q_cols = st.columns(4)
        for idx, target_st in enumerate(STATUSES):
            with q_cols[idx]:
                is_curr = selected_req.get("status") == target_st
                if st.button(
                    f"Set {target_st}",
                    key=f"quick_req_{req_id}_{target_st}",
                    disabled=is_curr,
                    use_container_width=True
                ):
                    try:
                        api.update_service_request(req_id, {"status": target_st}, token=token)
                        st.success(f"Work order {selected_req.get('request_id')} updated to '{target_st}'!")
                        st.rerun()
                    except APIError as e:
                        st.error(f"Status transition failed: {e.message}")

    with tab_details:
        d1, d2 = st.columns(2)
        with d1:
            st.markdown(f"**Request ID:** `{selected_req.get('request_id')}`")
            st.markdown(f"**Title:** {selected_req.get('title')}")
            st.markdown(f"**Category:** {selected_req.get('request_category')}")
            st.markdown(f"**Customer Reference:** {selected_req.get('customer_reference') or '—'}")
        with d2:
            st.markdown(f"**Priority:** {selected_req.get('priority')}")
            st.markdown(f"**Status:** {selected_req.get('status')}")
            st.markdown(f"**Assigned Team:** {selected_req.get('assigned_team')}")
            st.markdown(f"**Created:** {format_date(selected_req.get('created_at'))}")
        st.markdown("**Description & Requirements:**")
        st.info(selected_req.get("description", "No description provided."))

    with tab_edit:
        with st.form(f"edit_req_{req_id}"):
            e_title = st.text_input("Title", value=selected_req.get("title", ""))
            e_desc = st.text_area("Description", value=selected_req.get("description", ""))

            ec1, ec2, ec3 = st.columns(3)
            with ec1:
                curr_cat = selected_req.get("request_category")
                c_idx = CATEGORIES.index(curr_cat) if curr_cat in CATEGORIES else 0
                e_cat = st.selectbox("Category", CATEGORIES, index=c_idx)
            with ec2:
                curr_pr = selected_req.get("priority")
                p_idx = PRIORITIES.index(curr_pr) if curr_pr in PRIORITIES else 1
                e_prio = st.selectbox("Priority", PRIORITIES, index=p_idx)
            with ec3:
                curr_st = selected_req.get("status")
                s_idx = STATUSES.index(curr_st) if curr_st in STATUSES else 0
                e_status = st.selectbox("Status", STATUSES, index=s_idx)

            ec4, ec5 = st.columns(2)
            with ec4:
                e_cust_ref = st.text_input("Customer Reference", value=selected_req.get("customer_reference", ""))
            with ec5:
                curr_tm = selected_req.get("assigned_team")
                tm_idx = TEAMS.index(curr_tm) if curr_tm in TEAMS else 0
                e_team = st.selectbox("Assigned Team", TEAMS, index=tm_idx)

            if st.form_submit_button("Save Changes", type="primary", use_container_width=True):
                if not e_title.strip() or not e_desc.strip():
                    st.error("Title and Description are required.")
                else:
                    payload = {
                        "title": e_title.strip(),
                        "description": e_desc.strip(),
                        "request_category": e_cat,
                        "priority": e_prio,
                        "status": e_status,
                        "customer_reference": e_cust_ref.strip(),
                        "assigned_team": e_team
                    }
                    try:
                        api.update_service_request(req_id, payload, token=token)
                        st.success(f"Work order {selected_req.get('request_id')} updated successfully!")
                        st.rerun()
                    except APIError as e:
                        st.error(f"Update failed: {e.message}")

    with tab_delete:
        st.warning(f"Are you sure you want to permanently delete **{selected_req.get('request_id')}**?")
        if st.button("Confirm Delete Request", key=f"del_req_{req_id}", type="primary"):
            try:
                api.delete_service_request(req_id, token=token)
                st.success(f"Request {selected_req.get('request_id')} deleted.")
                st.rerun()
            except APIError as e:
                st.error(f"Deletion failed: {e.message}")
