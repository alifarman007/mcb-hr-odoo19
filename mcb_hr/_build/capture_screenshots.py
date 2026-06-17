"""Playwright-driven screenshot tour of the MCB HR module.

Run from the project root with the dev server already running on 127.0.0.1:8069.

Saves PNGs into _build/screenshots/<area>/NN_<slug>.png
"""
import time
from pathlib import Path

from playwright.sync_api import sync_playwright


BASE = "http://127.0.0.1:8069"
ROOT = Path("/Data/odoo19_enterprise/custom-addons/mcb_hr/_build/screenshots")
ROOT.mkdir(parents=True, exist_ok=True)


def login(page):
    page.goto(f"{BASE}/web/login", wait_until="domcontentloaded")
    page.fill("input[name='login']", "admin")
    page.fill("input[name='password']", "admin")
    page.click("button[type='submit']")
    try:
        page.wait_for_url(lambda url: "/web/login" not in url, timeout=30000)
    except Exception:
        pass
    time.sleep(3)


def shot(page, area, n, slug):
    area_dir = ROOT / area
    area_dir.mkdir(parents=True, exist_ok=True)
    out = area_dir / f"{n:02d}_{slug}.png"
    try:
        page.screenshot(path=str(out), full_page=False)
        print(f"  saved {out}")
    except Exception as e:
        print(f"  WARN screenshot {slug}: {e}")
    return out


def goto(page, url, wait=3.0):
    try:
        page.goto(url, wait_until="domcontentloaded", timeout=30000)
    except Exception as e:
        print(f"  WARN goto {url}: {e}")
    time.sleep(wait)


def try_click(page, *locators, wait=1.5):
    """Try several locators, return True if any succeeded."""
    for loc in locators:
        try:
            loc.first.click(timeout=4000)
            time.sleep(wait)
            return True
        except Exception:
            continue
    return False


def switch_to_list_view(page):
    """If the current view is kanban, switch to list view."""
    try:
        page.locator("button[data-tooltip='List']").first.click(timeout=2500)
        time.sleep(1.0)
        return True
    except Exception:
        pass
    try:
        page.get_by_role("button", name="List").first.click(timeout=2500)
        time.sleep(1.0)
        return True
    except Exception:
        return False


def open_first_row(page):
    """Open the first row of a list view."""
    # Try list cell
    try:
        page.locator("tr.o_data_row").first.click(timeout=5000)
        time.sleep(2.0)
        return True
    except Exception:
        pass
    try:
        page.locator("td.o_data_cell").first.click(timeout=5000)
        time.sleep(2.0)
        return True
    except Exception:
        pass
    # Try kanban card
    try:
        page.locator(".o_kanban_record").first.click(timeout=5000)
        time.sleep(2.0)
        return True
    except Exception:
        return False


def click_tab(page, label):
    try:
        page.get_by_role("tab", name=label, exact=True).first.click(timeout=4000)
        time.sleep(1.0)
        return True
    except Exception:
        pass
    try:
        page.get_by_text(label, exact=True).first.click(timeout=4000)
        time.sleep(1.0)
        return True
    except Exception:
        return False


