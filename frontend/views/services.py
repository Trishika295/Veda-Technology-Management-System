import streamlit as st
import pandas as pd
from api_client import api, APIError
from components import render_top_navbar, render_module_header, render_empty_state, format_date

CATEGORIES = [
    'Custom Software Development',
    'Cloud Migration',
    'AI Automation',
    'Security Audit',
    'IT Consulting'
]

AVAILABILITY_STATUSES = ['Available', 'In Development', 'Beta', 'Deprecated']

TEAMS = [
    'Engineering Core',
    'Cloud Solutions',
    'AI Labs',
    'Security Ops',
    'Client Delivery'
]


def render_services(token: str):
    render_top_navbar("Digital Services Catalog")
    render_module_header(
        "Digital Service Management",
        "Catalog, availability tracking, and team ownership for client solutions",
        icon_name="server"
    )

    # Search and Filter Bar
    f1, f2, f3, f4 = st.columns([2, 1.2, 1.2, 0.8])
    with f1:
        search = st.text_input("Search Services", placeholder="Search by name, description, or ID...", label_visibility="collapsed")
    with f2:
        cat_options = ["All"] + CATEGORIES
        category = st.selectbox("Filter Category", cat_options, label_visibility="collapsed")
    with f3:
        st_options = ["All"] + AVAILABILITY_STATUSES
        status = st.selectbox("Filter Status", st_options, label_visibility="collapsed")
    with f4:
        if st.button("Reset", key="reset_services", use_container_width=True):
            st.rerun()

    st.write("")

    # Add Service Expander
    with st.expander("➕ Register New Digital Service", expanded=False):
        with st.form("create_service_form", clear_on_submit=True):
            c_name, c_cat = st.columns([2, 1])
            with c_name:
                s_name = st.text_input("Service Name *", placeholder="e.g., Cloud Migration Architecture")
            with c_cat:
                s_cat = st.selectbox("Category *", CATEGORIES)

            s_desc = st.text_area("Description *", placeholder="Detailed capabilities and delivery specifications...")

            c_st, c_team = st.columns(2)
            with c_st:
                s_status = st.selectbox("Availability Status *", AVAILABILITY_STATUSES, index=0)
            with c_team:
                s_team = st.selectbox("Assigned Team *", TEAMS, index=0)

            submitted = st.form_submit_button("Register Service", type="primary", use_container_width=True)
            if submitted:
                if not s_name.strip() or not s_desc.strip():
                    st.error("Service Name and Description are required.")
                else:
                    payload = {
                        "name": s_name.strip(),
                        "description": s_desc.strip(),
                        "category": s_cat,
                        "availability_status": s_status,
                        "assigned_team": s_team
                    }
                    try:
                        res = api.create_service(payload, token=token)
                        st.success(f"Digital Service '{res.get('name')}' created with ID {res.get('service_id')}!")
                        st.rerun()
                    except APIError as e:
                        st.error(f"Failed to register service: {e.message}")

    # Fetch services
    try:
        services = api.get_services(token=token, search=search, category=category, status=status)
    except APIError as e:
        st.error(f"Error fetching services: {e.message}")
        return

    st.write("")
    if not services:
        render_empty_state("No digital services found", "Try clearing filters or register a new service above.")
        return

    # Table view
    table_rows = []
    for s in services:
        table_rows.append({
            "Service ID": s.get("service_id", ""),
            "Service Name": s.get("name", ""),
            "Category": s.get("category", ""),
            "Availability": s.get("availability_status", ""),
            "Assigned Team": s.get("assigned_team", ""),
            "Description": s.get("description", "")
        })

    df = pd.DataFrame(table_rows)
    st.dataframe(df, use_container_width=True, hide_index=True)

    st.write("")
    st.divider()

    # Manage Record
    st.subheader("Manage Service Record")
    options_map = {f"{s.get('service_id')} - {s.get('name')}": s for s in services}
    selected_label = st.selectbox("Select digital service to view or modify:", list(options_map.keys()))
    selected_svc = options_map[selected_label]
    svc_id = selected_svc.get("service_id") or selected_svc.get("id")

    tab_view, tab_edit, tab_delete = st.tabs(["View Details", "Edit Service", "Delete Service"])

    with tab_view:
        v1, v2 = st.columns(2)
        with v1:
            st.markdown(f"**Service ID:** `{selected_svc.get('service_id')}`")
            st.markdown(f"**Service Name:** {selected_svc.get('name')}")
            st.markdown(f"**Category:** {selected_svc.get('category')}")
        with v2:
            st.markdown(f"**Availability Status:** {selected_svc.get('availability_status')}")
            st.markdown(f"**Assigned Team:** {selected_svc.get('assigned_team')}")
            st.markdown(f"**Last Updated:** {format_date(selected_svc.get('updated_at'))}")
        st.markdown("**Description:**")
        st.info(selected_svc.get("description", "No description provided."))

    with tab_edit:
        with st.form(f"edit_service_form_{svc_id}"):
            e_name = st.text_input("Service Name", value=selected_svc.get("name", ""))
            curr_cat = selected_svc.get("category")
            cat_idx = CATEGORIES.index(curr_cat) if curr_cat in CATEGORIES else 0
            e_cat = st.selectbox("Category", CATEGORIES, index=cat_idx)
            e_desc = st.text_area("Description", value=selected_svc.get("description", ""))

            e_c1, e_c2 = st.columns(2)
            with e_c1:
                curr_st = selected_svc.get("availability_status")
                st_idx = AVAILABILITY_STATUSES.index(curr_st) if curr_st in AVAILABILITY_STATUSES else 0
                e_status = st.selectbox("Availability Status", AVAILABILITY_STATUSES, index=st_idx)
            with e_c2:
                curr_team = selected_svc.get("assigned_team")
                team_idx = TEAMS.index(curr_team) if curr_team in TEAMS else 0
                e_team = st.selectbox("Assigned Team", TEAMS, index=team_idx)

            if st.form_submit_button("Save Changes", type="primary", use_container_width=True):
                if not e_name.strip() or not e_desc.strip():
                    st.error("Name and Description are required.")
                else:
                    payload = {
                        "name": e_name.strip(),
                        "category": e_cat,
                        "description": e_desc.strip(),
                        "availability_status": e_status,
                        "assigned_team": e_team
                    }
                    try:
                        api.update_service(svc_id, payload, token=token)
                        st.success(f"Service {selected_svc.get('service_id')} updated successfully!")
                        st.rerun()
                    except APIError as e:
                        st.error(f"Update failed: {e.message}")

    with tab_delete:
        st.warning(f"Are you sure you want to permanently delete **{selected_svc.get('service_id')}** ({selected_svc.get('name')})?")
        if st.button("Confirm Delete Service", key=f"del_svc_{svc_id}", type="primary"):
            try:
                api.delete_service(svc_id, token=token)
                st.success(f"Service {selected_svc.get('service_id')} deleted.")
                st.rerun()
            except APIError as e:
                st.error(f"Deletion failed: {e.message}")
