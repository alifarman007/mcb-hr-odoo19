"""Capture the applicant MCB Recruitment tab directly by URL."""
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


def main():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True, args=["--no-sandbox"])
        ctx = browser.new_context(viewport={"width": 1440, "height": 900})
        page = ctx.new_page()
        login(page)
        # Open applicant via web client URL (hash)
        page.goto(f"{BASE}/web#id=42&model=hr.applicant&view_type=form")
        time.sleep(5)
        try:
            page.locator("a.nav-link:has-text('MCB Recruitment')").first.click(timeout=5000)
            time.sleep(2)
        except Exception as e:
            print("tab click failed:", e)
            # Try by role
            try:
                page.get_by_role("tab", name="MCB Recruitment").first.click(timeout=4000)
                time.sleep(2)
            except Exception as e2:
                print("role click failed:", e2)
        page.screenshot(path=str(ROOT/"02_recruitment/06_applicant_mcb_recruitment_tab.png"))
        print("saved")
        browser.close()


if __name__ == "__main__":
    main()
