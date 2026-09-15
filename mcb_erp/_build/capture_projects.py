"""Playwright screenshot tour of the MCB Projects (Part D) modules:
mcb_project + mcb_volunteer + mcb_vehicle + mcb_store.
Run with the dev server already up on 127.0.0.1:8069.
Saves PNGs into _build/screenshots/projects/<area>/NN_<slug>.png
"""
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

BASE = "http://127.0.0.1:8069"
ROOT = Path("/Data/odoo19_enterprise/custom-addons/mcb_erp/_build/screenshots/projects")
ROOT.mkdir(parents=True, exist_ok=True)


def login(page):
    page.goto(f"{BASE}/web/login?db=mcb_demo", wait_until="domcontentloaded")
    page.fill("input[name='login']", "admin")
    page.fill("input[name='password']", "admin")
    page.click("button[type='submit']")
    try:
        page.wait_for_url(lambda url: "/web/login" not in url, timeout=30000)
    except Exception:
        pass
    time.sleep(3)


def dismiss_expiry_banner(page):
    try:
        page.evaluate(
            "document.querySelectorAll('.database_expiration_panel')"
            ".forEach(e => { const o = e.closest('div[style*=\"position: absolute\"]') || e; o.remove(); })"
        )
    except Exception:
        pass


def shot(page, area, n, slug):
    area_dir = ROOT / area
    area_dir.mkdir(parents=True, exist_ok=True)
    out = area_dir / f"{n:02d}_{slug}.png"
    dismiss_expiry_banner(page)
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
    dismiss_expiry_banner(page)


def switch_to_list_view(page):
    try:
        page.locator("button[data-tooltip='List']").first.click(timeout=2500)
        time.sleep(1.0)
        return True
    except Exception:
        return False


