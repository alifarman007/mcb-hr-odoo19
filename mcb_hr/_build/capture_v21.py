"""Re-capture screenshots that changed in the v2.1 client-feedback round."""
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
        page.wait_for_url(lambda u: "/web/login" not in u, timeout=30000)
    except Exception:
        pass
    time.sleep(3)


def main():
    with sync_playwright() as pw:
        b = pw.chromium.launch(headless=True, args=["--no-sandbox"])
        ctx = b.new_context(viewport={"width": 1440, "height": 900})
        page = ctx.new_page()
        login(page)

        # Applicant marks tab (now Skills 15 / Knowledge 15)
        page.goto(f"{BASE}/web#id=42&model=hr.applicant&view_type=form")
        time.sleep(5)
        try:
            page.locator("a.nav-link:has-text('MCB Recruitment')").first.click(timeout=5000)
            time.sleep(2)
        except Exception as e:
            print("tab:", e)
        page.screenshot(path=str(ROOT/"02_recruitment/06_applicant_mcb_recruitment_tab.png"))
        print("saved applicant tab")

        # Compensatory leave type form (CE approval toggle)
        page.goto(f"{BASE}/web#id=81&model=hr.leave.type&view_type=form")
        time.sleep(5)
        page.screenshot(path=str(ROOT/"04_leave/05_compensatory_leave_type_ce.png"))
        print("saved compensatory leave type")

        b.close()
        print("DONE")


if __name__ == "__main__":
    main()
