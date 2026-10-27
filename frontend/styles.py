import streamlit as st

def inject_custom_css():
    """
    Injects custom enterprise CSS with a professional Purple / Royal Blue theme:
    - Sidebar: #4C1D95 (Dark Purple) / #3B0764, Border: #6D28D9, Active: #6D28D9 (Primary Royal Purple)
    - Main Background: #F8FAFC, Card Background: #FFFFFF, Border: #DDD6FE
    - Text: #1E1B4B (Primary Deep Navy/Purple), #475569 (Secondary Text), #FFFFFF on dark backgrounds
    """
    custom_css = """
    <style>
    /* Google Fonts Inter */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"], .stMarkdown {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
        color: #1E1B4B;
    }

    /* Main App Background */
    .stApp {
        background-color: #F8FAFC !important;
    }

    /* Main Container Padding */
    .block-container {
        padding-top: 0rem !important;
        padding-bottom: 2rem !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
        max-width: 1540px;
    }

    /* Remove default Streamlit top header gap */
    header[data-testid="stHeader"] {
        background-color: transparent !important;
        height: 1.25rem !important;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #4C1D95 !important;
        border-right: 1px solid #6D28D9 !important;
        box-shadow: 2px 0 12px rgba(76, 29, 149, 0.25);
    }

    section[data-testid="stSidebar"] > div:first-child {
        padding-top: 1rem !important;
        padding-bottom: 1rem !important;
        padding-left: 0.85rem !important;
        padding-right: 0.85rem !important;
        background-color: #4C1D95 !important;
    }

    /* Hide Streamlit default multipage navigation list */
    div[data-testid="stSidebarNav"],
    div[data-testid="stSidebarNavItems"],
    ul[data-testid="stSidebarNavItems"],
    div[data-testid="stSidebarNavSeparator"] {
        display: none !important;
        visibility: hidden !important;
        height: 0 !important;
        max-height: 0 !important;
        margin: 0 !important;
        padding: 0 !important;
        overflow: hidden !important;
    }

    /* Navigation Buttons in Sidebar */
    section[data-testid="stSidebar"] div[data-testid="stButton"] button {
        display: flex !important;
        flex-direction: row !important;
        justify-content: flex-start !important;
        align-items: center !important;
        gap: 12px !important;
        text-align: left !important;
        border-radius: 8px !important;
        font-size: 0.88rem !important;
        padding: 9px 14px !important;
        margin-bottom: 4px !important;
        width: 100% !important;
        box-shadow: none !important;
        transition: all 0.15s ease !important;
    }

    /* Ensure text inside sidebar button is strictly left-aligned/justified, never centered */
    section[data-testid="stSidebar"] div[data-testid="stButton"] button * {
        text-align: left !important;
        justify-content: flex-start !important;
    }
    section[data-testid="stSidebar"] div[data-testid="stButton"] button div[data-testid="stMarkdownContainer"] {
        display: flex !important;
        justify-content: flex-start !important;
        align-items: center !important;
        text-align: left !important;
        flex: 1 1 auto !important;
        width: 100% !important;
    }
    section[data-testid="stSidebar"] div[data-testid="stButton"] button p {
        text-align: left !important;
        justify-content: flex-start !important;
        margin: 0 !important;
        font-size: 0.88rem !important;
        width: 100% !important;
        letter-spacing: -0.01em !important;
    }
    section[data-testid="stSidebar"] div[data-testid="stButton"] button span[data-testid="stIconMaterial"] {
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        flex-shrink: 0 !important;
        font-size: 1.15rem !important;
    }

    /* Active Nav Item: Royal Purple button */
    section[data-testid="stSidebar"] div[data-testid="stButton"] button[kind="primary"] {
        background-color: #6D28D9 !important;
        color: #FFFFFF !important;
        border: 1px solid #8B5CF6 !important;
        font-weight: 600 !important;
        border-radius: 8px !important;
        box-shadow: 0 2px 8px rgba(109, 40, 217, 0.4) !important;
    }
    section[data-testid="stSidebar"] div[data-testid="stButton"] button[kind="primary"] * {
        color: #FFFFFF !important;
    }

    /* Inactive Nav Item: light purple-white text for high contrast */
    section[data-testid="stSidebar"] div[data-testid="stButton"] button[kind="secondary"] {
        background-color: transparent !important;
        color: #E9D5FF !important;
        border: 1px solid transparent !important;
        font-weight: 500 !important;
    }
    section[data-testid="stSidebar"] div[data-testid="stButton"] button[kind="secondary"]:hover {
        background-color: rgba(255, 255, 255, 0.12) !important;
        color: #FFFFFF !important;
        border: 1px solid rgba(221, 214, 254, 0.3) !important;
    }
    section[data-testid="stSidebar"] div[data-testid="stButton"] button[kind="secondary"] * {
        color: #E9D5FF !important;
    }
    section[data-testid="stSidebar"] div[data-testid="stButton"] button[kind="secondary"]:hover * {
        color: #FFFFFF !important;
    }

    /* Specific style for logout button in sidebar footer */
    section[data-testid="stSidebar"] div.st-key-btn_logout button {
        width: 36px !important;
        height: 36px !important;
        min-width: 36px !important;
        padding: 0 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        border: 1px solid #7C3AED !important;
        border-radius: 8px !important;
        background: rgba(255, 255, 255, 0.08) !important;
        color: #E9D5FF !important;
    }
    section[data-testid="stSidebar"] div.st-key-btn_logout button:hover {
        background: #6D28D9 !important;
        border-color: #8B5CF6 !important;
        color: #FFFFFF !important;
    }
    section[data-testid="stSidebar"] div.st-key-btn_logout button * {
        color: inherit !important;
        justify-content: center !important;
        text-align: center !important;
    }

    /* Enterprise White Panels */
    .veda-panel {
        background: #FFFFFF;
        border: 1px solid #DDD6FE;
        border-radius: 12px;
        padding: 20px 22px;
        box-shadow: 0 1px 3px rgba(109, 40, 217, 0.05);
        margin-bottom: 1.25rem;
    }

    /* Status Pills */
    .status-pill {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 9999px;
        font-size: 0.74rem;
        font-weight: 600;
        letter-spacing: 0.01em;
        white-space: nowrap;
        text-align: center;
    }
    .status-open, .status-new {
        border: 1px solid #93C5FD;
        background-color: #EFF6FF;
        color: #2563EB;
    }
    .status-upcoming, .status-planned, .status-beta {
        border: 1px solid #DDD6FE;
        background-color: #F5F3FF;
        color: #6D28D9;
    }
    .status-closed, .status-deprecated, .status-completed, .status-onhold {
        border: 1px solid #CBD5E1;
        background-color: #F8FAFC;
        color: #475569;
    }
    .status-inprogress {
        border: 1px solid #FDE68A;
        background-color: #FFFBEB;
        color: #D97706;
    }
    .status-active, .status-available, .status-resolved {
        border: 1px solid #A7F3D0;
        background-color: #ECFDF5;
        color: #059669;
    }

    /* ID Badge */
    .id-pill {
        background-color: #F5F3FF;
        color: #6D28D9;
        font-weight: 700;
        font-size: 0.78rem;
        border: 1px solid #DDD6FE;
        border-radius: 6px;
        padding: 3px 8px;
        font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
        display: inline-block;
    }

    /* Activity row */
    .activity-feed-row {
        background: #F8FAFC;
        border: 1px solid #EDE9FE;
        border-radius: 8px;
        padding: 11px 14px;
        margin-bottom: 9px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 12px;
    }

    .act-tag {
        font-size: 0.68rem;
        font-weight: 700;
        border-radius: 4px;
        padding: 3px 8px;
        white-space: nowrap;
        text-transform: uppercase;
        letter-spacing: 0.02em;
    }
    .act-tag-login, .act-tag-export, .act-tag-update {
        background-color: #EDE9FE;
        color: #5B21B6;
    }
    .act-tag-create {
        background-color: #DCFCE7;
        color: #15803D;
    }
    .act-tag-status {
        background-color: #FEF3C7;
        color: #B45309;
    }
    .act-tag-delete {
        background-color: #FEE2E2;
        color: #B91C1C;
    }

    /* Form buttons in main content */
    .stButton > button {
        border-radius: 7px !important;
        font-weight: 600 !important;
        font-size: 0.86rem !important;
        padding: 0.45rem 1rem !important;
        transition: all 0.15s ease !important;
    }
    .stButton > button[kind="primary"] {
        background-color: #6D28D9 !important;
        border: 1px solid #6D28D9 !important;
        color: #FFFFFF !important;
        box-shadow: 0 2px 6px rgba(109, 40, 217, 0.3) !important;
    }
    .stButton > button[kind="primary"]:hover {
        background-color: #5B21B6 !important;
        border-color: #5B21B6 !important;
    }
    .stButton > button[kind="secondary"] {
        background-color: #FFFFFF !important;
        border: 1px solid #DDD6FE !important;
        color: #4C1D95 !important;
    }
    .stButton > button[kind="secondary"]:hover {
        background-color: #F5F3FF !important;
        border-color: #C4B5FD !important;
        color: #6D28D9 !important;
    }

    /* Streamlit Download Buttons */
    .stDownloadButton > button {
        border-radius: 7px !important;
        font-weight: 600 !important;
        font-size: 0.86rem !important;
        background-color: #FFFFFF !important;
        border: 1px solid #DDD6FE !important;
        color: #4C1D95 !important;
    }
    .stDownloadButton > button:hover {
        background-color: #F5F3FF !important;
        border-color: #6D28D9 !important;
        color: #6D28D9 !important;
    }

    /* Inputs, Textareas, Selectboxes */
    .stTextInput input, .stTextArea textarea, .stSelectbox [data-baseweb="select"] {
        border-radius: 7px !important;
        border-color: #DDD6FE !important;
        font-size: 0.88rem !important;
        background-color: #FFFFFF !important;
        color: #1E1B4B !important;
    }
    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: #6D28D9 !important;
        box-shadow: 0 0 0 2px rgba(109, 40, 217, 0.2) !important;
    }

    /* Streamlit Tabs styling */
    button[data-baseweb="tab"] {
        color: #475569 !important;
        font-weight: 600 !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        color: #6D28D9 !important;
        border-bottom-color: #6D28D9 !important;
    }

    /* Streamlit Expanders */
    div[data-testid="stExpander"] {
        background-color: #FFFFFF !important;
        border: 1px solid #DDD6FE !important;
        border-radius: 8px !important;
    }
    div[data-testid="stExpander"] summary {
        color: #4C1D95 !important;
        font-weight: 600 !important;
    }

    /* Streamlit Dataframe custom header theme override */
    div[data-testid="stDataFrame"] {
        border: 1px solid #DDD6FE !important;
        border-radius: 8px !important;
        overflow: hidden !important;
    }

    /* Hide Streamlit footer */
    footer {
        visibility: hidden !important;
    }
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)


def status_badge(status_str: str) -> str:
    """Returns an HTML string for a colored status badge matching the screenshot."""
    st_clean = (status_str or "").strip()
    st_lower = st_clean.lower()
    
    if st_lower in ["open"]:
        css = "status-open"
    elif st_lower in ["new"]:
        css = "status-new"
    elif st_lower in ["upcoming"]:
        css = "status-upcoming"
    elif st_lower in ["planned"]:
        css = "status-planned"
    elif st_lower in ["closed"]:
        css = "status-closed"
    elif st_lower in ["in progress"]:
        css = "status-inprogress"
    elif st_lower in ["active", "available", "resolved"]:
        css = "status-active"
    elif st_lower in ["completed", "deprecated", "on hold"]:
        css = "status-closed"
    else:
        css = "status-closed"
        
    return f'<span class="status-pill {css}">{st_clean}</span>'


def action_badge(action_str: str) -> str:
    """Returns an HTML badge for audit activity actions matching screenshot."""
    act = (action_str or "").upper().strip()
    if act == "LOGIN":
        return f'<span class="act-tag act-tag-login">LOGIN</span>'
    elif act == "EXPORT_CSV":
        return f'<span class="act-tag act-tag-export">EXPORT_CSV</span>'
    elif act == "CREATE":
        return f'<span class="act-tag act-tag-create">CREATE</span>'
    elif act == "UPDATE":
        return f'<span class="act-tag act-tag-update">UPDATE</span>'
    elif act == "STATUS_CHANGE":
        return f'<span class="act-tag act-tag-status">STATUS_CHANGE</span>'
    elif act == "DELETE":
        return f'<span class="act-tag act-tag-delete">DELETE</span>'
    return f'<span class="act-tag act-tag-login">{action_str}</span>'