def main():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True, args=["--no-sandbox"])
        ctx = browser.new_context(viewport={"width": 1440, "height": 900})
        page = ctx.new_page()

        login(page)

        # === 0. OVERVIEW ===
        area = "00_overview"
        goto(page, f"{BASE}/odoo/apps", wait=4)
        try:
            page.locator("input.o_searchview_input").first.fill("MCB")
            page.keyboard.press("Enter")
            time.sleep(1.5)
        except Exception:
            pass
        shot(page, area, 1, "apps_mcb_filtered")
        # Open the main MCB HR menu
        goto(page, f"{BASE}/odoo", wait=3)
        shot(page, area, 2, "home_dashboard")

        # === 1. EMPLOYEE ===
        area = "01_employee"
        goto(page, f"{BASE}/odoo/employees", wait=4)
        switch_to_list_view(page)
        shot(page, area, 1, "employee_list")
        # Open first row
        if open_first_row(page):
            shot(page, area, 2, "employee_form_default")
            # Switch to MCB tab
            if click_tab(page, "MCB Profile"):
                shot(page, area, 3, "employee_form_mcb_profile")
        # Grade list
        goto(page, f"{BASE}/odoo/action-mcb_hr_employee.action_mcb_hr_grade", wait=3)
        shot(page, area, 4, "grades_list")
        # MCB HR root menu
        goto(page, f"{BASE}/odoo", wait=3)
        try:
            page.locator("a.o_app:has-text('MCB HR')").first.click(timeout=5000)
            time.sleep(2.5)
            shot(page, area, 5, "mcb_app_landing")
        except Exception:
            pass

        # === 2. RECRUITMENT ===
        area = "02_recruitment"
        goto(page, f"{BASE}/odoo/action-mcb_hr_recruitment.action_mcb_requisition", wait=4)
        switch_to_list_view(page)
        shot(page, area, 1, "requisition_list")
        if open_first_row(page):
            shot(page, area, 2, "requisition_form")
        # Recruitment pipeline (kanban)
        goto(page, f"{BASE}/odoo/recruitment", wait=4)
        shot(page, area, 3, "recruitment_kanban_pipeline")
        # Applicants list — switch to list view to see custom columns
        try:
            page.locator("button:has-text('Applications')").first.click(timeout=4000)
            time.sleep(2)
        except Exception:
            pass
        try:
            switch_to_list_view(page)
            shot(page, area, 4, "applicant_list_with_marks")
        except Exception:
            pass
        # Open applicant form
        if open_first_row(page):
            shot(page, area, 5, "applicant_form_default")
            if click_tab(page, "MCB Recruitment"):
                shot(page, area, 6, "applicant_mcb_recruitment_tab")
        # Expenditure
        goto(page, f"{BASE}/odoo/action-mcb_hr_recruitment.action_mcb_recruitment_expenditure", wait=3)
        shot(page, area, 7, "expenditure_list")

        # === 3. PAYROLL ===
        area = "03_payroll"
        goto(page, f"{BASE}/odoo/action-hr_payroll.action_view_hr_payroll_structure_list_form", wait=4)
        switch_to_list_view(page)
        shot(page, area, 1, "salary_structures_list")
        # Open MCB Permanent structure
        try:
            page.locator("tr.o_data_row:has-text('MCB Permanent Monthly')").first.click(timeout=5000)
            time.sleep(2)
            shot(page, area, 2, "salary_structure_mcb_permanent")
        except Exception:
            pass
        # Salary rules
        goto(page, f"{BASE}/odoo/action-hr_payroll.action_salary_rule_form", wait=4)
        switch_to_list_view(page)
        shot(page, area, 3, "salary_rules_list")
        # Payslips dashboard
        goto(page, f"{BASE}/odoo/payroll", wait=4)
        shot(page, area, 4, "payslips_dashboard")
        # Structure types
        goto(page, f"{BASE}/odoo/action-hr_payroll.action_hr_payroll_structure_type", wait=4)
        switch_to_list_view(page)
        shot(page, area, 5, "structure_types_list")

        # === 4. LEAVE ===
        area = "04_leave"
        goto(page, f"{BASE}/odoo/time-off", wait=4)
        shot(page, area, 1, "time_off_dashboard")
        # Leave types
        goto(page, f"{BASE}/odoo/time-off/configuration/types", wait=4)
        switch_to_list_view(page)
        shot(page, area, 2, "leave_types_mcb")
        # Public holidays (resource calendar leaves) — use working hours menu
        goto(page, f"{BASE}/odoo/employees/working-hours", wait=4)
        shot(page, area, 3, "working_hours_list")

        # === 5. ONBOARDING ===
        area = "05_onboarding"
        goto(page, f"{BASE}/odoo/employees", wait=4)
        switch_to_list_view(page)
        if open_first_row(page):
            click_tab(page, "MCB Profile")
            shot(page, area, 1, "employee_mcb_with_onboarding_section")
        # Activity plans
        try:
            page.goto(f"{BASE}/odoo/action-mail.mail_activity_plan_action", timeout=30000)
            time.sleep(3)
            shot(page, area, 2, "activity_plans_list")
            try:
                page.locator("tr.o_data_row:has-text('MCB Employee Onboarding')").first.click(timeout=5000)
                time.sleep(2)
                shot(page, area, 3, "mcb_onboarding_plan_form")
            except Exception:
                pass
        except Exception:
            pass

        # === 6. EXPENSE / TA-DA ===
        area = "06_expense"
        goto(page, f"{BASE}/odoo/expenses", wait=4)
        shot(page, area, 1, "expense_dashboard")
        # Per diem
        goto(page, f"{BASE}/odoo/action-mcb_hr_expense.action_mcb_per_diem", wait=3)
        shot(page, area, 2, "per_diem_rates")
        # Open expense
        goto(page, f"{BASE}/odoo/expenses", wait=4)
        switch_to_list_view(page)
        if open_first_row(page):
            shot(page, area, 3, "expense_form_mcb_ta_da")

        # === 7. SEPARATION ===
        area = "07_separation"
        goto(page, f"{BASE}/odoo/action-mcb_hr_separation.action_mcb_resignation", wait=4)
        shot(page, area, 1, "resignation_list_empty")
        # Create new (open form)
        try:
            page.locator("button.o_list_button_add").first.click(timeout=5000)
            time.sleep(2)
            shot(page, area, 2, "resignation_form_new")
        except Exception:
            pass
        goto(page, f"{BASE}/odoo/action-mcb_hr_separation.action_mcb_exit_interview", wait=3)
        shot(page, area, 3, "exit_interview_list")

        browser.close()
        print("DONE")


if __name__ == "__main__":
    main()
