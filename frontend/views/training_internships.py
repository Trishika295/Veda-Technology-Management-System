import streamlit as st
import pandas as pd
from datetime import date
from api_client import api, APIError
from components import render_top_navbar, render_module_header, render_empty_state, format_date

PROGRAM_TYPES = ['Training', 'Internship']
STATUSES = ['Upcoming', 'Open', 'Closed', 'Completed']


def render_training_internships(token: str):
    render_top_navbar("Training & Internship Cohorts")
    render_module_header(
        "Training & Internship Management",
        "Coordinate academic technical bootcamps, student quotas, and enterprise internship cohorts",
        icon_name="graduation-cap"
    )

    # Search and Filters
    f1, f2, f3, f4 = st.columns([2, 1.2, 1.2, 0.8])
    with f1:
        search = st.text_input("Search Cohorts", placeholder="Search by title, description, or ID...", label_visibility="collapsed")
    with f2:
        type_options = ["All"] + PROGRAM_TYPES
        selected_type = st.selectbox("Cohort Type", type_options, label_visibility="collapsed")
    with f3:
        status_options = ["All"] + STATUSES
        selected_status = st.selectbox("Status", status_options, label_visibility="collapsed")
    with f4:
        if st.button("Reset", key="reset_training", use_container_width=True):
            st.rerun()

    st.write("")

    # Add Program Expander
    with st.expander("➕ Register New Training / Internship Program", expanded=False):
        with st.form("create_training_form", clear_on_submit=True):
            c_title, c_type = st.columns([2, 1])
            with c_title:
                t_title = st.text_input("Program Title *", placeholder="e.g., Full-Stack Cloud & DevOps Bootcamp")
            with c_type:
                t_type = st.selectbox("Type *", PROGRAM_TYPES)

            t_desc = st.text_area("Description *", placeholder="Curriculum summary, learning objectives, and cohort schedule...")

            c_dur, c_seats, c_dead, c_st = st.columns(4)
            with c_dur:
                t_dur = st.text_input("Duration *", value="12 Weeks")
            with c_seats:
                t_seats = st.number_input("Available Seats", min_value=1, max_value=500, value=25)
            with c_dead:
                t_deadline = st.date_input("Deadline", value=date.today())
            with c_st:
                t_status = st.selectbox("Status *", STATUSES, index=1)

            t_elig = st.text_input("Eligibility Criteria *", value="Undergraduate / Graduate STEM students or recent passouts")

            submitted = st.form_submit_button("Register Program Cohort", type="primary", use_container_width=True)
            if submitted:
                if not t_title.strip() or not t_dur.strip() or not t_elig.strip():
                    st.error("Title, Duration, and Eligibility criteria are required.")
                else:
                    payload = {
                        "title": t_title.strip(),
                        "program_type": t_type,
                        "description": t_desc.strip(),
                        "duration": t_dur.strip(),
                        "eligibility": t_elig.strip(),
                        "available_seats": int(t_seats),
                        "application_deadline": t_deadline.isoformat(),
                        "status": t_status
                    }
                    try:
                        res = api.create_training_program(payload, token=token)
                        st.success(f"{res.get('program_type')} '{res.get('title')}' created with ID {res.get('program_id')}!")
                        st.rerun()
                    except APIError as e:
                        st.error(f"Failed to register program: {e.message}")

    # Fetch programs
    try:
        programs = api.get_training_programs(token=token, search=search, program_type=selected_type, status=selected_status)
    except APIError as e:
        st.error(f"Error fetching training programs: {e.message}")
        return

    st.write("")
    if not programs:
        render_empty_state("No training programs found", "Adjust your search filters or register a new cohort above.")
        return

    # Table view
    table_rows = []
    for t in programs:
        table_rows.append({
            "Program ID": t.get("program_id", ""),
            "Title": t.get("title", ""),
            "Type": t.get("program_type", ""),
            "Duration": t.get("duration", ""),
            "Seats": t.get("available_seats", 0),
            "Deadline": format_date(t.get("application_deadline")),
            "Status": t.get("status", ""),
            "Eligibility": t.get("eligibility", "")
        })

    df = pd.DataFrame(table_rows)
    st.dataframe(df, use_container_width=True, hide_index=True)

    st.write("")
    st.divider()

    # Manage Record
    st.subheader("Manage Cohort Record")
    options_map = {f"{t.get('program_id')} - {t.get('title')} ({t.get('program_type')})": t for t in programs}
    selected_label = st.selectbox("Select cohort to view or edit:", list(options_map.keys()))
    selected_item = options_map[selected_label]
    prog_id = selected_item.get("program_id") or selected_item.get("id")

    tab_view, tab_edit, tab_delete = st.tabs(["View Details", "Edit Program", "Delete Program"])

    with tab_view:
        v1, v2 = st.columns(2)
        with v1:
            st.markdown(f"**Program ID:** `{selected_item.get('program_id')}`")
            st.markdown(f"**Title:** {selected_item.get('title')}")
            st.markdown(f"**Type:** {selected_item.get('program_type')}")
            st.markdown(f"**Status:** {selected_item.get('status')}")
        with v2:
            st.markdown(f"**Duration:** {selected_item.get('duration')}")
            st.markdown(f"**Available Seats:** {selected_item.get('available_seats')}")
            st.markdown(f"**Application Deadline:** {format_date(selected_item.get('application_deadline'))}")
        st.markdown(f"**Eligibility Requirements:** {selected_item.get('eligibility')}")
        st.markdown("**Description:**")
        st.info(selected_item.get("description", "No description provided."))

    with tab_edit:
        with st.form(f"edit_training_{prog_id}"):
            e_title = st.text_input("Program Title", value=selected_item.get("title", ""))
            curr_type = selected_item.get("program_type")
            t_idx = PROGRAM_TYPES.index(curr_type) if curr_type in PROGRAM_TYPES else 0
            e_type = st.selectbox("Type", PROGRAM_TYPES, index=t_idx)

            e_desc = st.text_area("Description", value=selected_item.get("description", ""))

            ec1, ec2, ec3, ec4 = st.columns(4)
            with ec1:
                e_dur = st.text_input("Duration", value=selected_item.get("duration", "12 Weeks"))
            with ec2:
                e_seats = st.number_input("Available Seats", min_value=1, max_value=500, value=int(selected_item.get("available_seats", 25)))
            with ec3:
                e_deadline = st.text_input("Deadline (YYYY-MM-DD)", value=selected_item.get("application_deadline", ""))
            with ec4:
                curr_st = selected_item.get("status")
                st_idx = STATUSES.index(curr_st) if curr_st in STATUSES else 0
                e_status = st.selectbox("Status", STATUSES, index=st_idx)

            e_elig = st.text_input("Eligibility", value=selected_item.get("eligibility", ""))

            if st.form_submit_button("Save Changes", type="primary", use_container_width=True):
                if not e_title.strip() or not e_dur.strip():
                    st.error("Title and Duration are required.")
                else:
                    payload = {
                        "title": e_title.strip(),
                        "program_type": e_type,
                        "description": e_desc.strip(),
                        "duration": e_dur.strip(),
                        "eligibility": e_elig.strip(),
                        "available_seats": int(e_seats),
                        "application_deadline": e_deadline.strip(),
                        "status": e_status
                    }
                    try:
                        api.update_training_program(prog_id, payload, token=token)
                        st.success(f"Program {selected_item.get('program_id')} updated successfully!")
                        st.rerun()
                    except APIError as e:
                        st.error(f"Update failed: {e.message}")

    with tab_delete:
        st.warning(f"Are you sure you want to permanently delete **{selected_item.get('program_id')}** ({selected_item.get('title')})?")
        if st.button("Confirm Delete Program", key=f"del_trn_{prog_id}", type="primary"):
            try:
                api.delete_training_program(prog_id, token=token)
                st.success(f"Program {selected_item.get('program_id')} deleted.")
                st.rerun()
            except APIError as e:
                st.error(f"Deletion failed: {e.message}")
