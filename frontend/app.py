import sys
import os
from pathlib import Path

# Ensure current frontend directory is in sys.path
CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

import streamlit as st
from api_client import api, APIError
from styles import inject_custom_css
from icons import get_svg_icon
from views.dashboard import render_dashboard
from views.programs import render_programs
from views.services import render_services
from views.training_internships import render_training_internships
from views.customers import render_customers
from views.inquiries import render_inquiries
from views.service_requests import render_service_requests
from views.reports import render_reports
from views.activity_history import render_activity_history

# Configure main Streamlit page
st.set_page_config(
    page_title="Veda Technology - Business & Service Management",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject custom enterprise CSS styling
inject_custom_css()

# Initialize session state for authentication and navigation
if "auth_token" not in st.session_state:
    st.session_state.auth_token = None
if "auth_user" not in st.session_state:
    st.session_state.auth_user = None
if "nav_page" not in st.session_state:
    st.session_state.nav_page = "Dashboard"

# Navigation definitions with material icons
NAV_ITEMS = [
    {"label": "Dashboard", "icon": ":material/dashboard:"},
    {"label": "Technology Programs", "icon": ":material/memory:"},
    {"label": "Digital Services", "icon": ":material/layers:"},
    {"label": "Training & Internships", "icon": ":material/school:"},
    {"label": "Customers", "icon": ":material/group:"},
    {"label": "Customer Inquiries", "icon": ":material/chat:"},
    {"label": "Service Requests", "icon": ":material/build:"},
    {"label": "Business Reports", "icon": ":material/bar_chart:"},
    {"label": "Activity History", "icon": ":material/history:"}
]


def render_auth_view():
    """Renders the enterprise login and registration screen."""
    col_l, col_center, col_r = st.columns([1, 1.8, 1])
    with col_center:
        st.markdown(
            """
            <div style="text-align: center; margin-top: 40px; margin-bottom: 25px;">
                <div style="display:inline-block; width:54px; height:54px; line-height:54px; background:#6D28D9; color:#ffffff; font-weight:800; font-size:1.65rem; border-radius:12px; margin-bottom:12px; box-shadow: 0 4px 12px rgba(109,40,217,0.35);">V</div>
                <h2 style="margin:0; font-size:1.6rem; color:#1E1B4B; font-weight:800; letter-spacing:-0.02em;">Veda Technology</h2>
                <p style="margin:4px 0 0 0; color:#475569; font-size:0.88rem; font-weight:500;">BUSINESS & SERVICE MANAGEMENT SYSTEM</p>
            </div>
            """,
            unsafe_allow_html=True
        )

        tab_login, tab_register = st.tabs(["Sign In to System", "Register New Staff Account"])

        with tab_login:
            # Internship Demo Credentials Helper
            st.markdown(
                """
                <div style="background:#F8FAFC; border:1px solid #DDD6FE; border-radius:8px; padding:14px 16px; margin-bottom:16px; font-size:0.82rem;">
                    <div style="font-weight:700; color:#1E1B4B; margin-bottom:4px;">Internship Evaluation Demo Account:</div>
                    <div style="color:#475569;">Email: <code style="color:#6D28D9; background:#F5F3FF; padding:2px 5px; border-radius:4px; font-weight:600;">admin@vedatechnology.com</code></div>
                    <div style="color:#475569; margin-top:3px;">Password: <code style="color:#6D28D9; background:#F5F3FF; padding:2px 5px; border-radius:4px; font-weight:600;">Admin@123</code></div>
                </div>
                """,
                unsafe_allow_html=True
            )

            # Autofill demo credentials state
            if "login_email_val" not in st.session_state:
                st.session_state.login_email_val = "admin@vedatechnology.com"
            if "login_pass_val" not in st.session_state:
                st.session_state.login_pass_val = "Admin@123"

            if st.button("Autofill Admin Credentials", key="btn_autofill", use_container_width=True):
                st.session_state.login_email_val = "admin@vedatechnology.com"
                st.session_state.login_pass_val = "Admin@123"
                st.rerun()

            with st.form("login_form"):
                email = st.text_input("Email Address", value=st.session_state.login_email_val)
                password = st.text_input("Password", value=st.session_state.login_pass_val, type="password")
                submit_login = st.form_submit_button("Sign In to System", type="primary", use_container_width=True)

                if submit_login:
                    if not email.strip() or not password:
                        st.error("Please enter both email and password.")
                    else:
                        try:
                            res = api.login(email.strip(), password)
                            st.session_state.auth_token = res.get("access_token")
                            st.session_state.auth_user = res.get("user")
                            st.success(f"Welcome back, {res.get('user', {}).get('name', 'Staff')}!")
                            st.rerun()
                        except APIError as e:
                            st.error(f"Login failed: {e.message}")

        with tab_register:
            with st.form("register_form"):
                reg_name = st.text_input("Full Name *", placeholder="e.g., Trishika S")
                reg_email = st.text_input("Email Address *", placeholder="name@vedatechnology.com")
                reg_password = st.text_input("Password (min 6 characters) *", type="password")
                reg_role = st.selectbox("Role / Position", ["Staff", "Manager", "Admin"])
                submit_register = st.form_submit_button("Complete Registration", type="primary", use_container_width=True)

                if submit_register:
                    if not reg_name.strip() or not reg_email.strip() or not reg_password:
                        st.error("Please fill in all required fields.")
                    elif len(reg_password) < 6:
                        st.error("Password must be at least 6 characters long.")
                    elif "@" not in reg_email:
                        st.error("Please enter a valid email address.")
                    else:
                        try:
                            payload = {
                                "name": reg_name.strip(),
                                "email": reg_email.strip().lower(),
                                "password": reg_password,
                                "role": reg_role
                            }
                            res = api.register(payload)
                            st.session_state.auth_token = res.get("access_token")
                            st.session_state.auth_user = res.get("user")
                            st.success(f"Account registered successfully! Welcome, {res.get('user', {}).get('name')}!")
                            st.rerun()
                        except APIError as e:
                            st.error(f"Registration failed: {e.message}")


def render_authenticated_app():
    """Renders the main authenticated enterprise dashboard with dark navy sidebar navigation."""
    user = st.session_state.auth_user or {}
    token = st.session_state.auth_token

    # Sidebar setup
    with st.sidebar:
        # Top Logo & Branding
        st.markdown(
            """
            <div style="display:flex; align-items:center; gap:12px; padding:4px 0 16px 0; border-bottom:1px solid #6D28D9; margin-bottom:14px;">
                <div style="width:38px; height:38px; background:#6D28D9; border:1px solid #8B5CF6; color:#ffffff; font-weight:800; font-size:1.35rem; border-radius:8px; display:flex; align-items:center; justify-content:center; flex-shrink:0; box-shadow: 0 2px 8px rgba(0,0,0,0.2);">V</div>
                <div>
                    <div style="font-weight:700; font-size:1.02rem; color:#FFFFFF; line-height:1.2;">Veda Technology</div>
                    <div style="font-size:0.65rem; font-weight:700; letter-spacing:0.06em; color:#DDD6FE; margin-top:2px; line-height:1.25;">BUSINESS & SERVICE<br>SYSTEM</div>
                </div>
            </div>
            <div style="font-size:0.68rem; font-weight:700; letter-spacing:0.08em; color:#C4B5FD; margin:8px 0 8px 4px;">NAVIGATION</div>
            """,
            unsafe_allow_html=True
        )

        # Navigation buttons with active state highlighting
        for item in NAV_ITEMS:
            lbl = item["label"]
            ico = item["icon"]
            is_active = (st.session_state.nav_page == lbl)
            btn_kind = "primary" if is_active else "secondary"

            if st.button(
                lbl,
                icon=ico,
                key=f"nav_btn_{lbl}",
                type=btn_kind,
                use_container_width=True
            ):
                if st.session_state.nav_page != lbl:
                    st.session_state.nav_page = lbl
                    st.rerun()

        # Bottom User Profile Section
        user_name = user.get("name", "Admin Officer")
        user_initial = (user_name[0] if user_name else "A").upper()
        user_role = user.get("role", "Admin")

        st.markdown('<div style="border-top:1px solid #6D28D9; margin-top:36px; margin-bottom:14px;"></div>', unsafe_allow_html=True)
        col_prof, col_logout = st.columns([3.8, 1.2])
        with col_prof:
            st.markdown(
                f"""
                <div style="display:flex; align-items:center; gap:10px;">
                    <div style="width:34px; height:34px; border-radius:50%; background:#2563EB; border:1px solid #93C5FD; color:#ffffff; font-weight:700; font-size:0.92rem; display:flex; align-items:center; justify-content:center; flex-shrink:0;">
                        {user_initial}
                    </div>
                    <div style="min-width:0; flex:1;">
                        <div style="font-weight:700; font-size:0.84rem; color:#FFFFFF; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; line-height:1.2;">{user_name}</div>
                        <div style="font-size:0.72rem; color:#DDD6FE; margin-top:1px;">{user_role}</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
        with col_logout:
            if st.button("", icon=":material/logout:", key="btn_logout", help="Log Out"):
                st.session_state.auth_token = None
                st.session_state.auth_user = None
                st.rerun()

    # Route page rendering based on selection
    selected_page = st.session_state.nav_page

    if selected_page == "Dashboard":
        render_dashboard(token)
    elif selected_page == "Technology Programs":
        render_programs(token)
    elif selected_page == "Digital Services":
        render_services(token)
    elif selected_page == "Training & Internships":
        render_training_internships(token)
    elif selected_page == "Customers":
        render_customers(token)
    elif selected_page == "Customer Inquiries":
        render_inquiries(token)
    elif selected_page == "Service Requests":
        render_service_requests(token)
    elif selected_page == "Business Reports":
        render_reports(token)
    elif selected_page == "Activity History":
        render_activity_history(token)


def main():
    if not st.session_state.auth_token:
        render_auth_view()
    else:
        render_authenticated_app()


if __name__ == "__main__":
    main()
