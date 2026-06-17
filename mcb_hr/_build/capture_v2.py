"""Capture screenshots for the v2.0 completions."""
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE = "http://127.0.0.1:8069"
ROOT = Path("/Data/odoo19_enterprise/custom-addons/mcb_hr/_build/screenshots")


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
    page.screenshot(path=str(out), full_page=False)
    print(f"  saved {out}")


def main():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True, args=["--no-sandbox"])
        ctx = browser.new_context(viewport={"width": 1440, "height": 900})
        page = ctx.new_page()
        login(page)

        # === Recruitment requisition with new Print buttons ===
        try:
            page.goto(f"{BASE}/web#id=1&model=mcb.hr.staff.requisition&view_type=form")
            time.sleep(4)
            shot(page, "02_recruitment", 8, "requisition_form_with_print_buttons")
        except Exception as e:
            print("WARN req form:", e)

        # === Salary revision wizard ===
        try:
            # Need an employee id. Use first MCB demo employee (Rashedul)
            page.goto(f"{BASE}/odoo/action-mcb_hr_payroll.action_mcb_salary_revision_wizard?active_model=hr.employee&active_id=1")
            time.sleep(4)
            shot(page, "03_payroll", 6, "salary_revision_wizard")
        except Exception as e:
            print("WARN salary rev:", e)

        # === Bank transfer wizard (no payslip_run? open the wizard anyway) ===
        try:
            page.goto(f"{BASE}/odoo/action-mcb_hr_payroll.action_mcb_bank_transfer_wizard")
            time.sleep(4)
            shot(page, "03_payroll", 7, "bank_transfer_wizard")
        except Exception as e:
            print("WARN bank:", e)

        # === Expense — show CE-approval section ===
        try:
            page.goto(f"{BASE}/odoo/expenses")
            time.sleep(4)
            try:
                page.locator("button[data-tooltip='List']").first.click(timeout=4000)
                time.sleep(2)
            except Exception:
                pass
            try:
                page.locator("tr.o_data_row").first.click(timeout=5000)
                time.sleep(3)
                shot(page, "06_expense", 4, "expense_with_ce_approval_block")
            except Exception:
                pass
        except Exception as e:
            print("WARN expense:", e)

        # === Leave type form showing 'block during probation' ===
        try:
            page.goto(f"{BASE}/odoo/time-off/configuration/types")
            time.sleep(4)
            try:
                page.locator("button[data-tooltip='List']").first.click(timeout=4000)
                time.sleep(2)
            except Exception:
                pass
            try:
                page.locator("tr.o_data_row:has-text('Annual')").first.click(timeout=6000)
                time.sleep(3)
                shot(page, "04_leave", 4, "leave_type_form_with_probation_block")
            except Exception:
                # fallback: any first
                page.locator("tr.o_data_row").first.click(timeout=4000)
                time.sleep(2)
                shot(page, "04_leave", 4, "leave_type_form_with_probation_block")
        except Exception as e:
            print("WARN leave type:", e)

        # === Print a Job Circular and grab a PDF preview via the report URL ===
        # The QWeb PDF view: /report/pdf/...
        # Easier: take screenshot of the HTML preview
        try:
            page.goto(f"{BASE}/report/html/mcb_hr_recruitment.report_mcb_job_circular/1")
            time.sleep(4)
            shot(page, "02_recruitment", 9, "job_circular_html_preview")
        except Exception as e:
            print("WARN job circular preview:", e)

        try:
            page.goto(f"{BASE}/report/html/mcb_hr_recruitment.report_mcb_shortlist/1")
            time.sleep(4)
            shot(page, "02_recruitment", 10, "shortlist_html_preview")
        except Exception as e:
            print("WARN shortlist preview:", e)

        try:
            page.goto(f"{BASE}/report/html/mcb_hr_recruitment.report_mcb_admit_card_topsheet/1")
            time.sleep(4)
            shot(page, "02_recruitment", 11, "admit_card_topsheet_preview")
        except Exception as e:
            print("WARN topsheet preview:", e)

        browser.close()
        print("DONE")


if __name__ == "__main__":
    main()
