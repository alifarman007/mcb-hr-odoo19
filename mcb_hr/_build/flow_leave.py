"""LEAVE flow — the complete click path, both sides.

Part A: an employee applies for leave.
Part B: the approver finds it and approves it.
"""
import sys
sys.path.insert(0, "/Data/odoo19_enterprise/custom-addons/mcb_hr/_build")
from flow_recorder import run_flow  # noqa: E402

LEAVE_PENDING = 15
LEAVE_APPROVED = 30   # Rashedul's approved 3-day Annual/Earned leave


def pick_leave_type(page):
    """Choose 'Annual / Earned Leave' in the autocomplete, then push the dates a
    few days out so the request does not clash with anything already booked."""
    page.keyboard.press("Control+a")
    page.keyboard.type("Annual", delay=80)
    page.wait_for_timeout(1800)
    for sel in ("li.o-autocomplete--dropdown-item:has-text('Annual')",
                ".o-autocomplete--dropdown-item:has-text('Annual')",
                "li:has-text('Annual / Earned Leave')"):
        try:
            page.locator(sel).first.click(timeout=2500)
            break
        except Exception:
            continue
    else:
        page.keyboard.press("Enter")
    page.wait_for_timeout(1500)
    # click a neutral part of the dialog so the autocomplete list closes cleanly
    for sel in (".modal-header", ".modal-title", ".modal-body"):
        try:
            page.locator(sel).first.click(timeout=1500)
            break
        except Exception:
            continue
    page.wait_for_timeout(2200)   # let the duration recompute finish


def set_dates(page):
    """Type the first and last day so the Submit Request button actually appears.

    fill() is used rather than keyboard typing: the date widget re-formats on each
    keystroke, and a stray keystroke leaves the field on today's date — which then
    collides with an existing request and hides the button behind an overlap warning.
    """
    for name, value in (("request_date_from", "09/21/2026"),
                        ("request_date_to", "09/23/2026")):
        for sel in (f"div[name='{name}'] input", f"[name='{name}'] input"):
            try:
                box = page.locator(sel).first
                if not box.count():
                    continue
                box.fill(value, timeout=3000)
                page.keyboard.press("Escape")
                page.wait_for_timeout(1200)
                break
            except Exception:
                continue
    page.wait_for_timeout(2500)   # let the duration and the button state recompute


STEPS = [
    # ---------------------------------------------------------- PART A -----
    dict(slug="open_app_launcher", goto="/odoo", wait=3.2,
         login=("rashedul", "rashedul"),
         role="EMPLOYEE (Rashedul)",
         headline="Open the Time Off app",
         instruction="After logging in you land here. Click the Time Off tile.",
         target=["a.o_app[href='/odoo/time-off']", "text=Time Off"]),

    dict(slug="timeoff_dashboard", wait=3.5,
         role="EMPLOYEE (Rashedul)",
         headline="Your leave balance is shown here",
         instruction="Check your balance first, then click the New button to start a request.",
         target=["button.btn-time-off", "role=button=New", "button:has-text('New')"]),

    dict(slug="new_leave_form", wait=3.0,
         role="EMPLOYEE (Rashedul)",
         headline="Choose the type of leave",
         instruction="Click the Time Off Type box and pick Annual / Earned Leave.",
         target=["div[name='holiday_status_id'] input", "div[name='holiday_status_id']"],
         then=[pick_leave_type], after=1.5),

    dict(slug="pick_dates", wait=2.5,
         role="EMPLOYEE (Rashedul)",
         headline="Pick your dates",
         instruction="Enter the first and last day. The system counts working days only.",
         target=["div[name='request_date_from']", "div[name='duration_display']"],
         click=False, then=[set_dates]),

    dict(slug="save_request", wait=2.0,
         role="EMPLOYEE (Rashedul)",
         headline="Send it for approval",
         instruction="Once type and dates are filled, the Submit Request button appears. Click it.",
         target=["button:has-text('Submit Request')", ".modal button.btn-primary",
                 "button:has-text('Ok')"],
         click=False),

    # ---------------------------------------------------------- PART B -----
    dict(slug="request_waiting", goto=f"/odoo/action-hr_holidays.hr_leave_action_my/{LEAVE_PENDING}",
         wait=3.5, role="EMPLOYEE (Rashedul)",
         headline="Now it says: To Approve",
         instruction="Your part is done. The request has gone to your manager.",
         target=["button:has-text('To Approve')", ".o_arrow_button:has-text('To Approve')"],
         click=False),

    dict(slug="approver_logs_in", goto="/odoo", wait=3.2,
         login=("admin", "admin"),
         role="APPROVER (Manager)",
         headline="Now the approver logs in",
         instruction="The line manager signs in with their own account and opens Time Off.",
         target=["a.o_app[href='/odoo/time-off']", "text=Time Off"]),

    dict(slug="approver_opens_management", goto="/odoo/time-off", wait=3.5,
         role="APPROVER (Manager)",
         headline="The approver logs in and opens Management",
         instruction="The manager opens the Time Off app and clicks the Management menu.",
         target=["button:has-text('Management')", "text=Management"], after=1.6),

    dict(slug="approver_menu_timeoff", wait=1.8,
         role="APPROVER (Manager)",
         headline="Choose Time Off from the menu",
         instruction="This list holds every request waiting for this manager.",
         target=["a.dropdown-item:has-text('Time Off')", ".dropdown-item:has-text('Time Off')"],
         after=3.0),

    dict(slug="approval_queue",
         goto="/odoo/action-hr_holidays.hr_leave_action_action_approve_department",
         wait=3.5, role="APPROVER (Manager)",
         headline="The request is waiting here",
         instruction="Rashedul's 3 days are shown with his balance. Click Approve on the card.",
         target=["button:has-text('Approve')", ".o_kanban_record button.btn-primary"],
         click=False,
         note="The manager can approve straight from this list — no need to open the record."),

    dict(slug="open_the_request",
         goto=f"/odoo/action-hr_holidays.hr_leave_action_action_approve_department/{LEAVE_PENDING}",
         wait=3.5, role="APPROVER (Manager)",
         headline="Or open it first to check the details",
         instruction="Click the request to see the dates, the reason and the balance, then Approve.",
         target=["button[name='action_approve']", "button:has-text('Approve')"],
         click=False),

    dict(slug="after_approval",
         goto=f"/odoo/action-hr_holidays.hr_leave_action_my/{LEAVE_APPROVED}",
         wait=3.5, role="DONE",
         headline="Approved — and the balance drops by itself",
         instruction="The status now reads Approved. The history on the right shows who approved it, and when.",
         target=["button:has-text('Approved')", ".o_arrow_button:has-text('Approved')"],
         click=False),
]

if __name__ == "__main__":
    print("LEAVE flow:")
    run_flow("leave", STEPS)
