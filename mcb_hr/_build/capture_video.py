"""Capture the step-by-step screenshots for the MCB HR video tutorial series.

Unlike the reference-manual captures, these follow ONE story:
  REQ/2026/0001 MEAL Officer -> Rashedul Karim wins -> hired MEAL-001
  -> leave -> TA/DA -> payroll ; plus Farzana's short-notice resignation.

Output: _build/screenshots/video/<vN_topic>/NN_<slug>.png
"""
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

BASE = "http://127.0.0.1:8069"
ROOT = Path("/Data/odoo19_enterprise/custom-addons/mcb_hr/_build/screenshots/video")
ROOT.mkdir(parents=True, exist_ok=True)

# --- story record ids (from populate_story.py) ---
EMP_RASHEDUL = 22
APPLICANT_WINNER = 50
REQ = 1
JOB = 12
LEAVE_PENDING = 15
LEAVE_APPROVED = 18
EXPENSE = 21
RESIGNATION = 3
PAYSLIP = 7
PAYSLIP_RUN = 4
GRADE_OFFICER = 5
LT_ANNUAL = 76
LT_COMPENSATORY = 3
PERDIEM = 1
STRUCTURE_PERMANENT = 6


def login(page):
    page.goto(f"{BASE}/web/login?db=mcb_demo", wait_until="domcontentloaded")
    page.fill("input[name='login']", "admin")
    page.fill("input[name='password']", "admin")
    page.click("button[type='submit']")
    try:
        page.wait_for_url(lambda u: "/web/login" not in u, timeout=30000)
    except Exception:
        pass
    time.sleep(3)


def clean(page):
    """Remove the trial-expiry overlay so it never covers a tutorial screenshot."""
    try:
        page.evaluate(
            "document.querySelectorAll('.database_expiration_panel')"
            ".forEach(e => { const o = e.closest('div[style*=\"position: absolute\"]') || e; o.remove(); })"
        )
    except Exception:
        pass


def shot(page, area, n, slug):
    d = ROOT / area
    d.mkdir(parents=True, exist_ok=True)
    out = d / f"{n:02d}_{slug}.png"
    clean(page)
    try:
        page.screenshot(path=str(out), full_page=False)
        print(f"  saved {area}/{out.name}")
    except Exception as e:
        print(f"  WARN {slug}: {e}")


def goto(page, url, wait=3.0):
    try:
        page.goto(url, wait_until="domcontentloaded", timeout=30000)
    except Exception as e:
        print(f"  WARN goto {url}: {e}")
    time.sleep(wait)
    clean(page)


def act(xmlid, rec=None):
    return f"{BASE}/odoo/action-{xmlid}" + (f"/{rec}" if rec else "")


def to_list(page):
    try:
        page.locator("button[data-tooltip='List']").first.click(timeout=2500)
        time.sleep(1.2)
    except Exception:
        pass


def tab(page, label):
    for how in (lambda: page.get_by_role("tab", name=label, exact=True).first,
                lambda: page.get_by_role("tab", name=label).first,
                lambda: page.get_by_text(label, exact=True).first):
        try:
            how().click(timeout=3500)
            time.sleep(1.2)
            return True
        except Exception:
            continue
    return False


