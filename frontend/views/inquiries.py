import streamlit as st
import pandas as pd
from api_client import api, APIError
from components import render_top_navbar, render_module_header, render_empty_state, format_date

CATEGORIES = [
    'Technology Program',
    'Digital Service',
    'Training / Internship',
    'Partnership',
    'General Inquiry'
]

STATUSES = ['New', 'In Progress', 'Resolved', 'Closed']
PRIORITIES = ['Low', 'Medium', 'High']
TEAMS = ['Client Solutions', 'Admissions Desk', 'Cloud Solutions', 'AI Labs', 'Technical Support']


def render_inquiries(token: str):
    render_top_navbar("Customer Inquiries Triage")
    render_module_header(
        "Customer Inquiry Management",
        "Triage, assign, and track client inquiries, strategic partnerships, and advisory requests",
        icon_name="message-square"
    )

    # Search and Filter Bar
    f1, f2, f3, f4, f5 = st.columns([2, 1.2, 1.2, 1.2, 0.8])
    with f1:
        search = st.text_input("Search Inquiries", placeholder="Search subject, customer, or ID...", label_visibility="collapsed")
    with f2:
        category = st.selectbox("Category", ["All"] + CATEGORIES, label_visibility="collapsed")
    with f3:
        status = st.selectbox("Status", ["All"] + STATUSES, label_visibility="collapsed")
    with f4:
        priority = st.selectbox("Priority", ["All"] + PRIORITIES, label_visibility="collapsed")
    with f5:
        if st.button("Reset", key="reset_inquiries", use_container_width=True):
            st.rerun()

    st.write("")

    # Add Inquiry Expander
    with st.expander("➕ Register New Customer Inquiry", expanded=False):
        with st.form("create_inquiry_form", clear_on_submit=True):
            c_name, c_sub = st.columns([1, 2])
            with c_name:
                i_customer = st.text_input("Customer / Contact Name *", placeholder="e.g., Rajesh Kumar")
            with c_sub:
                i_subject = st.text_input("Inquiry Subject *", placeholder="Brief summary of inquiry")

            i_desc = st.text_area("Detailed Message *", placeholder="Detailed inquiry requirements...")

            c_cat, c_prio, c_team = st.columns(3)
            with c_cat:
                i_cat = st.selectbox("Inquiry Category *", CATEGORIES, index=0)
            with c_prio:
                i_prio = st.selectbox("Priority Level *", PRIORITIES, index=1)
            with c_team:
                i_team = st.selectbox("Assigned Unit *", TEAMS, index=0)

            submitted = st.form_submit_button("Submit Inquiry", type="primary", use_container_width=True)
            if submitted:
                if not i_customer.strip() or not i_subject.strip() or not i_desc.strip():
                    st.error("Customer Name, Subject, and Message are required.")
                else:
                    payload = {
                        "customer_name": i_customer.strip(),
                        "subject": i_subject.strip(),
                        "description": i_desc.strip(),
                        "category": i_cat,
                        "priority": i_prio,
                        "status": "New",
                        "assigned_team": i_team
                    }
                    try:
                        res = api.create_inquiry(payload, token=token)
                        st.success(f"Inquiry ticket created with ID {res.get('inquiry_id')}!")
                        st.rerun()
                    except APIError as e:
                        st.error(f"Failed to submit inquiry: {e.message}")

    # Fetch inquiries
    try:
        inquiries = api.get_inquiries(token=token, search=search, category=category, status=status, priority=priority)
    except APIError as e:
        st.error(f"Error fetching inquiries: {e.message}")
        return

    st.write("")
    if not inquiries:
        render_empty_state("No customer inquiries found", "Try clearing your filters or create a new ticket above.")
        return

    # Table view
    table_rows = []
    for inq in inquiries:
        table_rows.append({
            "Inquiry ID": inq.get("inquiry_id", ""),
            "Subject": inq.get("subject", ""),
            "Customer": inq.get("customer_name", ""),
            "Category": inq.get("category", ""),
            "Priority": inq.get("priority", ""),
            "Status": inq.get("status", ""),
            "Assigned Team": inq.get("assigned_team", ""),
            "Created": format_date(inq.get("created_at"))
        })

    df = pd.DataFrame(table_rows)
    st.dataframe(df, use_container_width=True, hide_index=True)

    st.write("")
    st.divider()

    # Manage Record
    st.subheader("Manage Inquiry Ticket")
    options_map = {f"{inq.get('inquiry_id')} - {inq.get('subject')} ({inq.get('status')})": inq for inq in inquiries}
    selected_label = st.selectbox("Select inquiry to inspect or update:", list(options_map.keys()))
    selected_inq = options_map[selected_label]
    inq_id = selected_inq.get("inquiry_id") or selected_inq.get("id")

    tab_quick, tab_details, tab_edit, tab_delete = st.tabs([
        "⚡ Quick Status Transition",
        "View Details",
        "Edit Inquiry",
        "Delete Ticket"
    ])

    with tab_quick:
        st.markdown(f"Current Status: **{selected_inq.get('status')}**")
        q_cols = st.columns(4)
        for idx, target_st in enumerate(STATUSES):
            with q_cols[idx]:
                is_curr = selected_inq.get("status") == target_st
                if st.button(
                    f"Set {target_st}",
                    key=f"quick_inq_{inq_id}_{target_st}",
                    disabled=is_curr,
                    use_container_width=True
                ):
                    try:
                        api.update_inquiry(inq_id, {"status": target_st}, token=token)
                        st.success(f"Inquiry {selected_inq.get('inquiry_id')} moved to '{target_st}'!")
                        st.rerun()
                    except APIError as e:
                        st.error(f"Status transition failed: {e.message}")

    with tab_details:
        d1, d2 = st.columns(2)
        with d1:
            st.markdown(f"**Inquiry ID:** `{selected_inq.get('inquiry_id')}`")
            st.markdown(f"**Customer Name:** {selected_inq.get('customer_name')}")
            st.markdown(f"**Subject:** {selected_inq.get('subject')}")
            st.markdown(f"**Category:** {selected_inq.get('category')}")
        with d2:
            st.markdown(f"**Priority:** {selected_inq.get('priority')}")
            st.markdown(f"**Current Status:** {selected_inq.get('status')}")
            st.markdown(f"**Assigned Team:** {selected_inq.get('assigned_team')}")
            st.markdown(f"**Registered Date:** {format_date(selected_inq.get('created_at'))}")
        st.markdown("**Inquiry Description:**")
        st.info(selected_inq.get("description", "No details provided."))

    with tab_edit:
        with st.form(f"edit_inq_{inq_id}"):
            e_cust = st.text_input("Customer Name", value=selected_inq.get("customer_name", ""))
            e_sub = st.text_input("Subject", value=selected_inq.get("subject", ""))
            e_desc = st.text_area("Description", value=selected_inq.get("description", ""))

            ec1, ec2, ec3 = st.columns(3)
            with ec1:
                curr_cat = selected_inq.get("category")
                c_idx = CATEGORIES.index(curr_cat) if curr_cat in CATEGORIES else 0
                e_cat = st.selectbox("Category", CATEGORIES, index=c_idx)
            with ec2:
                curr_pr = selected_inq.get("priority")
                p_idx = PRIORITIES.index(curr_pr) if curr_pr in PRIORITIES else 1
                e_prio = st.selectbox("Priority", PRIORITIES, index=p_idx)
            with ec3:
                curr_st = selected_inq.get("status")
                s_idx = STATUSES.index(curr_st) if curr_st in STATUSES else 0
                e_status = st.selectbox("Status", STATUSES, index=s_idx)

            curr_tm = selected_inq.get("assigned_team")
            tm_idx = TEAMS.index(curr_tm) if curr_tm in TEAMS else 0
            e_team = st.selectbox("Assigned Team", TEAMS, index=tm_idx)

            if st.form_submit_button("Save Changes", type="primary", use_container_width=True):
                if not e_cust.strip() or not e_sub.strip():
                    st.error("Customer Name and Subject are required.")
                else:
                    payload = {
                        "customer_name": e_cust.strip(),
                        "subject": e_sub.strip(),
                        "description": e_desc.strip(),
                        "category": e_cat,
                        "priority": e_prio,
                        "status": e_status,
                        "assigned_team": e_team
                    }
                    try:
                        api.update_inquiry(inq_id, payload, token=token)
                        st.success(f"Inquiry {selected_inq.get('inquiry_id')} updated successfully!")
                        st.rerun()
                    except APIError as e:
                        st.error(f"Update failed: {e.message}")

    with tab_delete:
        st.warning(f"Are you sure you want to permanently delete ticket **{selected_inq.get('inquiry_id')}**?")
        if st.button("Confirm Delete Inquiry", key=f"del_inq_{inq_id}", type="primary"):
            try:
                api.delete_inquiry(inq_id, token=token)
                st.success(f"Inquiry {selected_inq.get('inquiry_id')} deleted.")
                st.rerun()
            except APIError as e:
                st.error(f"Deletion failed: {e.message}")
