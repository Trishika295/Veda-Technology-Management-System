from datetime import datetime
from typing import Optional, Any
import streamlit as st
from icons import get_svg_icon


def render_top_navbar(title: str = "Enterprise Overview Dashboard", user_email: str = "admin@vedatechnology.com"):
    """
    Renders top enterprise header with professional Purple / Royal Blue styling:
    - Left: 'Enterprise Overview Dashboard' in #1E1B4B
    - Right: '● MongoDB Active' pill badge and user icon with user email
    """
    user_svg = get_svg_icon("users", size=15, color="#6D28D9", stroke_width=1.8)
    html = (
        f'<div style="display:flex; justify-content:space-between; align-items:center; padding:12px 24px; background:#FFFFFF; border-bottom:1px solid #DDD6FE; margin:-1.5rem -2rem 1.5rem -2rem;">'
        f'<div style="font-size:1.15rem; font-weight:700; color:#1E1B4B; letter-spacing:-0.01em;">{title}</div>'
        f'<div style="display:flex; align-items:center; gap:16px;">'
        f'<div style="display:flex; align-items:center; gap:6px; background:#ECFDF5; border:1px solid #A7F3D0; padding:4px 12px; border-radius:9999px; font-size:0.75rem; font-weight:600; color:#059669;">'
        f'<span style="width:7px; height:7px; border-radius:50%; background:#10B981; display:inline-block;"></span>'
        f'MongoDB Active'
        f'</div>'
        f'<div style="display:flex; align-items:center; gap:6px; font-size:0.82rem; color:#475569;">'
        f'{user_svg}'
        f'<span>{user_email}</span>'
        f'</div>'
        f'</div>'
        f'</div>'
    )
    st.markdown(html, unsafe_allow_html=True)


def render_module_header(title: str, subtitle: str = "", icon_name: str = "dashboard"):
    """Renders a standard module page header with a professional royal purple line icon."""
    svg_html = get_svg_icon(icon_name, size=22, color="#6D28D9", stroke_width=2.0)
    sub_html = f'<p style="font-size:0.88rem; color:#475569; margin:4px 0 0 0;">{subtitle}</p>' if subtitle else ''
    html = (
        f'<div style="display:flex; align-items:flex-start; gap:14px; margin-bottom:1.5rem; padding-bottom:1rem; border-bottom:1px solid #DDD6FE;">'
        f'<div style="width:40px; height:40px; border-radius:10px; background:#F5F3FF; border:1px solid #DDD6FE; display:flex; align-items:center; justify-content:center; flex-shrink:0; margin-top:2px;">'
        f'{svg_html}'
        f'</div>'
        f'<div>'
        f'<h1 style="font-size:1.5rem; font-weight:800; color:#1E1B4B; margin:0; letter-spacing:-0.02em;">{title}</h1>'
        f'{sub_html}'
        f'</div>'
        f'</div>'
    )
    st.markdown(html, unsafe_allow_html=True)


def render_metric_card(
    label: str,
    value: Any,
    subtext: str,
    icon_name: str,
    icon_color: str,
    icon_bg: str
):
    """Renders a responsive metric card."""
    svg_html = get_svg_icon(icon_name, size=18, color=icon_color, stroke_width=2.0)
    html = (
        f'<div class="veda-metric-card" style="background:#FFFFFF; border:1px solid #DDD6FE; border-radius:12px; padding:18px 20px;">'
        f'<div>'
        f'<div class="veda-metric-top" style="display:flex; justify-content:space-between; align-items:center;">'
        f'<span class="veda-metric-label" style="color:#475569; font-weight:600; font-size:0.82rem; text-transform:uppercase;">{label}</span>'
        f'<div class="veda-metric-icon-box" style="background-color: {icon_bg}; width:34px; height:34px; border-radius:8px; display:flex; align-items:center; justify-content:center;">{svg_html}</div>'
        f'</div>'
        f'<div class="veda-metric-value" style="font-size:1.6rem; font-weight:800; color:#1E1B4B; margin-top:6px;">{value}</div>'
        f'</div>'
        f'<div class="veda-metric-subtext" style="color:#6D28D9; font-size:0.78rem; font-weight:500; margin-top:4px;">{subtext}</div>'
        f'</div>'
    )
    st.markdown(html, unsafe_allow_html=True)


def render_stat_card(
    label: str,
    value: Any,
    subtext: str = "",
    icon_name: str = "dashboard",
    icon_color: str = "#6D28D9",
    icon_bg: str = "#F5F3FF"
):
    """Alias for render_metric_card."""
    render_metric_card(label, value, subtext, icon_name, icon_color, icon_bg)


def render_empty_state(title: str, message: str, icon_name: str = "clipboard-list"):
    """Renders a refined empty-state placeholder with a clean line icon."""
    svg_html = get_svg_icon(icon_name, size=28, color="#6D28D9", stroke_width=1.5)
    html = (
        f'<div style="text-align: center; padding: 42px 20px; background: #FFFFFF; border: 1px dashed #DDD6FE; border-radius: 10px; margin: 16px 0;">'
        f'<div style="display:flex; justify-content:center; margin-bottom:10px;">{svg_html}</div>'
        f'<div style="font-weight: 700; font-size: 0.96rem; color: #1E1B4B; margin-bottom: 4px;">{title}</div>'
        f'<div style="font-size: 0.84rem; color: #475569; max-width: 440px; margin: 0 auto;">{message}</div>'
        f'</div>'
    )
    st.markdown(html, unsafe_allow_html=True)


def format_activity_time(iso_str: Optional[str]):
    """Returns (time_str, date_str) like ('03:26 pm', '24 Oct') matching the screenshot."""
    if not iso_str:
        return "—", ""
    try:
        clean_str = str(iso_str).replace("Z", "+00:00")
        dt = datetime.fromisoformat(clean_str)
        time_part = dt.strftime("%I:%M %p").lower()
        date_part = dt.strftime("%d %b")
        return time_part, date_part
    except Exception:
        return str(iso_str)[:10], ""


def format_datetime(iso_str: Optional[str]) -> str:
    """Converts ISO timestamp into readable date string."""
    if not iso_str:
        return "—"
    try:
        clean_str = str(iso_str).replace("Z", "+00:00")
        dt = datetime.fromisoformat(clean_str)
        return dt.strftime("%b %d, %Y %I:%M %p")
    except Exception:
        return str(iso_str)[:19]


def format_date(date_str: Optional[str]) -> str:
    """Formats YYYY-MM-DD or ISO string into human date."""
    if not date_str:
        return "—"
    try:
        if "T" in str(date_str):
            date_str = str(date_str).split("T")[0]
        dt = datetime.strptime(str(date_str), "%Y-%m-%d")
        return dt.strftime("%b %d, %Y")
    except Exception:
        return str(date_str)
