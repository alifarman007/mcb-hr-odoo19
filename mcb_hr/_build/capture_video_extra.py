"""Supplementary captures for the HR video script.

The marks scheme, the TA/DA fields and the final-settlement figures are NOT on
separate tabs - they sit further down the main form. Full-page screenshots show
them in context, which is what the script needs.
"""
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

BASE = "http://127.0.0.1:8069"
ROOT = Path("/Data/odoo19_enterprise/custom-addons/mcb_hr/_build/screenshots/video")

REQ, EMP, EXPENSE, RESIGNATION, PAYSLIP = 1, 22, 21, 3, 7


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
    try:
        page.evaluate(
            "document.querySelectorAll('.database_expiration_panel')"
            ".forEach(e => { const o = e.closest('div[style*=\"position: absolute\"]') || e; o.remove(); })")
    except Exception:
        pass


def grab(page, url, area, n, slug, full=True, wait=3.5):
    try:
        page.goto(url, wait_until="domcontentloaded", timeout=30000)
    except Exception as e:
        print("  WARN goto:", e)
    time.sleep(wait)
    clean(page)
    d = ROOT / area
    d.mkdir(parents=True, exist_ok=True)
    out = d / f"{n:02d}_{slug}.png"
    try:
        page.screenshot(path=str(out), full_page=full)
        print(f"  saved {area}/{out.name}  (full_page={full})")
    except Exception as e:
        print(f"  WARN {slug}: {e}")


def act(x, r=None):
    return f"{BASE}/odoo/action-{x}" + (f"/{r}" if r else "")


def main():
    with sync_playwright() as pw:
        b = pw.chromium.launch(headless=True, args=["--no-sandbox"])
        page = b.new_context(viewport={"width": 1440, "height": 900}).new_page()
        login(page)

        # whole requisition form (includes the marks scheme lower down)
        grab(page, act("mcb_hr_recruitment.action_mcb_requisition", REQ),
             "v2_requisition", 4, "requisition_full_form_marks_scheme")
        # whole employee form (MCB profile + contract details)
        grab(page, f"{BASE}/odoo/employees/{EMP}",
             "v4_onboarding", 5, "employee_full_form")
        # whole expense form (TA/DA fields + per-diem result)
        grab(page, f"{BASE}/odoo/action-hr_expense.hr_expense_actions_all/{EXPENSE}",
             "v6_expense", 4, "expense_full_form_tada_fields")
        # whole resignation form (notice + settlement figures)
        grab(page, act("mcb_hr_separation.action_mcb_resignation", RESIGNATION),
             "v8_separation", 3, "resignation_full_form_settlement")
        # whole payslip (all computation lines)
        grab(page, act("hr_payroll.action_view_hr_payslip_month_form", PAYSLIP),
             "v7_payroll", 7, "payslip_full_form")

        b.close()
        print("DONE")


if __name__ == "__main__":
    main()
