import streamlit as st
import pandas as pd
from api_client import api, APIError
from components import render_top_navbar, render_module_header, render_empty_state, format_date

CATEGORIES = ['Enterprise', 'SME', 'Startup', 'Academic', 'Individual']


def render_customers(token: str):
    render_top_navbar("Customer Accounts & Directory")
    render_module_header(
        "Customer Management",
        "Directory of corporate clients, academic partners, and institutional stakeholders",
        icon_name="users"
    )

    # Search and Filter
    f1, f2, f3 = st.columns([2.5, 1.5, 0.8])
    with f1:
        search = st.text_input("Search Customers", placeholder="Search by customer name, organization, or email...", label_visibility="collapsed")
    with f2:
        cat_options = ["All"] + CATEGORIES
        category = st.selectbox("Category Filter", cat_options, label_visibility="collapsed")
    with f3:
        if st.button("Reset", key="reset_customers", use_container_width=True):
            st.rerun()

    st.write("")

    # Add Customer Expander
    with st.expander("➕ Register New Customer Profile", expanded=False):
        with st.form("create_customer_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                c_name = st.text_input("Full Name *", placeholder="Contact officer or representative name")
                c_org = st.text_input("Organization / Company", placeholder="Corporate name or university")
            with c2:
                c_email = st.text_input("Email Address *", placeholder="contact@organization.com")
                c_phone = st.text_input("Phone Number", placeholder="+1 (555) 019-2834")

            c_cat = st.selectbox("Customer Category *", CATEGORIES, index=0)

            submitted = st.form_submit_button("Register Customer", type="primary", use_container_width=True)
            if submitted:
                if not c_name.strip() or not c_email.strip():
                    st.error("Name and a valid Email address are required.")
                elif "@" not in c_email:
                    st.error("Please provide a valid email format.")
                else:
                    payload = {
                        "name": c_name.strip(),
                        "organization": c_org.strip(),
                        "email": c_email.strip().lower(),
                        "phone": c_phone.strip(),
                        "customer_category": c_cat
                    }
                    try:
                        res = api.create_customer(payload, token=token)
                        st.success(f"Customer '{res.get('name')}' created with ID {res.get('customer_id')}!")
                        st.rerun()
                    except APIError as e:
                        st.error(f"Failed to register customer: {e.message}")

    # Fetch customers
    try:
        customers = api.get_customers(token=token, search=search, category=category)
    except APIError as e:
        st.error(f"Error fetching customers: {e.message}")
        return

    st.write("")
    if not customers:
        render_empty_state("No customer records found", "Try clearing your search filters or register a new customer above.")
        return

    # Table view
    table_rows = []
    for c in customers:
        table_rows.append({
            "Customer ID": c.get("customer_id", ""),
            "Name": c.get("name", ""),
            "Organization": c.get("organization", "—"),
            "Email": c.get("email", ""),
            "Phone": c.get("phone", "—"),
            "Category": c.get("customer_category", "")
        })

    df = pd.DataFrame(table_rows)
    st.dataframe(df, use_container_width=True, hide_index=True)

    st.write("")
    st.divider()

    # Manage Record
    st.subheader("Manage Customer Record")
    options_map = {f"{c.get('customer_id')} - {c.get('name')} ({c.get('organization') or 'Direct'})": c for c in customers}
    selected_label = st.selectbox("Select customer to view or edit:", list(options_map.keys()))
    selected_cust = options_map[selected_label]
    cust_id = selected_cust.get("customer_id") or selected_cust.get("id")

    tab_view, tab_edit, tab_delete = st.tabs(["View Details", "Edit Customer", "Delete Customer"])

    with tab_view:
        v1, v2 = st.columns(2)
        with v1:
            st.markdown(f"**Customer ID:** `{selected_cust.get('customer_id')}`")
            st.markdown(f"**Name:** {selected_cust.get('name')}")
            st.markdown(f"**Organization:** {selected_cust.get('organization') or '—'}")
        with v2:
            st.markdown(f"**Email:** {selected_cust.get('email')}")
            st.markdown(f"**Phone:** {selected_cust.get('phone') or '—'}")
            st.markdown(f"**Category:** {selected_cust.get('customer_category')}")

    with tab_edit:
        with st.form(f"edit_cust_{cust_id}"):
            e_name = st.text_input("Name", value=selected_cust.get("name", ""))
            e_org = st.text_input("Organization", value=selected_cust.get("organization", ""))
            e_email = st.text_input("Email", value=selected_cust.get("email", ""))
            e_phone = st.text_input("Phone", value=selected_cust.get("phone", ""))

            curr_cat = selected_cust.get("customer_category")
            cat_idx = CATEGORIES.index(curr_cat) if curr_cat in CATEGORIES else 0
            e_cat = st.selectbox("Category", CATEGORIES, index=cat_idx)

            if st.form_submit_button("Save Changes", type="primary", use_container_width=True):
                if not e_name.strip() or not e_email.strip():
                    st.error("Name and Email are required.")
                else:
                    payload = {
                        "name": e_name.strip(),
                        "organization": e_org.strip(),
                        "email": e_email.strip().lower(),
                        "phone": e_phone.strip(),
                        "customer_category": e_cat
                    }
                    try:
                        api.update_customer(cust_id, payload, token=token)
                        st.success(f"Customer {selected_cust.get('customer_id')} updated successfully!")
                        st.rerun()
                    except APIError as e:
                        st.error(f"Update failed: {e.message}")

    with tab_delete:
        st.warning(f"Are you sure you want to permanently delete **{selected_cust.get('customer_id')}** ({selected_cust.get('name')})?")
        if st.button("Confirm Delete Customer", key=f"del_cst_{cust_id}", type="primary"):
            try:
                api.delete_customer(cust_id, token=token)
                st.success(f"Customer {selected_cust.get('customer_id')} deleted.")
                st.rerun()
            except APIError as e:
                st.error(f"Deletion failed: {e.message}")
