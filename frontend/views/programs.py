import streamlit as st
import pandas as pd
from datetime import date
from api_client import api, APIError
from components import render_top_navbar, render_module_header, render_empty_state, format_date

CATEGORIES = [
    'Cloud & DevOps',
    'AI & Machine Learning',
    'Cybersecurity',
    'Full Stack Development',
    'Data Engineering'
]

STATUSES = ['Planned', 'Active', 'Completed', 'On Hold']


def render_programs(token: str):
    render_top_navbar("Technology Programs Management")
    render_module_header(
        "Technology Program Management",
        "Organize, plan, and monitor internal and client-facing technology initiatives",
        icon_name="cpu"
    )

    # Top search and filter bar
    f1, f2, f3, f4 = st.columns([2, 1.2, 1.2, 0.8])
    with f1:
        search = st.text_input("Search", placeholder="Search by name, description, or ID...", label_visibility="collapsed")
    with f2:
        category_options = ["All"] + CATEGORIES
        category = st.selectbox("Category", category_options, label_visibility="collapsed")
    with f3:
        status_options = ["All"] + STATUSES
        status = st.selectbox("Status", status_options, label_visibility="collapsed")
    with f4:
        if st.button("Reset", use_container_width=True):
            st.rerun()

    st.write("")

    # Form to Add New Program in an expander
    with st.expander("➕ Add New Technology Program", expanded=False):
        with st.form("create_program_form", clear_on_submit=True):
            st.subheader("Program Specification")
            c_name, c_cat = st.columns([2, 1])
            with c_name:
                p_name = st.text_input("Program Name *", placeholder="e.g., Enterprise Cloud Acceleration")
            with c_cat:
                p_category = st.selectbox("Category *", CATEGORIES)

            p_desc = st.text_area("Description *", placeholder="Comprehensive description of the technology initiative...")

            c_start, c_end, c_status = st.columns(3)
            with c_start:
                p_start = st.date_input("Start Date *", value=date.today())
            with c_end:
                p_end = st.date_input("Target End Date", value=None)
            with c_status:
                p_status = st.selectbox("Status *", STATUSES, index=0)

            submitted = st.form_submit_button("Create Program", type="primary", use_container_width=True)
            if submitted:
                if not p_name.strip() or not p_desc.strip():
                    st.error("Program Name and Description are required.")
                else:
                    payload = {
                        "name": p_name.strip(),
                        "description": p_desc.strip(),
                        "category": p_category,
                        "start_date": p_start.isoformat(),
                        "end_date": p_end.isoformat() if p_end else "",
                        "status": p_status
                    }
                    try:
                        res = api.create_program(payload, token=token)
                        st.success(f"Program '{res.get('name')}' created with ID {res.get('program_id')}!")
                        st.rerun()
                    except APIError as e:
                        st.error(f"Failed to create program: {e.message}")

    # Fetch programs with active filters
    try:
        programs = api.get_programs(token=token, search=search, category=category, status=status)
    except APIError as e:
        st.error(f"Error fetching programs: {e.message}")
        return

    st.write("")
    if not programs:
        render_empty_state("No technology programs found", "Try adjusting filters or create a new program above.")
        return

    # Display summary table
    table_rows = []
    for p in programs:
        table_rows.append({
            "Program ID": p.get("program_id", ""),
            "Name": p.get("name", ""),
            "Category": p.get("category", ""),
            "Status": p.get("status", ""),
            "Start Date": format_date(p.get("start_date")),
            "End Date": format_date(p.get("end_date")),
            "Description": p.get("description", "")
        })

    df = pd.DataFrame(table_rows)
    st.dataframe(df, use_container_width=True, hide_index=True)

    st.write("")
    st.divider()

    # Record Actions (View Details, Edit, Delete)
    st.subheader("Manage Program Record")
    options_map = {f"{p.get('program_id')} - {p.get('name')}": p for p in programs}
    selected_label = st.selectbox("Select program to view or modify:", list(options_map.keys()))
    selected_prog = options_map[selected_label]
    prog_id = selected_prog.get("program_id") or selected_prog.get("id")

    tab_view, tab_edit, tab_delete = st.tabs(["View Details", "Edit Program", "Delete Program"])

    with tab_view:
        v1, v2 = st.columns(2)
        with v1:
            st.markdown(f"**Program ID:** `{selected_prog.get('program_id')}`")
            st.markdown(f"**Program Name:** {selected_prog.get('name')}")
            st.markdown(f"**Category:** {selected_prog.get('category')}")
            st.markdown(f"**Status:** {selected_prog.get('status')}")
        with v2:
            st.markdown(f"**Start Date:** {format_date(selected_prog.get('start_date'))}")
            st.markdown(f"**End Date:** {format_date(selected_prog.get('end_date'))}")
            st.markdown(f"**Created At:** {format_date(selected_prog.get('created_at'))}")
        st.markdown(f"**Description:**")
        st.info(selected_prog.get("description", "No description provided."))

    with tab_edit:
        with st.form(f"edit_form_{prog_id}"):
            e_name = st.text_input("Program Name", value=selected_prog.get("name", ""))
            curr_cat = selected_prog.get("category")
            cat_idx = CATEGORIES.index(curr_cat) if curr_cat in CATEGORIES else 0
            e_cat = st.selectbox("Category", CATEGORIES, index=cat_idx)
            e_desc = st.text_area("Description", value=selected_prog.get("description", ""))

            e_c1, e_c2 = st.columns(2)
            with e_c1:
                e_start = st.text_input("Start Date (YYYY-MM-DD)", value=selected_prog.get("start_date", ""))
            with e_c2:
                e_end = st.text_input("End Date (YYYY-MM-DD)", value=selected_prog.get("end_date", ""))

            curr_st = selected_prog.get("status")
            st_idx = STATUSES.index(curr_st) if curr_st in STATUSES else 0
            e_status = st.selectbox("Status", STATUSES, index=st_idx)

            if st.form_submit_button("Save Changes", type="primary", use_container_width=True):
                if not e_name.strip() or not e_desc.strip():
                    st.error("Name and Description cannot be blank.")
                else:
                    payload = {
                        "name": e_name.strip(),
                        "category": e_cat,
                        "description": e_desc.strip(),
                        "start_date": e_start.strip(),
                        "end_date": e_end.strip(),
                        "status": e_status
                    }
                    try:
                        api.update_program(prog_id, payload, token=token)
                        st.success(f"Program {selected_prog.get('program_id')} updated successfully!")
                        st.rerun()
                    except APIError as e:
                        st.error(f"Update failed: {e.message}")

    with tab_delete:
        st.warning(f"Are you sure you want to permanently delete program **{selected_prog.get('program_id')}** ({selected_prog.get('name')})? This will also log an audit event in MongoDB.")
        if st.button("Confirm Delete Program", key=f"del_{prog_id}", type="primary"):
            try:
                api.delete_program(prog_id, token=token)
                st.success(f"Program {selected_prog.get('program_id')} deleted.")
                st.rerun()
            except APIError as e:
                st.error(f"Deletion failed: {e.message}")