def main():
    with sync_playwright() as pw:
        b = pw.chromium.launch(headless=True, args=["--no-sandbox"])
        ctx = b.new_context(viewport={"width": 1440, "height": 900})
        page = ctx.new_page()
        login(page)

        # ============ V0 — ORIENTATION ============
        a = "v0_overview"
        goto(page, f"{BASE}/odoo", wait=4)
        shot(page, a, 1, "home_app_launcher")
        goto(page, f"{BASE}/odoo/apps", wait=4)
        try:
            page.locator("input.o_searchview_input").first.fill("MCB")
            page.keyboard.press("Enter"); time.sleep(1.5)
        except Exception:
            pass
        shot(page, a, 2, "apps_mcb_modules")
        # anatomy of a record: statusbar + chatter + smart buttons
        goto(page, act("mcb_hr_recruitment.action_mcb_requisition", REQ), wait=3.5)
        shot(page, a, 3, "anatomy_of_a_record")

        # ============ V1 — CONFIGURATION ============
        a = "v1_config"
        goto(page, act("mcb_hr_employee.action_mcb_hr_grade"), wait=3.5)
        to_list(page); shot(page, a, 1, "grades_list_g1_g10")
        goto(page, act("mcb_hr_employee.action_mcb_hr_grade", GRADE_OFFICER), wait=3)
        shot(page, a, 2, "grade_form_officer")
        goto(page, act("hr_holidays.open_view_holiday_status"), wait=3.5)
        to_list(page); shot(page, a, 3, "leave_types_list")
        goto(page, act("hr_holidays.open_view_holiday_status", LT_ANNUAL), wait=3)
        shot(page, a, 4, "leave_type_annual_probation_block")
        goto(page, act("hr_holidays.open_view_holiday_status", LT_COMPENSATORY), wait=3)
        shot(page, a, 5, "leave_type_compensatory_ce_gate")
        goto(page, act("hr_holidays.open_view_public_holiday"), wait=3.5)
        to_list(page); shot(page, a, 6, "public_holidays_bd")
        goto(page, act("mcb_hr_expense.action_mcb_per_diem"), wait=3.5)
        to_list(page); shot(page, a, 7, "per_diem_rate_table")
        goto(page, act("mcb_hr_expense.action_mcb_per_diem", PERDIEM), wait=3)
        shot(page, a, 8, "per_diem_form_detail")
        goto(page, f"{BASE}/odoo/action-base.action_res_users", wait=3.5)
        to_list(page); shot(page, a, 9, "users_and_roles")

        # ============ V2 — REQUISITION ============
        a = "v2_requisition"
        goto(page, act("mcb_hr_recruitment.action_mcb_requisition"), wait=3.5)
        to_list(page); shot(page, a, 1, "requisition_list")
        goto(page, act("mcb_hr_recruitment.action_mcb_requisition", REQ), wait=3.5)
        shot(page, a, 2, "requisition_form_published")
        for lbl, idx in (("Position Details", 3), ("Marks Configuration", 4), ("Justification", 5)):
            if tab(page, lbl):
                shot(page, a, idx, "requisition_tab_" + lbl.split()[0].lower())
        goto(page, f"{BASE}/report/html/mcb_hr_recruitment.report_mcb_job_circular/{REQ}", wait=3.5)
        shot(page, a, 6, "job_circular_pdf")

        # ============ V3 — APPLICANTS / EXAMS / MERIT ============
        a = "v3_recruitment"
        goto(page, f"{BASE}/odoo/recruitment", wait=4)
        shot(page, a, 1, "recruitment_pipeline_kanban")
        goto(page, f"{BASE}/odoo/action-hr_recruitment.crm_case_categ0_act_job", wait=4)
        to_list(page); shot(page, a, 2, "applicants_list_with_marks")
        goto(page, f"{BASE}/odoo/action-hr_recruitment.crm_case_categ0_act_job/{APPLICANT_WINNER}", wait=3.5)
        shot(page, a, 3, "applicant_form_rashedul")
        if tab(page, "MCB Recruitment"):
            shot(page, a, 4, "applicant_mcb_tab_marks")
        goto(page, f"{BASE}/report/html/mcb_hr_recruitment.report_mcb_admit_card/{APPLICANT_WINNER}", wait=3.5)
        shot(page, a, 5, "admit_card_pdf")
        goto(page, f"{BASE}/report/html/mcb_hr_recruitment.report_mcb_admit_card_topsheet/{REQ}", wait=3.5)
        shot(page, a, 6, "admit_card_topsheet_pdf")
        goto(page, f"{BASE}/report/html/mcb_hr_recruitment.report_mcb_shortlist/{REQ}", wait=3.5)
        shot(page, a, 7, "shortlist_report_pdf")
        goto(page, act("mcb_hr_recruitment.action_mcb_recruitment_expenditure"), wait=3.5)
        to_list(page); shot(page, a, 8, "recruitment_expenditure")

        # ============ V4 — ONBOARDING ============
        a = "v4_onboarding"
        goto(page, f"{BASE}/odoo/employees", wait=4)
        to_list(page); shot(page, a, 1, "employees_list_with_codes")
        goto(page, f"{BASE}/odoo/employees/{EMP_RASHEDUL}", wait=4)
        shot(page, a, 2, "employee_form_rashedul")
        if tab(page, "MCB Profile"):
            shot(page, a, 3, "employee_mcb_profile_tab")
        for lbl, idx in (("Work Information", 4), ("HR Settings", 5)):
            if tab(page, lbl):
                shot(page, a, idx, "employee_tab_" + lbl.split()[0].lower())
        goto(page, f"{BASE}/odoo/action-mail.mail_activity_plan_action", wait=3.5)
        to_list(page); shot(page, a, 6, "activity_plans_list")

        # ============ V5 — LEAVE ============
        a = "v5_leave"
        goto(page, f"{BASE}/odoo/time-off", wait=4)
        shot(page, a, 1, "timeoff_dashboard_balances")
        goto(page, act("hr_holidays.hr_leave_action_my"), wait=3.5)
        to_list(page); shot(page, a, 2, "my_leave_requests_list")
        goto(page, act("hr_holidays.hr_leave_action_my", LEAVE_PENDING), wait=3.5)
        shot(page, a, 3, "leave_pending_approval_buttons")
        goto(page, act("hr_holidays.hr_leave_action_my", LEAVE_APPROVED), wait=3.5)
        shot(page, a, 4, "leave_approved")
        goto(page, act("hr_holidays.hr_leave_action_action_approve_department"), wait=3.5)
        to_list(page); shot(page, a, 5, "manager_approval_queue")
        goto(page, act("hr_holidays.hr_leave_action_holiday_allocation_id"), wait=3.5)
        to_list(page); shot(page, a, 6, "allocations_list")

        # ============ V6 — EXPENSE / TA-DA ============
        a = "v6_expense"
        goto(page, f"{BASE}/odoo/expenses", wait=4)
        shot(page, a, 1, "expenses_dashboard")
        goto(page, f"{BASE}/odoo/action-hr_expense.hr_expense_actions_all", wait=3.5)
        to_list(page); shot(page, a, 2, "expenses_list")
        goto(page, f"{BASE}/odoo/action-hr_expense.hr_expense_actions_all/{EXPENSE}", wait=3.5)
        shot(page, a, 3, "expense_form_ta_da")
        if tab(page, "MCB TA / DA"):
            shot(page, a, 4, "expense_mcb_tada_tab")

        # ============ V7 — PAYROLL ============
        a = "v7_payroll"
        goto(page, act("hr_payroll.action_view_hr_payroll_structure_list_form"), wait=4)
        to_list(page); shot(page, a, 1, "salary_structures_list")
        goto(page, act("hr_payroll.action_view_hr_payroll_structure_list_form", STRUCTURE_PERMANENT), wait=3.5)
        shot(page, a, 2, "structure_mcb_permanent_rules")
        goto(page, act("hr_payroll.action_hr_payslip_run"), wait=3.5)
        to_list(page); shot(page, a, 3, "payslip_batches")
        goto(page, act("hr_payroll.action_hr_payslip_run", PAYSLIP_RUN), wait=3.5)
        shot(page, a, 4, "payslip_batch_form")
        goto(page, act("hr_payroll.action_view_hr_payslip_month_form", PAYSLIP), wait=3.5)
        shot(page, a, 5, "payslip_form")
        if tab(page, "Salary Computation"):
            shot(page, a, 6, "payslip_salary_computation_lines")

        # ============ V8 — SEPARATION ============
        a = "v8_separation"
        goto(page, act("mcb_hr_separation.action_mcb_resignation"), wait=3.5)
        to_list(page); shot(page, a, 1, "resignation_list")
        goto(page, act("mcb_hr_separation.action_mcb_resignation", RESIGNATION), wait=3.5)
        shot(page, a, 2, "resignation_form_short_notice")
        for lbl, idx in (("Final Settlement", 3), ("Off-boarding", 4)):
            if tab(page, lbl):
                shot(page, a, idx, "resignation_tab_" + lbl.split()[0].lower())
        goto(page, act("mcb_hr_separation.action_mcb_exit_interview"), wait=3.5)
        to_list(page); shot(page, a, 5, "exit_interview_list")

        b.close()
        print("DONE")


if __name__ == "__main__":
    main()
