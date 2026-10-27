import streamlit as st
import pandas as pd
from api_client import api, APIError
from components import render_top_navbar, render_module_header, render_empty_state, format_datetime

MODULES = [
    'Programs',
    'Services',
    'Training',
    'Customers',
    'Inquiries',
    'Service Requests',
    'Reports',
    'Auth'
]

ACTIONS = [
    'CREATE',
    'UPDATE',
    'DELETE',
    'STATUS_CHANGE',
    'EXPORT_CSV',
    'LOGIN',
    'REGISTER'
]


def render_activity_history(token: str):
    render_top_navbar("Activity History & Audit Trails")
    col_h, col_dl = st.columns([3, 1])
    with col_h:
        render_module_header(
            "Activity History & Audit Log",
            "Immutable operational event timeline recorded directly in MongoDB for compliance and governance",
            icon_name="history"
        )
    with col_dl:
        st.write("")
        try:
            csv_data = api.get_csv_export("activity", token=token)
            st.download_button(
                label="⬇️ Export Audit Log CSV",
                data=csv_data,
                file_name="veda_activity_audit_logs.csv",
                mime="text/csv",
                use_container_width=True
            )
        except Exception:
            pass

    # Search and Filter
    f1, f2, f3, f4 = st.columns([2, 1.2, 1.2, 0.8])
    with f1:
        search = st.text_input("Search Logs", placeholder="Search description, record ID, or user...", label_visibility="collapsed")
    with f2:
        module = st.selectbox("Module Filter", ["All"] + MODULES, label_visibility="collapsed")
    with f3:
        action = st.selectbox("Action Filter", ["All"] + ACTIONS, label_visibility="collapsed")
    with f4:
        if st.button("Reset", key="reset_activity", use_container_width=True):
            st.rerun()

    # Pagination state
    if "activity_page" not in st.session_state:
        st.session_state.activity_page = 1

    limit = 25

    try:
        res = api.get_activity(
            token=token,
            search=search,
            module=module,
            action=action,
            page=st.session_state.activity_page,
            limit=limit
        )
    except APIError as e:
        st.error(f"Failed to load activity logs: {e.message}")
        return

    items = res.get("items", [])
    total = res.get("total", 0)
    total_pages = max(1, (total + limit - 1) // limit)

    st.write("")
    if not items:
        render_empty_state("No audit activities found", "No actions match your search query or filters.")
        return

    table_rows = []
    for log in items:
        table_rows.append({
            "Activity ID": log.get("activity_id", ""),
            "Action": log.get("action", ""),
            "Module": log.get("module", ""),
            "Record ID": log.get("record_id", "—"),
            "Description": log.get("description", ""),
            "User": log.get("user_identifier", "System"),
            "Timestamp": format_datetime(log.get("timestamp"))
        })

    df = pd.DataFrame(table_rows)
    st.dataframe(df, use_container_width=True, hide_index=True)

    # Pagination Controls
    st.write("")
    p1, p2, p3 = st.columns([1, 2, 1])
    with p1:
        if st.button("⬅️ Previous Page", disabled=(st.session_state.activity_page <= 1), use_container_width=True):
            st.session_state.activity_page -= 1
            st.rerun()
    with p2:
        st.markdown(
            f"<div style='text-align:center; padding:6px; color:#64748b; font-size:0.86rem;'>"
            f"Page <b>{st.session_state.activity_page}</b> of <b>{total_pages}</b> ({total} total audit records)"
            f"</div>",
            unsafe_allow_html=True
        )
    with p3:
        if st.button("Next Page ➡️", disabled=(st.session_state.activity_page >= total_pages), use_container_width=True):
            st.session_state.activity_page += 1
            st.rerun()
