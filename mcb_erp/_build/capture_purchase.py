"""Playwright screenshot tour of the MCB Purchase (Part B) module.
Run with the dev server already up on 127.0.0.1:8069.
Saves PNGs into _build/screenshots/purchase/<area>/NN_<slug>.png
"""
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

BASE = "http://127.0.0.1:8069"
ROOT = Path("/Data/odoo19_enterprise/custom-addons/mcb_erp/_build/screenshots/purchase")
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
    """The dev DB's trial-expiry nag renders as a full-page position:absolute
    overlay (z-index 1100) that intercepts all clicks. Strip it from THIS
    Playwright-rendered page only (no server/config change) so the underlying
    UI — which works fine — is clickable and screenshots stay clean."""
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


def switch_to_list_view(page):
    try:
        page.locator("button[data-tooltip='List']").first.click(timeout=2500)
        time.sleep(1.0)
        return True
    except Exception:
        return False


def open_row(page, text):
    try:
        page.locator(f"tr.o_data_row:has-text('{text}')").first.click(timeout=5000)
        time.sleep(2.0)
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

        # === 1. PURCHASE REQUEST (Step 1) ===
        area = "01_pr"
        goto(page, f"{BASE}/odoo/action-mcb_purchase.action_mcb_pr", wait=4)
        switch_to_list_view(page)
        shot(page, area, 1, "pr_list")
        goto(page, f"{BASE}/odoo/action-mcb_purchase.action_mcb_pr/1", wait=3)
        shot(page, area, 2, "pr1_form_rfp_method")
        if click_tab(page, "Note Sheet-1"):
            shot(page, area, 3, "pr1_note_sheet_1")
        goto(page, f"{BASE}/odoo/action-mcb_purchase.action_mcb_pr/4", wait=3)
        shot(page, area, 4, "pr4_form_ift_method_noal_required")
        goto(page, f"{BASE}/odoo/action-mcb_purchase.action_mcb_pr/5", wait=3)
        shot(page, area, 5, "pr5_form_direct_method_small_value")
        goto(page, f"{BASE}/report/html/mcb_purchase.action_report_mcb_pr_form/1", wait=3)
        shot(page, area, 6, "pr1_report_notesheets_preview")

        # === 2. OPENING SHEET (Step 4) ===
        area = "02_opening"
        goto(page, f"{BASE}/odoo/action-mcb_purchase.action_mcb_opening", wait=4)
        switch_to_list_view(page)
        shot(page, area, 1, "opening_sheet_list")
        goto(page, f"{BASE}/odoo/action-mcb_purchase.action_mcb_opening/1", wait=3)
        shot(page, area, 2, "opening_sheet_form")
        goto(page, f"{BASE}/report/html/mcb_purchase.action_report_mcb_opening_sheet/1", wait=3)
        shot(page, area, 3, "opening_sheet_report_preview")

        # === 3. TECHNICAL ANALYSIS (Step 5) ===
        area = "03_ta"
        goto(page, f"{BASE}/odoo/action-mcb_purchase.action_mcb_ta", wait=4)
        switch_to_list_view(page)
        shot(page, area, 1, "ta_list")
        goto(page, f"{BASE}/odoo/action-mcb_purchase.action_mcb_ta/2", wait=3)
        shot(page, area, 2, "ta2_form_ift_3vendors")
        goto(page, f"{BASE}/report/html/mcb_purchase.action_report_mcb_ta/2", wait=3)
        shot(page, area, 3, "ta2_report_preview")

        # === 4. COMPARATIVE STATEMENT (Step 6) ===
        area = "04_cs"
        goto(page, f"{BASE}/odoo/action-mcb_purchase.action_mcb_cs", wait=4)
        switch_to_list_view(page)
        shot(page, area, 1, "cs_list")
        goto(page, f"{BASE}/odoo/action-mcb_purchase.action_mcb_cs/1", wait=3)
        shot(page, area, 2, "cs1_form_gemini_lowest")
        goto(page, f"{BASE}/report/html/mcb_purchase.action_report_mcb_cs/1", wait=3)
        shot(page, area, 3, "cs1_report_preview")

        # === 5. VENDOR EVALUATION (Step 7) ===
        area = "05_eval"
        goto(page, f"{BASE}/odoo/action-mcb_purchase.action_mcb_eval", wait=4)
        switch_to_list_view(page)
        shot(page, area, 1, "evaluation_list")
        goto(page, f"{BASE}/odoo/action-mcb_purchase.action_mcb_eval/1", wait=3)
        shot(page, area, 2, "eval1_form_scores")
        goto(page, f"{BASE}/report/html/mcb_purchase.action_report_mcb_eval/1", wait=3)
        shot(page, area, 3, "eval1_report_preview")

        # === 6. NOAL (Step 9) ===
        area = "06_noal"
        goto(page, f"{BASE}/odoo/action-mcb_purchase.action_mcb_noal", wait=4)
        switch_to_list_view(page)
        shot(page, area, 1, "noal_list")
        goto(page, f"{BASE}/odoo/action-mcb_purchase.action_mcb_noal/1", wait=3)
        shot(page, area, 2, "noal1_form_acknowledged")
        goto(page, f"{BASE}/report/html/mcb_purchase.action_report_mcb_noal/1", wait=3)
        shot(page, area, 3, "noal1_letter_preview")

        # === 7. PURCHASE ORDER (confirmed) ===
        area = "07_po"
        goto(page, f"{BASE}/odoo/action-purchase.purchase_form_action", wait=4)
        switch_to_list_view(page)
        shot(page, area, 1, "po_list_all")
        goto(page, f"{BASE}/odoo/action-purchase.purchase_form_action/18", wait=3)
        shot(page, area, 2, "po18_gemini_confirmed_form")
        goto(page, f"{BASE}/report/html/purchase.action_report_purchase_order/18", wait=3)
        shot(page, area, 3, "po18_pdf_preview")

        # === 8. PROCUREMENT CHECKLIST (Annex-29) ===
        area = "08_checklist"
        goto(page, f"{BASE}/odoo/action-mcb_purchase.action_mcb_proc_checklist", wait=4)
        switch_to_list_view(page)
        shot(page, area, 1, "checklist_list")
        goto(page, f"{BASE}/odoo/action-mcb_purchase.action_mcb_proc_checklist/1", wait=3)
        shot(page, area, 2, "checklist1_form_all_yes")
        goto(page, f"{BASE}/report/html/mcb_purchase.action_report_mcb_proc_checklist/1", wait=3)
        shot(page, area, 3, "checklist1_report_preview")

        # === 9. MCB REPORTS (Step 11 — Table-14 suite) ===
        area = "09_reports"
        goto(page, f"{BASE}/odoo/action-mcb_purchase.action_mcb_pr_pending", wait=4)
        switch_to_list_view(page)
        shot(page, area, 1, "pr_pending_report")
        goto(page, f"{BASE}/odoo/action-mcb_purchase.action_mcb_pr_projectwise", wait=4)
        switch_to_list_view(page)
        shot(page, area, 2, "project_wise_report")
        goto(page, f"{BASE}/odoo/action-mcb_purchase.action_mcb_vendorwise", wait=4)
        switch_to_list_view(page)
        shot(page, area, 3, "vendor_wise_report")
        goto(page, f"{BASE}/odoo/action-mcb_purchase.action_mcb_wo_report", wait=4)
        switch_to_list_view(page)
        shot(page, area, 4, "work_order_wise_report")
        goto(page, f"{BASE}/odoo/action-mcb_purchase.action_mcb_pr_report_wizard", wait=4)
        shot(page, area, 5, "pr_process_report_wizard_form")

        browser.close()
        print("DONE")


if __name__ == "__main__":
    main()
