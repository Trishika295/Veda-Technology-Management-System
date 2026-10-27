import streamlit as st
import streamlit.components.v1 as components
from api_client import api, APIError
from components import render_top_navbar, format_activity_time
from styles import status_badge, action_badge


def render_dashboard(token: str):
    user = st.session_state.auth_user or {}
    user_email = user.get("email", "admin@vedatechnology.com")

    # Top Enterprise Navbar
    render_top_navbar("Enterprise Overview Dashboard", user_email=user_email)

    # Fetch live telemetry from backend
    try:
        data = api.get_dashboard(token)
    except APIError as e:
        st.error(f"Failed to fetch live dashboard telemetry: {e.message}")
        return

    recently_created = data.get("recently_created", [])
    recent_activity = data.get("recent_activity", [])
    programs_by_status = data.get("programs_by_status", {})
    requests_by_status = data.get("requests_by_status", {})
    inquiries_by_status = data.get("inquiries_by_status", {})

    # Shared CSS styling for iframe-rendered components
    iframe_head = """
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
        body { background: transparent; color: #1E1B4B; overflow: hidden; }
        .id-pill { background-color: #F5F3FF; color: #6D28D9; font-weight: 700; font-size: 0.78rem; border: 1px solid #DDD6FE; border-radius: 6px; padding: 3px 8px; font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; display: inline-block; }
        .status-pill { display: inline-block; padding: 3px 10px; border-radius: 9999px; font-size: 0.74rem; font-weight: 600; letter-spacing: 0.01em; white-space: nowrap; text-align: center; }
        .status-open, .status-new { border: 1px solid #93C5FD; background-color: #EFF6FF; color: #2563EB; }
        .status-upcoming, .status-planned, .status-beta { border: 1px solid #DDD6FE; background-color: #F5F3FF; color: #6D28D9; }
        .status-closed, .status-deprecated, .status-completed, .status-onhold { border: 1px solid #CBD5E1; background-color: #F8FAFC; color: #475569; }
        .status-inprogress { border: 1px solid #FDE68A; background-color: #FFFBEB; color: #D97706; }
        .status-active, .status-available, .status-resolved { border: 1px solid #A7F3D0; background-color: #ECFDF5; color: #059669; }
        .act-tag { font-size: 0.68rem; font-weight: 700; border-radius: 4px; padding: 3px 8px; white-space: nowrap; text-transform: uppercase; letter-spacing: 0.02em; }
        .act-tag-login, .act-tag-export, .act-tag-update { background-color: #EDE9FE; color: #5B21B6; }
        .act-tag-create { background-color: #DCFCE7; color: #15803D; }
        .act-tag-status { background-color: #FEF3C7; color: #B45309; }
        .act-tag-delete { background-color: #FEE2E2; color: #B91C1C; }
    </style>
    """

    # =========================================================================
    # UPPER SECTION: Side-by-Side Cards (Recently Created Records & Activity)
    # =========================================================================
    col_records, col_activity = st.columns([1.1, 0.9], gap="medium")

    with col_records:
        table_rows_list = []
        for r in recently_created[:6]:
            r_id = r.get("display_id") or r.get("id") or "—"
            title = r.get("title") or r.get("name") or "—"
            category = r.get("category") or ""
            mod = r.get("module") or "—"
            st_val = r.get("status") or "—"
            badge = status_badge(st_val)

            row = (
                f'<tr style="border-bottom: 1px solid #F1F5F9;">'
                f'<td style="padding: 13px 12px; vertical-align: middle;"><span class="id-pill">{r_id}</span></td>'
                f'<td style="padding: 13px 12px; vertical-align: middle;">'
                f'<div style="font-weight: 700; color: #1E1B4B; font-size: 0.85rem; line-height: 1.25; max-width: 230px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{title}</div>'
                f'<div style="font-size: 0.73rem; color: #6D28D9; font-weight: 500; margin-top: 2px;">{category}</div>'
                f'</td>'
                f'<td style="padding: 13px 12px; vertical-align: middle; color: #475569; font-size: 0.82rem;">{mod}</td>'
                f'<td style="padding: 13px 12px; vertical-align: middle; text-align: left;">{badge}</td>'
                f'</tr>'
            )
            table_rows_list.append(row)

        table_rows_html = "".join(table_rows_list)
        left_card_html = f"""<!DOCTYPE html><html><head>{iframe_head}</head><body style="padding: 0;">
        <div style="background: #FFFFFF; border: 1px solid #DDD6FE; border-radius: 12px; padding: 18px 20px; box-shadow: 0 1px 3px rgba(109,40,217,0.04); height: calc(100vh - 2px); box-sizing: border-box;">
            <table style="width: 100%; border-collapse: collapse; text-align: left;">
                <thead>
                    <tr style="border-bottom: 1px solid #DDD6FE; color: #FFFFFF; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.05em; background: #6D28D9;">
                        <th style="padding: 10px 12px; font-weight: 600; border-top-left-radius: 6px; border-bottom-left-radius: 6px;">ID</th>
                        <th style="padding: 10px 12px; font-weight: 600;">TITLE / NAME</th>
                        <th style="padding: 10px 12px; font-weight: 600;">MODULE</th>
                        <th style="padding: 10px 12px; font-weight: 600; border-top-right-radius: 6px; border-bottom-right-radius: 6px;">STATUS</th>
                    </tr>
                </thead>
                <tbody>{table_rows_html}</tbody>
            </table>
        </div></body></html>"""
        components.html(left_card_html, height=450, scrolling=False)

    with col_activity:
        activity_rows_list = []
        for act in recent_activity[:6]:
            action = act.get("action", "ACTION")
            desc = act.get("description", "—")
            module = act.get("module", "—")
            user_id = act.get("user_identifier", "System")
            time_part, date_part = format_activity_time(act.get("timestamp"))

            act_row = (
                f'<div style="background: #F8FAFC; border: 1px solid #EDE9FE; border-radius: 8px; padding: 10px 14px; margin-bottom: 8px; display: flex; align-items: center; justify-content: space-between;">'
                f'<div style="display: flex; align-items: center; gap: 10px; min-width: 0; flex: 1;">'
                f'<div style="flex-shrink: 0;">{action_badge(action)}</div>'
                f'<div style="min-width: 0; flex: 1;">'
                f'<div style="font-weight: 700; font-size: 0.83rem; color: #1E1B4B; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; line-height: 1.25;">{desc}</div>'
                f'<div style="font-size: 0.72rem; color: #475569; margin-top: 2px;">Module: {module} &nbsp;•&nbsp; User: {user_id}</div>'
                f'</div>'
                f'</div>'
                f'<div style="text-align: right; margin-left: 12px; flex-shrink: 0; line-height: 1.2;">'
                f'<div style="font-size: 0.74rem; color: #6D28D9; font-weight: 600;">{time_part}</div>'
                f'<div style="font-size: 0.71rem; color: #475569; margin-top: 1px;">{date_part}</div>'
                f'</div>'
                f'</div>'
            )
            activity_rows_list.append(act_row)

        activity_rows_html = "".join(activity_rows_list)
        right_card_html = f"""<!DOCTYPE html><html><head>{iframe_head}</head><body style="padding: 0;">
        <div style="background: #FFFFFF; border: 1px solid #DDD6FE; border-radius: 12px; padding: 18px 20px; box-shadow: 0 1px 3px rgba(109,40,217,0.04); height: calc(100vh - 2px); box-sizing: border-box;">
            {activity_rows_html}
        </div></body></html>"""
        components.html(right_card_html, height=450, scrolling=False)

    st.write("")

    # =========================================================================
    # LOWER SECTION: 3 Columns Status Distribution Breakdowns
    # =========================================================================
    sc1, sc2, sc3 = st.columns(3, gap="medium")

    # 1. Technology Programs Status
    with sc1:
        total_p = sum(programs_by_status.values()) or 1
        p_active = programs_by_status.get("Active", 0)
        p_planned = programs_by_status.get("Planned", 0)
        p_comp = programs_by_status.get("Completed", 0)
        p_hold = programs_by_status.get("On Hold", 0)

        p_items = [
            ("Active", p_active, int(p_active / total_p * 100), "#10B981"),
            ("Planned", p_planned, int(p_planned / total_p * 100), "#6D28D9"),
            ("Completed", p_comp, int(p_comp / total_p * 100), "#2563EB"),
            ("On Hold", p_hold, int(p_hold / total_p * 100), "#C4B5FD")
        ]

        p_rows = "".join([
            f'<div style="margin-bottom: 13px;">'
            f'<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 5px;">'
            f'<span style="font-size: 0.82rem; font-weight: 600; color: #1E1B4B;">{name}</span>'
            f'<span style="font-size: 0.79rem; color: #475569; font-weight: 500;">{cnt}({pct}%)</span>'
            f'</div>'
            f'<div style="width: 100%; height: 5px; background: #EDE9FE; border-radius: 9999px; overflow: hidden;">'
            f'<div style="width: {pct}%; height: 100%; background: {col}; border-radius: 9999px;"></div>'
            f'</div>'
            f'</div>'
            for name, cnt, pct, col in p_items
        ])

        p_html = f"""<!DOCTYPE html><html><head>{iframe_head}</head><body style="padding: 0;">
        <div style="background: #FFFFFF; border: 1px solid #DDD6FE; border-radius: 12px; padding: 18px 20px; box-shadow: 0 1px 3px rgba(109,40,217,0.04);">
            <div style="font-size: 0.94rem; font-weight: 700; color: #1E1B4B; margin-bottom: 16px;">Technology Programs Status</div>
            {p_rows}
        </div></body></html>"""
        components.html(p_html, height=220, scrolling=False)

    # 2. Service Requests Status
    with sc2:
        total_r = sum(requests_by_status.values()) or 1
        r_open = requests_by_status.get("Open", 0)
        r_prog = requests_by_status.get("In Progress", 0)
        r_res = requests_by_status.get("Resolved", 0)
        r_cls = requests_by_status.get("Closed", 0)

        r_items = [
            ("Open", r_open, int(r_open / total_r * 100), "#2563EB"),
            ("In Progress", r_prog, int(r_prog / total_r * 100), "#D97706"),
            ("Resolved", r_res, int(r_res / total_r * 100), "#10B981"),
            ("Closed", r_cls, int(r_cls / total_r * 100), "#6D28D9")
        ]

        r_rows = "".join([
            f'<div style="margin-bottom: 13px;">'
            f'<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 5px;">'
            f'<span style="font-size: 0.82rem; font-weight: 600; color: #1E1B4B;">{name}</span>'
            f'<span style="font-size: 0.79rem; color: #475569; font-weight: 500;">{cnt}({pct}%)</span>'
            f'</div>'
            f'<div style="width: 100%; height: 5px; background: #EDE9FE; border-radius: 9999px; overflow: hidden;">'
            f'<div style="width: {pct}%; height: 100%; background: {col}; border-radius: 9999px;"></div>'
            f'</div>'
            f'</div>'
            for name, cnt, pct, col in r_items
        ])

        r_html = f"""<!DOCTYPE html><html><head>{iframe_head}</head><body style="padding: 0;">
        <div style="background: #FFFFFF; border: 1px solid #DDD6FE; border-radius: 12px; padding: 18px 20px; box-shadow: 0 1px 3px rgba(109,40,217,0.04);">
            <div style="font-size: 0.94rem; font-weight: 700; color: #1E1B4B; margin-bottom: 16px;">Service Requests Status</div>
            {r_rows}
        </div></body></html>"""
        components.html(r_html, height=220, scrolling=False)

    # 3. Inquiries Status
    with sc3:
        total_i = sum(inquiries_by_status.values()) or 1
        i_new = inquiries_by_status.get("New", 0)
        i_prog = inquiries_by_status.get("In Progress", 0)
        i_res = inquiries_by_status.get("Resolved", 0)
        i_cls = inquiries_by_status.get("Closed", 0)

        i_items = [
            ("New", i_new, int(i_new / total_i * 100), "#2563EB"),
            ("In Progress", i_prog, int(i_prog / total_i * 100), "#D97706"),
            ("Resolved", i_res, int(i_res / total_i * 100), "#10B981"),
            ("Closed", i_cls, int(i_cls / total_i * 100), "#6D28D9")
        ]

        i_rows = "".join([
            f'<div style="margin-bottom: 13px;">'
            f'<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 5px;">'
            f'<span style="font-size: 0.82rem; font-weight: 600; color: #1E1B4B;">{name}</span>'
            f'<span style="font-size: 0.79rem; color: #475569; font-weight: 500;">{cnt}({pct}%)</span>'
            f'</div>'
            f'<div style="width: 100%; height: 5px; background: #EDE9FE; border-radius: 9999px; overflow: hidden;">'
            f'<div style="width: {pct}%; height: 100%; background: {col}; border-radius: 9999px;"></div>'
            f'</div>'
            f'</div>'
            for name, cnt, pct, col in i_items
        ])

        i_html = f"""<!DOCTYPE html><html><head>{iframe_head}</head><body style="padding: 0;">
        <div style="background: #FFFFFF; border: 1px solid #DDD6FE; border-radius: 12px; padding: 18px 20px; box-shadow: 0 1px 3px rgba(109,40,217,0.04);">
            <div style="font-size: 0.94rem; font-weight: 700; color: #1E1B4B; margin-bottom: 16px;">Inquiries Status</div>
            {i_rows}
        </div></body></html>"""
        components.html(i_html, height=220, scrolling=False)
