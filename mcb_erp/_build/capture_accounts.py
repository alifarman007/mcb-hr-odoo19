"""Playwright screenshot tour of the MCB Accounts/Finance (Part C) modules:
mcb_account + mcb_cash_advance + mcb_budget + mcb_asset.
Run with the dev server already up on 127.0.0.1:8069.
Saves PNGs into _build/screenshots/accounts/<area>/NN_<slug>.png
"""
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

BASE = "http://127.0.0.1:8069"
ROOT = Path("/Data/odoo19_enterprise/custom-addons/mcb_erp/_build/screenshots/accounts")
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

        # === 1. VOUCHERS (JV / 4-level approval) ===
        area = "01_vouchers"
        goto(page, f"{BASE}/odoo/action-account.action_move_journal_line", wait=4)
        switch_to_list_view(page)
        shot(page, area, 1, "journal_entries_list")
        goto(page, f"{BASE}/odoo/action-account.action_move_journal_line/66", wait=3)
        shot(page, area, 2, "jv66_form_reclass_posted")
        goto(page, f"{BASE}/report/html/mcb_account.action_report_mcb_voucher/66", wait=3)
        shot(page, area, 3, "jv66_voucher_report_preview")

        # === 2. MONEY RECEIPT / CHEQUE PAYMENT ===
        area = "02_payments"
        goto(page, f"{BASE}/odoo/action-account.action_account_payments", wait=4)
        switch_to_list_view(page)
        shot(page, area, 1, "payments_list")
        goto(page, f"{BASE}/odoo/action-account.action_account_payments/1", wait=3)
        shot(page, area, 2, "receipt1_care_donor_form")
        goto(page, f"{BASE}/report/html/mcb_account.action_report_mcb_money_receipt/1", wait=3)
        shot(page, area, 3, "receipt1_money_receipt_preview")
        goto(page, f"{BASE}/odoo/action-account.action_account_payments/3", wait=3)
        shot(page, area, 4, "cheque3_gemini_form")
        goto(page, f"{BASE}/odoo/action-mcb_account.action_mcb_cheque_register_wizard", wait=4)
        shot(page, area, 5, "cheque_register_wizard_form")
        goto(page, f"{BASE}/report/html/mcb_account.action_report_mcb_cheque_register/1", wait=3)
        shot(page, area, 6, "cheque_register_report_preview")

        # === 3. TAX CHALLAN / PAYMENT CHECKLIST ===
        area = "03_tax_checklist"
        goto(page, f"{BASE}/odoo/action-mcb_account.action_mcb_tax_challan", wait=4)
        switch_to_list_view(page)
        shot(page, area, 1, "tax_challan_list")
        goto(page, f"{BASE}/odoo/action-mcb_account.action_mcb_tax_challan/1", wait=3)
        shot(page, area, 2, "tax_challan1_form")
        goto(page, f"{BASE}/odoo/action-mcb_account.action_mcb_payment_checklist", wait=4)
        switch_to_list_view(page)
        shot(page, area, 3, "payment_checklist_list")
        goto(page, f"{BASE}/odoo/action-mcb_account.action_mcb_payment_checklist/1", wait=3)
        shot(page, area, 4, "payment_checklist1_form")
        goto(page, f"{BASE}/report/html/mcb_account.action_report_mcb_payment_checklist/1", wait=3)
        shot(page, area, 5, "payment_checklist1_report_preview")

        # === 4. BANK RECON / TOP SHEET / VAT-TDS / DONOR ANALYTIC ===
        area = "04_registers"
        goto(page, f"{BASE}/odoo/action-mcb_account.action_mcb_bank_recon_wizard", wait=4)
        shot(page, area, 1, "bank_recon_wizard_form")
        goto(page, f"{BASE}/report/html/mcb_account.action_report_mcb_bank_recon/1", wait=3)
        shot(page, area, 2, "bank_recon_report_preview")
        goto(page, f"{BASE}/odoo/action-mcb_account.action_mcb_top_sheet_wizard", wait=4)
        shot(page, area, 3, "top_sheet_wizard_form")
        goto(page, f"{BASE}/report/html/mcb_account.action_report_mcb_top_sheet/1", wait=3)
        shot(page, area, 4, "top_sheet_report_preview")
        goto(page, f"{BASE}/odoo/action-mcb_account.action_mcb_vat_tds_wizard", wait=4)
        shot(page, area, 5, "vat_tds_wizard_form")
        goto(page, f"{BASE}/report/html/mcb_account.action_report_mcb_vat_tds/1", wait=3)
        shot(page, area, 6, "vat_tds_report_preview")
        goto(page, f"{BASE}/odoo/action-mcb_account.action_mcb_analytic_report_wizard", wait=4)
        shot(page, area, 7, "donor_analytic_wizard_form")
        goto(page, f"{BASE}/report/html/mcb_account.action_report_mcb_analytic/1", wait=3)
        shot(page, area, 8, "donor_analytic_report_preview")
        goto(page, f"{BASE}/odoo/action-mcb_account.action_mcb_year_end_wizard", wait=4)
        shot(page, area, 9, "year_end_closing_wizard_form")

        # === 5. CASH ADVANCE (Annex-18) ===
        area = "05_advance"
        goto(page, f"{BASE}/odoo/action-mcb_cash_advance.action_mcb_advance", wait=4)
        switch_to_list_view(page)
        shot(page, area, 1, "advance_list")
        goto(page, f"{BASE}/odoo/action-mcb_cash_advance.action_mcb_advance/5", wait=3)
        shot(page, area, 2, "advance5_form_paid")
        goto(page, f"{BASE}/report/html/mcb_cash_advance.action_report_mcb_advance/5", wait=3)
        shot(page, area, 3, "advance5_report_preview")

        # === 6. ADVANCE ADJUSTMENT (Annex-19) ===
        area = "06_adv_adjust"
        goto(page, f"{BASE}/odoo/action-mcb_cash_advance.action_mcb_adv_adjustment", wait=4)
        switch_to_list_view(page)
        shot(page, area, 1, "adjustment_list")
        goto(page, f"{BASE}/odoo/action-mcb_cash_advance.action_mcb_adv_adjustment/3", wait=3)
        shot(page, area, 2, "adjustment3_form")
        goto(page, f"{BASE}/report/html/mcb_cash_advance.action_report_mcb_adv_adjust/3", wait=3)
        shot(page, area, 3, "adjustment3_report_preview")

        # === 7. IOU (Annex-13) ===
        area = "07_iou"
        goto(page, f"{BASE}/odoo/action-mcb_cash_advance.action_mcb_iou", wait=4)
        switch_to_list_view(page)
        shot(page, area, 1, "iou_list")
        goto(page, f"{BASE}/odoo/action-mcb_cash_advance.action_mcb_iou/1", wait=3)
        shot(page, area, 2, "iou1_form_adjusted")
        goto(page, f"{BASE}/report/html/mcb_cash_advance.action_report_mcb_iou/1", wait=3)
        shot(page, area, 3, "iou1_report_preview")

        # === 8. PETTY CASH (count / top-up / book) ===
        area = "08_petty_cash"
        goto(page, f"{BASE}/odoo/action-mcb_cash_advance.action_mcb_cash_count", wait=4)
        switch_to_list_view(page)
        shot(page, area, 1, "cash_count_list")
        goto(page, f"{BASE}/odoo/action-mcb_cash_advance.action_mcb_cash_count/1", wait=3)
        shot(page, area, 2, "cash_count1_form")
        goto(page, f"{BASE}/report/html/mcb_cash_advance.action_report_mcb_cash_count/1", wait=3)
        shot(page, area, 3, "cash_count1_report_preview")
        goto(page, f"{BASE}/odoo/action-mcb_cash_advance.action_mcb_petty_topup", wait=4)
        switch_to_list_view(page)
        shot(page, area, 4, "petty_topup_list")
        goto(page, f"{BASE}/odoo/action-mcb_cash_advance.action_mcb_petty_topup/1", wait=3)
        shot(page, area, 5, "petty_topup1_form_done")
        goto(page, f"{BASE}/odoo/action-mcb_cash_advance.action_mcb_petty_book_wizard", wait=4)
        shot(page, area, 6, "petty_book_wizard_form")
        goto(page, f"{BASE}/report/html/mcb_cash_advance.action_report_mcb_petty_book/1", wait=3)
        shot(page, area, 7, "petty_book_report_preview")
        goto(page, f"{BASE}/report/html/mcb_cash_advance.action_report_mcb_petty_statement/1", wait=3)
        shot(page, area, 8, "petty_statement_report_preview")

        # === 9. WORKING BUDGET / REVISION / DONOR REPORT ===
        area = "09_budget"
        goto(page, f"{BASE}/odoo/action-mcb_budget.action_mcb_working_budget", wait=4)
        switch_to_list_view(page)
        shot(page, area, 1, "working_budget_list")
        goto(page, f"{BASE}/odoo/action-mcb_budget.action_mcb_working_budget/1", wait=3)
        shot(page, area, 2, "working_budget1_form_approved")
        goto(page, f"{BASE}/report/html/mcb_budget.action_report_mcb_working_budget/1", wait=3)
        shot(page, area, 3, "working_budget1_report_preview")
        goto(page, f"{BASE}/odoo/action-mcb_budget.action_mcb_budget_revision", wait=4)
        switch_to_list_view(page)
        shot(page, area, 4, "budget_revision_list")
        goto(page, f"{BASE}/odoo/action-mcb_budget.action_mcb_budget_revision/1", wait=3)
        shot(page, area, 5, "budget_revision1_form_ce_approved")
        goto(page, f"{BASE}/odoo/action-mcb_budget.action_mcb_donor_report_wizard", wait=4)
        shot(page, area, 6, "donor_report_wizard_form")
        goto(page, f"{BASE}/report/html/mcb_budget.action_report_mcb_donor_budget/1", wait=3)
        shot(page, area, 7, "donor_budget_report_preview")
        goto(page, f"{BASE}/report/html/mcb_budget.action_report_mcb_variance/1", wait=3)
        shot(page, area, 8, "variance_statement_preview")

        # === 10. FIXED ASSETS ===
        area = "10_asset"
        goto(page, f"{BASE}/odoo/action-account_asset.action_account_asset_form", wait=4)
        switch_to_list_view(page)
        shot(page, area, 1, "asset_list")
        goto(page, f"{BASE}/odoo/action-account_asset.action_account_asset_form/2", wait=3)
        shot(page, area, 2, "asset2_generator_form")
        if click_tab(page, "Depreciation"):
            shot(page, area, 3, "asset2_depreciation_board")
        goto(page, f"{BASE}/odoo/action-mcb_asset.action_mcb_asset_register_wizard", wait=4)
        shot(page, area, 4, "asset_register_wizard_form")
        goto(page, f"{BASE}/report/html/mcb_asset.action_report_mcb_asset_register/1", wait=3)
        shot(page, area, 5, "asset_register_report_preview")
        goto(page, f"{BASE}/odoo/action-mcb_asset.action_mcb_asset_inventory", wait=4)
        switch_to_list_view(page)
        shot(page, area, 6, "asset_inventory_list")
        goto(page, f"{BASE}/odoo/action-mcb_asset.action_mcb_asset_inventory/1", wait=3)
        shot(page, area, 7, "asset_inventory1_form_verified")
        goto(page, f"{BASE}/report/html/mcb_asset.action_report_mcb_asset_inventory/1", wait=3)
        shot(page, area, 8, "asset_inventory1_report_preview")
        goto(page, f"{BASE}/report/html/mcb_asset.action_report_mcb_asset_label/2", wait=3)
        shot(page, area, 9, "asset2_barcode_label_preview")

        browser.close()
        print("DONE")


if __name__ == "__main__":
    main()