def click_tab(page, label):
    try:
        page.get_by_role("tab", name=label, exact=True).first.click(timeout=4000)
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

        # === 1. PROJECT PROFILE (MCB tab) ===
        area = "01_project_profile"
        goto(page, f"{BASE}/odoo/action-project.open_view_project_all", wait=4)
        switch_to_list_view(page)
        shot(page, area, 1, "project_list")
        goto(page, f"{BASE}/odoo/action-project.open_view_project_all/10", wait=3)
        shot(page, area, 2, "gbvie_project_form")
        if click_tab(page, "Settings"):
            shot(page, area, 3, "gbvie_project_settings_tab")

        # === 2. STAFF ASSIGNMENTS (% TIME) ===
        area = "02_assignments"
        goto(page, f"{BASE}/odoo/action-mcb_project.action_mcb_assignment", wait=4)
        switch_to_list_view(page)
        shot(page, area, 1, "assignment_list_pct_time")

        # === 3. BENEFICIARY DATA / MEAL ===
        area = "03_beneficiary_meal"
        goto(page, f"{BASE}/odoo/action-mcb_project.action_mcb_beneficiary", wait=4)
        switch_to_list_view(page)
        shot(page, area, 1, "beneficiary_list")
        goto(page, f"{BASE}/odoo/action-mcb_project.action_mcb_beneficiary/1", wait=3)
        shot(page, area, 2, "beneficiary1_form")
        goto(page, f"{BASE}/odoo/action-mcb_project.action_mcb_meal", wait=4)
        switch_to_list_view(page)
        shot(page, area, 3, "meal_indicator_list")

        # === 4. TRAVEL AUTHORIZATION (Annex-30) ===
        area = "04_travel_auth"
        goto(page, f"{BASE}/odoo/action-mcb_project.action_mcb_travel_auth", wait=4)
        switch_to_list_view(page)
        shot(page, area, 1, "travel_auth_list")
        goto(page, f"{BASE}/odoo/action-mcb_project.action_mcb_travel_auth/1", wait=3)
        shot(page, area, 2, "travel_auth1_form_approved")
        goto(page, f"{BASE}/report/html/mcb_project.action_report_mcb_travel_auth/1", wait=3)
        shot(page, area, 3, "travel_auth1_report_preview")

        # === 5. QUARTERLY / TIMESHEET / ATTENDANCE REPORTS ===
        area = "05_reports"
        goto(page, f"{BASE}/odoo/action-mcb_project.action_mcb_qtr_wizard", wait=4)
        shot(page, area, 1, "quarterly_report_wizard_form")
        goto(page, f"{BASE}/report/html/mcb_project.action_report_mcb_quarterly/1", wait=3)
        shot(page, area, 2, "quarterly_report_preview")
        goto(page, f"{BASE}/odoo/action-mcb_project.action_mcb_ts_wizard", wait=4)
        shot(page, area, 3, "timesheet_report_wizard_form")
        goto(page, f"{BASE}/report/html/mcb_project.action_report_mcb_timesheet/1", wait=3)
        shot(page, area, 4, "timesheet_report_preview")
        goto(page, f"{BASE}/odoo/action-mcb_project.action_mcb_att_wizard", wait=4)
        shot(page, area, 5, "attendance_report_wizard_form")
        goto(page, f"{BASE}/report/html/mcb_project.action_report_mcb_attendance/1", wait=3)
        shot(page, area, 6, "attendance_report_preview")
        goto(page, f"{BASE}/odoo/action-mcb_project.action_mcb_att_import_wizard", wait=4)
        shot(page, area, 7, "camp_attendance_import_wizard_form")

        # === 6. PAYROLL COST ALLOCATION (TMS-004) ===
        area = "06_payroll_allocation"
        goto(page, f"{BASE}/odoo/action-mcb_project.action_mcb_alloc_wizard", wait=4)
        shot(page, area, 1, "payroll_allocation_wizard_form")
        goto(page, f"{BASE}/odoo/action-account.action_move_journal_line/94", wait=3)
        shot(page, area, 2, "payroll_allocation_je_posted")

        # === 7. VOLUNTEER DATABASE ===
        area = "07_volunteer"
        goto(page, f"{BASE}/odoo/action-mcb_volunteer.action_mcb_volunteer", wait=4)
        switch_to_list_view(page)
        shot(page, area, 1, "volunteer_list")
        goto(page, f"{BASE}/odoo/action-mcb_volunteer.action_mcb_volunteer/1", wait=3)
        shot(page, area, 2, "volunteer1_form")
        goto(page, f"{BASE}/odoo/action-mcb_volunteer.action_mcb_vol_att", wait=4)
        switch_to_list_view(page)
        shot(page, area, 3, "volunteer_attendance_list")

        # === 8. VOLUNTEER INCENTIVE BATCH ===
        area = "08_incentive"
        goto(page, f"{BASE}/odoo/action-mcb_volunteer.action_mcb_vib", wait=4)
        switch_to_list_view(page)
        shot(page, area, 1, "incentive_batch_list")
        goto(page, f"{BASE}/odoo/action-mcb_volunteer.action_mcb_vib/2", wait=3)
        shot(page, area, 2, "incentive_batch2_form_paid")
        goto(page, f"{BASE}/report/html/mcb_volunteer.action_report_mcb_incentive_sheet/2", wait=3)
        shot(page, area, 3, "incentive_signature_sheet_preview")

        # === 9. VEHICLE LOG BOOK / MOVEMENT REGISTER ===
        area = "09_vehicle"
        goto(page, f"{BASE}/odoo/action-fleet.fleet_vehicle_action", wait=4)
        switch_to_list_view(page)
        shot(page, area, 1, "vehicle_list")
        goto(page, f"{BASE}/odoo/action-fleet.fleet_vehicle_action/5", wait=3)
        shot(page, area, 2, "vehicle5_corolla_form_gbvie")
        goto(page, f"{BASE}/odoo/action-mcb_vehicle.action_mcb_vehicle_log", wait=4)
        switch_to_list_view(page)
        shot(page, area, 3, "vehicle_log_list")
        goto(page, f"{BASE}/odoo/action-mcb_vehicle.action_mcb_movement", wait=4)
        switch_to_list_view(page)
        shot(page, area, 4, "movement_register_list")
        goto(page, f"{BASE}/odoo/action-mcb_vehicle.action_mcb_movement/1", wait=3)
        shot(page, area, 5, "movement1_form_linked_travel_auth")
        goto(page, f"{BASE}/report/html/mcb_vehicle.action_report_mcb_movement/1", wait=3)
        shot(page, area, 6, "movement1_report_preview")
        goto(page, f"{BASE}/odoo/action-mcb_vehicle.action_mcb_logbook_wizard", wait=4)
        shot(page, area, 7, "logbook_wizard_form")
        goto(page, f"{BASE}/report/html/mcb_vehicle.action_report_mcb_logbook/1", wait=3)
        shot(page, area, 8, "logbook_monthly_report_preview")

        # === 10. STORE — SRF / MUSTER ROLL / STORE REGISTER ===
        area = "10_store"
        goto(page, f"{BASE}/odoo/action-mcb_store.action_mcb_srf", wait=4)
        switch_to_list_view(page)
        shot(page, area, 1, "srf_list")
        goto(page, f"{BASE}/odoo/action-mcb_store.action_mcb_srf/1", wait=3)
        shot(page, area, 2, "srf1_form_issued")
        goto(page, f"{BASE}/odoo/action-mcb_store.action_mcb_muster", wait=4)
        switch_to_list_view(page)
        shot(page, area, 3, "muster_roll_list")
        goto(page, f"{BASE}/odoo/action-mcb_store.action_mcb_muster/1", wait=3)
        shot(page, area, 4, "muster_roll1_form_distributed")
        goto(page, f"{BASE}/report/html/mcb_store.action_report_mcb_muster_roll/1", wait=3)
        shot(page, area, 5, "muster_roll1_report_preview")
        goto(page, f"{BASE}/odoo/action-mcb_store.action_mcb_store_register_wizard", wait=4)
        shot(page, area, 6, "store_register_wizard_form")
        goto(page, f"{BASE}/report/html/mcb_store.action_report_mcb_store_register/1", wait=3)
        shot(page, area, 7, "store_register_report_preview")
        goto(page, f"{BASE}/report/html/mcb_store.action_report_mcb_monthly_stock/1", wait=3)
        shot(page, area, 8, "monthly_stock_report_preview")

        browser.close()
        print("DONE")


if __name__ == "__main__":
    main()
