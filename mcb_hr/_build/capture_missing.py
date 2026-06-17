"""Capture the two screenshots that the main tour missed."""
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

        # --- MCB Permanent salary structure form ---
        page.goto(f"{BASE}/odoo/action-hr_payroll.action_view_hr_payroll_structure_list_form")
        time.sleep(5)
        # The list view is grouped — expand "MCB Permanent / Regular" group
        try:
            page.get_by_text("MCB Permanent / Regular").first.click(timeout=8000)
            time.sleep(2)
            # Now click the structure row inside
            page.locator("td.o_data_cell").first.click(timeout=8000)
            time.sleep(3)
            page.screenshot(path=str(ROOT/"03_payroll/02_salary_structure_mcb_permanent.png"))
            print("OK payroll structure")
        except Exception as e:
            print(f"WARN payroll: {e}")
            # As a fallback, just screenshot the structures list (it's still informative)
            try:
                page.goto(f"{BASE}/odoo/action-hr_payroll.action_view_hr_payroll_structure_list_form")
                time.sleep(4)
                page.get_by_text("MCB Permanent / Regular").first.click(timeout=6000)
                time.sleep(2)
                page.screenshot(path=str(ROOT/"03_payroll/02_salary_structure_mcb_permanent.png"))
                print("OK payroll structure (group expanded fallback)")
            except Exception as e2:
                print(f"FAILED payroll fallback: {e2}")

        # --- Applicant MCB Recruitment tab ---
        page.goto(f"{BASE}/odoo/recruitment")
        time.sleep(5)
        try:
            # Click on a kanban card (any applicant)
            cards = page.locator(".o_kanban_record")
            count = cards.count()
            print(f"  found {count} kanban cards")
            if count > 0:
                cards.first.click(timeout=8000)
                time.sleep(3)
                # Scroll the notebook into view
                try:
                    page.locator(".o_notebook").first.scroll_into_view_if_needed(timeout=3000)
                    time.sleep(1)
                except Exception:
                    pass
                # Click the tab
                tab_found = False
                for attempt in [
                    lambda: page.locator(".o_notebook_headers a:has-text('MCB Recruitment')").first.click(timeout=4000),
                    lambda: page.locator("a.nav-link:has-text('MCB Recruitment')").first.click(timeout=4000),
                    lambda: page.get_by_role("tab", name="MCB Recruitment").first.click(timeout=4000),
                ]:
                    try:
                        attempt()
                        tab_found = True
                        break
                    except Exception:
                        continue
                time.sleep(2)
                if tab_found:
                    page.screenshot(path=str(ROOT/"02_recruitment/06_applicant_mcb_recruitment_tab.png"))
                    print("OK applicant MCB tab")
                else:
                    page.screenshot(path=str(ROOT/"02_recruitment/06_applicant_mcb_recruitment_tab.png"))
                    print("Captured applicant form anyway (tab couldn't be clicked)")
        except Exception as e:
            print(f"WARN recruitment: {e}")

        browser.close()


if __name__ == "__main__":
    main()
