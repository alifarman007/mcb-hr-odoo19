"""Accounts (SRS Part C) click-path flows — 16 tutorials.

Navigation is by URL and the click target is marked, but destructive clicks are
suppressed (click=False) so the demo records keep the state the guide describes
and the capture can be re-run any number of times.

All flows run as `admin`. In live these steps are done by different people
(Accounts Officer prepares, Finance Manager checks/reviews, CE approves) — the
role badge on each screen shows who should do it in real life.
"""
import sys
sys.path.insert(0, "/Data/odoo19_enterprise/custom-addons/mcb_hr/_build")
from flow_recorder import run_flow  # noqa: E402

# ---- record ids in the training database -------------------------------
JV = 66             # journal voucher, posted, 4-level approved
DRAFT_JV = 103      # draft voucher - still shows Check/Review/Approve buttons
RECEIPT = 1         # inbound payment - CARE 500,000
CHEQUE = 3          # outbound cheque - Gemini 90,000
BILL = 102          # vendor bill from PO P00018, 3-way match = yes
CHECKLIST = 1       # payment checklist (Annex-28)
CHALLAN = 1         # treasury TDS challan
ADVANCE = 5
ADJUSTMENT = 3
IOU = 1
CASHCOUNT = 1
TOPUP = 1
WORKBUDGET = 1
REVISION = 1
BUDGET = 3          # budget.analytic - GBViE FY25-26
ASSET_GEN = 2       # generator
ASSET_OLD = 4       # photocopier, flagged for disposal
ASSET_INV = 1

# ---- actions -----------------------------------------------------------
A_ACC = "account.action_account_form"
A_JRN = "account.action_account_journal_form"
A_TAX = "account.action_tax_form"
A_PARTNER = "account.res_partner_action_supplier"
A_MOVE = "account.action_move_journal_line"
A_PAY = "account.action_account_payments"
A_PAYOUT = "account.action_account_payments_payable"
A_BILL = "account.action_move_in_invoice_type"
A_CHALLAN = "mcb_account.action_mcb_tax_challan"
A_CHECKLIST = "mcb_account.action_mcb_payment_checklist"
A_BANKREC = "mcb_account.action_mcb_bank_recon_wizard"
A_CHEQREG = "mcb_account.action_mcb_cheque_register_wizard"
A_VATTDS = "mcb_account.action_mcb_vat_tds_wizard"
A_TOPSHEET = "mcb_account.action_mcb_top_sheet_wizard"
A_ANALYTIC = "mcb_account.action_mcb_analytic_report_wizard"
A_YEAREND = "mcb_account.action_mcb_year_end_wizard"
A_ADV = "mcb_cash_advance.action_mcb_advance"
A_ADJ = "mcb_cash_advance.action_mcb_adv_adjustment"
A_IOU = "mcb_cash_advance.action_mcb_iou"
A_COUNT = "mcb_cash_advance.action_mcb_cash_count"
A_TOPUP = "mcb_cash_advance.action_mcb_petty_topup"
A_PETTYBOOK = "mcb_cash_advance.action_mcb_petty_book_wizard"
A_WB = "mcb_budget.action_mcb_working_budget"
A_REV = "mcb_budget.action_mcb_budget_revision"
A_DONOR = "mcb_budget.action_mcb_donor_report_wizard"
A_BUDGETS = "account_budget.act_budget_analytic_view"
A_ASSET = "account_asset.action_account_asset_form"
A_ASSETINV = "mcb_asset.action_mcb_asset_inventory"
A_ASSETREG = "mcb_asset.action_mcb_asset_register_wizard"
R_BS = "account_reports.action_account_report_bs"
R_PL = "account_reports.action_account_report_pl"
R_TB = "account_reports.action_account_report_coa"
R_GL = "account_reports.action_account_report_general_ledger"
R_AR = "account_reports.action_account_report_ar"
R_AP = "account_reports.action_account_report_ap"

ACCOUNTING = "/odoo/accounting"


def S(slug, headline, instruction, target, role, goto=None, wait=3.2, note=""):
    d = dict(slug=slug, headline=headline, instruction=instruction, target=target,
             role=role, wait=wait, click=False)
    if goto:
        d["goto"] = goto
    if note:
        d["note"] = note
    return d


def L(slug, headline, instruction, target, role, goto=ACCOUNTING, wait=3.4, note=""):
    """First step of a flow — shows the login screen, then lands here."""
    d = dict(slug=slug, goto=goto, wait=wait, login=("admin", "admin"), role=role,
             headline=headline, instruction=instruction, target=target, click=False)
    if note:
        d["note"] = note
    return d


NEW = ["button.o_list_button_add", "button:has-text('New')"]

# ==================================================== 1. CHART OF ACCOUNTS ==
F1 = [
    L("open_accounting", "Open the Accounting app",
      "Everything in these tutorials starts from the Accounting app.",
      ["a.o_app[href='/odoo/accounting']", "text=Accounting"], "ADMINISTRATOR", goto="/odoo"),
    S("coa_list", "Configuration → Chart of Accounts",
      "Every account MCB uses to record money. The code decides where it sits in the reports.",
      ["tr.o_data_row", ".o_data_row"], "ADMINISTRATOR", goto=f"/odoo/action-{A_ACC}", wait=4.0,
      note="1xxxxx assets · 2xxxxx liabilities · 3xxxxx equity · 4/5xxxxx income · 6xxxxx expense"),
    S("coa_search_mcb", "Find MCB's own accounts",
      "Type a code in the search box — 102910 Employee Advances, 200910 TDS Payable, 300190 Fund Balance.",
      ["input.o_searchview_input", ".o_searchview"], "ADMINISTRATOR", wait=2.6),
    S("coa_new", "Add a new account",
      "Click New, then give it a code, a name and an account type.",
      NEW, "ADMINISTRATOR", wait=2.6,
      note="The Type is what puts the account on the Balance Sheet or the P&L — get it right."),
]

# ========================================================= 2. JOURNALS =====
F2 = [
    L("journals_list", "Configuration → Journals",
      "A journal is a book of entries: Bank, Cash, Purchases, Sales, Miscellaneous.",
      ["tr.o_data_row", ".o_data_row"], "ADMINISTRATOR", goto=f"/odoo/action-{A_JRN}", wait=4.0),
    S("journal_bank", "Open the Bank journal",
      "Each journal has its own account, its own short code and its own numbering.",
      ["div[name='name']", "h1"], "ADMINISTRATOR", goto=f"/odoo/action-{A_JRN}/6", wait=3.4),
    S("journal_voucher_numbering", "MCB voucher numbering",
      "Voucher numbers restart every fiscal year — JV-2627-001, BNK-2627-001, and so on.",
      ["div[name='code']", "[name='code']"], "ADMINISTRATOR", wait=2.6,
      note="Numbering follows MCB's July–June year, not the calendar year."),
    S("journal_petty", "The Petty Cash journal",
      "Cash journals work the same way — this one holds the office petty cash.",
      ["div[name='name']", "h1"], "ADMINISTRATOR", goto=f"/odoo/action-{A_JRN}/22", wait=3.2),
]

# ================================================= 3. FISCAL YEAR & TAX ====
F3 = [
    L("settings_open", "Configuration → Settings → Accounting",
      "This is where the fiscal year and the tax defaults live.",
      ["text=Fiscal", "input#fiscalyear_last_day", ".o_setting_box"], "ADMINISTRATOR",
      goto="/odoo/action-account.action_account_config", wait=5.0,
      note="MCB's financial year runs 1 July to 30 June — set it once, everything follows."),
    S("taxes_list", "Configuration → Taxes",
      "VAT and TDS rates. The TDS ones are the withholding taxes MCB deducts when paying.",
      ["tr.o_data_row", ".o_data_row"], "ADMINISTRATOR", goto=f"/odoo/action-{A_TAX}", wait=4.0),
    S("tax_tds_search", "Find the TDS rates",
      "Search TDS — MCB has 2%, 3%, 5%, 7.5% and 10% set up.",
      ["input.o_searchview_input", ".o_searchview"], "ADMINISTRATOR", wait=2.6),
    S("tax_withholding", "Deducted at payment, not at billing",
      "These are marked as withholding-on-payment, so the deduction happens when you pay.",
      ["tr.o_data_row", ".o_data_row"], "ADMINISTRATOR", wait=2.6,
      note="That is the Bangladesh rule — TDS is withheld at the moment of payment."),
]

# ======================================================== 4. PARTNERS =====
F4 = [
    L("vendors_list", "Vendors and donors",
      "Everyone MCB pays or receives money from lives here.",
      ["tr.o_data_row", ".o_data_row", ".o_kanban_record"], "ACCOUNTS OFFICER",
      goto=f"/odoo/action-{A_PARTNER}", wait=4.0),
    S("vendor_open", "Open a vendor",
      "Gemini Furniture — one of the vendors used through these tutorials.",
      ["div[name='name']", "h1"], "ACCOUNTS OFFICER",
      goto=f"/odoo/action-{A_PARTNER}/10", wait=3.4),
    S("vendor_bin_tin", "BIN and TIN",
      "Bangladesh tax registration numbers. They are needed on the VAT and TDS returns.",
      ["div[name='mcb_bin_no']", "[name='mcb_bin_no']", "div[name='mcb_tin_no']"],
      "ACCOUNTS OFFICER", wait=2.8,
      note="No BIN/TIN on the vendor means an incomplete challan later — fill them in now."),
]

# ================================================ 5. JOURNAL VOUCHER ======
F5 = [
    L("moves_list", "Accounting → Journal Entries",
      "Every voucher MCB records — journal, receipt and payment vouchers.",
      ["tr.o_data_row", ".o_data_row"], "ACCOUNTS OFFICER",
      goto=f"/odoo/action-{A_MOVE}", wait=4.2),
    S("jv_new", "Click New to write a voucher",
      "You choose the journal, the date, a reference, then the debit and credit lines.",
      NEW, "ACCOUNTS OFFICER", wait=2.6),
    S("jv_open", "A voucher being written",
      "Fuel and transport for Camp 12. Debit the expense, credit the payable — they must agree.",
      ["div[name='ref']", "h1", "div[name='line_ids']"], "ACCOUNTS OFFICER",
      goto=f"/odoo/action-{A_MOVE}/{DRAFT_JV}", wait=3.6),
    S("jv_analytic", "Code every line to a project",
      "The analytic column carries the project and donor — this is what makes donor reports work.",
      ["div[name='line_ids']", ".o_field_x2many"], "ACCOUNTS OFFICER", wait=2.8,
      note="A line with no analytic code will not appear in any donor report."),
    S("jv_approval", "The 4-level approval",
      "Prepared → Checked → Reviewed → Approved. Four different people in real life.",
      [".o_statusbar_buttons button[name='action_mcb_check']",
       ".o_statusbar_buttons button:has-text('Check')",
       ".o_form_statusbar button:has-text('Check')"], "FINANCE MANAGER", wait=2.8,
      note="A manual voucher cannot be posted until all four stamps are on it."),
    S("jv_posted", "Posted",
      "Once all four have signed and it is posted, it is in the ledger for good.",
      [".o_statusbar_status", "button:has-text('Posted')"], "FINANCE MANAGER",
      goto=f"/odoo/action-{A_MOVE}/{JV}", wait=3.4),
    S("jv_print", "Print the voucher",
      "Print gives the MCB voucher on letterhead, with the amount in words.",
      ["button:has-text('Print')", ".o_cp_action_menus button"], "ACCOUNTS OFFICER", wait=2.6),
]

# ================================================= 6. RECEIPT VOUCHER =====
F6 = [
    L("payments_list", "Accounting → Payments",
      "Money coming in from donors, and money going out to vendors.",
      ["tr.o_data_row", ".o_data_row"], "ACCOUNTS OFFICER",
      goto=f"/odoo/action-{A_PAY}", wait=4.2),
    S("receipt_new", "Click New to record money received",
      "Choose Receive, the donor, the bank journal and the amount.",
      NEW, "ACCOUNTS OFFICER", wait=2.6),
    S("receipt_open", "A donor receipt",
      "CARE Bangladesh, tranche 3 — 500,000 into the bank account.",
      ["div[name='partner_id']", "h1", "div[name='amount']"], "ACCOUNTS OFFICER",
      goto=f"/odoo/action-{A_PAY}/{RECEIPT}", wait=3.6),
    S("receipt_amount", "Amount and journal",
      "The bank journal decides which account is debited. The amount is shown in words on the receipt.",
      ["div[name='amount']", "div[name='journal_id']"], "ACCOUNTS OFFICER", wait=2.6),
    S("receipt_print", "Print the Money Receipt",
      "Print → Money Receipt gives the Annexure-01/31 form to hand to the donor.",
      ["button:has-text('Print')", ".o_cp_action_menus button"], "ACCOUNTS OFFICER", wait=2.8,
      note="Every rupee received should leave the office with a numbered money receipt."),
]

# ================================================= 7. PAYMENT VOUCHER ====
F7 = [
    L("payments_out", "Accounting → Payments (money out)",
      "Paying a vendor. In MCB this is nearly always by cheque.",
      ["tr.o_data_row", ".o_data_row"], "ACCOUNTS OFFICER",
      goto=f"/odoo/action-{A_PAYOUT}", wait=4.2),
    S("cheque_open", "A cheque payment",
      "90,000 to Gemini Furniture against their invoice.",
      ["div[name='partner_id']", "h1"], "ACCOUNTS OFFICER",
      goto=f"/odoo/action-{A_PAY}/{CHEQUE}", wait=3.6),
    S("cheque_number", "The cheque number is recorded",
      "Choose Checks as the method and type the cheque number — it feeds the cheque register.",
      ["div[name='check_number']", "[name='check_number']", "div[name='payment_method_line_id']"],
      "ACCOUNTS OFFICER", wait=2.8),
    S("checklist_list", "Payment Checklist (Annexure-28)",
      "Before a payment file is closed, the standard checklist is signed off.",
      ["tr.o_data_row", ".o_data_row"], "FINANCE MANAGER",
      goto=f"/odoo/action-{A_CHECKLIST}", wait=3.6),
    S("checklist_open", "Tick each item",
      "Bill attached, budget available, TDS deducted, approvals in place — then mark it done.",
      ["div[name='line_ids']", ".o_field_x2many"], "FINANCE MANAGER",
      goto=f"/odoo/action-{A_CHECKLIST}/{CHECKLIST}", wait=3.4),
    S("checklist_print", "Print the checklist",
      "The printed checklist goes into the voucher file as evidence.",
      ["button:has-text('Print')", ".o_cp_action_menus button"], "FINANCE MANAGER", wait=2.6),
]

# ================================================ 8. VENDOR BILL / 3-WAY ==
F8 = [
    L("bills_list", "Accounting → Vendor Bills",
      "A bill is what the vendor sends you. It is not the same as paying them.",
      ["tr.o_data_row", ".o_data_row"], "ACCOUNTS OFFICER",
      goto=f"/odoo/action-{A_BILL}", wait=4.2),
    S("bill_open", "A bill raised from a Purchase Order",
      "300,000 from Gemini Furniture, created straight from PO P00018 — nothing re-typed.",
      ["div[name='partner_id']", "h1"], "ACCOUNTS OFFICER",
      goto=f"/odoo/action-{A_BILL}/{BILL}", wait=3.6),
    S("bill_3way", "The 3-way match",
      "Purchase Order + Goods Received + Bill must agree. Here it says Yes — safe to pay.",
      ["div[name='invoice_origin']", "[name='invoice_origin']",
       "div[name='release_to_pay']", "div[name='partner_id']"],
      "FINANCE MANAGER", wait=3.0,
      note="If this does not say Yes, MCB's rule blocks the payment — goods may not have arrived."),
    S("bill_lines", "Check the lines and the analytic code",
      "Quantity and price should match the order. Each line carries its project and donor.",
      ["div[name='invoice_line_ids']", ".o_field_x2many"], "ACCOUNTS OFFICER", wait=2.8),
    S("bill_register_payment", "Register the payment",
      "Click Register Payment. TDS is deducted at this moment, not when the bill was entered.",
      ["button[name='action_register_payment']", "button:has-text('Register Payment')",
       ".o_statusbar_buttons button"], "FINANCE MANAGER", wait=2.8),
]

# ======================================================= 9. VAT / TDS =====
F9 = [
    L("challan_list", "MCB Registers → VAT / TDS Challans",
      "Every deduction MCB makes has to be deposited and recorded against a challan.",
      ["tr.o_data_row", ".o_data_row"], "ACCOUNTS OFFICER",
      goto=f"/odoo/action-{A_CHALLAN}", wait=4.0),
    S("challan_open", "A treasury challan",
      "Challan number, bank, branch, date and amount — TR-2026-000123, Sonali Bank.",
      ["div[name='challan_no']", "h1"], "ACCOUNTS OFFICER",
      goto=f"/odoo/action-{A_CHALLAN}/{CHALLAN}", wait=3.4),
    S("challan_state", "Mark it deposited",
      "Until the challan is deposited, the deduction is still a liability MCB owes.",
      [".o_statusbar_status", "button:has-text('Deposited')"], "ACCOUNTS OFFICER", wait=2.6),
    S("vattds_wizard", "Monthly VAT / TDS summary",
      "Pick the month and print. It shows Deductible, Deducted, Deposited and Dues.",
      ["div[name='date_from']", "button:has-text('Print')", ".modal"], "FINANCE MANAGER",
      goto=f"/odoo/action-{A_VATTDS}", wait=3.6,
      note="Dues is the number that matters — anything still owed to the treasury."),
    S("topsheet_wizard", "Expenses Top Sheet (Annexure-24)",
      "The same idea for expenses — a monthly summary built from the posted bills.",
      ["div[name='date_from']", "button:has-text('Print')", ".modal"], "FINANCE MANAGER",
      goto=f"/odoo/action-{A_TOPSHEET}", wait=3.4),
]

# ============================================= 10. ADVANCE & ADJUSTMENT ===
F10 = [
    L("advance_list", "Advances & Petty Cash → Advance Requests",
      "Staff going to the field ask for money in advance (Annexure-18).",
      ["tr.o_data_row", ".o_data_row"], "ACCOUNTS OFFICER",
      goto=f"/odoo/action-{A_ADV}", wait=4.0),
    S("advance_open", "An advance request",
      "15,000 for a community awareness session in Camp 12, with the purpose broken into lines.",
      ["div[name='employee_id']", "h1"], "ACCOUNTS OFFICER",
      goto=f"/odoo/action-{A_ADV}/{ADVANCE}", wait=3.4),
    S("advance_chain", "Finance check → review → approve → pay",
      "Four stages, and paying it posts a real journal entry: Dr Employee Advances / Cr Bank.",
      [".o_statusbar_status", ".o_statusbar_buttons button"], "FINANCE MANAGER", wait=2.8,
      note="ADV-003: a person cannot take a new advance while an old one is unadjusted."),
    S("adjust_list", "Advance Adjustments (Annexure-19)",
      "After the activity, the employee accounts for what was actually spent.",
      ["tr.o_data_row", ".o_data_row"], "ACCOUNTS OFFICER",
      goto=f"/odoo/action-{A_ADJ}", wait=3.6),
    S("adjust_open", "The expenditure lines",
      "Each real cost is listed. The system compares it against what was advanced.",
      ["div[name='line_ids']", ".o_field_x2many"], "ACCOUNTS OFFICER",
      goto=f"/odoo/action-{A_ADJ}/{ADJUSTMENT}", wait=3.4),
    S("adjust_settle", "Settle it",
      "One journal entry clears the advance and books the expenses — refund or extra is automatic.",
      [".o_statusbar_buttons button", "button:has-text('Settle')"], "FINANCE MANAGER", wait=2.8),
]

# =================================================== 11. IOU & PETTY CASH =
F11 = [
    L("iou_list", "IOU / Cash Requisition (Annexure-13)",
      "For small urgent needs that cannot wait for the full advance process.",
      ["tr.o_data_row", ".o_data_row"], "ACCOUNTS OFFICER",
      goto=f"/odoo/action-{A_IOU}", wait=4.0),
    S("iou_open", "An IOU",
      "2,500 for urgent stationery. Submit → approve → pay → adjust, same idea but lighter.",
      ["div[name='employee_id']", "h1"], "ACCOUNTS OFFICER",
      goto=f"/odoo/action-{A_IOU}/{IOU}", wait=3.4),
    S("topup_list", "Petty Cash Top-Up",
      "Moving money from the bank into the office cash box.",
      ["tr.o_data_row", ".o_data_row"], "ACCOUNTS OFFICER",
      goto=f"/odoo/action-{A_TOPUP}", wait=3.6),
    S("topup_open", "Request → approve → done",
      "Approving it posts the transfer: Dr Petty Cash / Cr Bank.",
      [".o_statusbar_status", "div[name='amount']"], "FINANCE MANAGER",
      goto=f"/odoo/action-{A_TOPUP}/{TOPUP}", wait=3.4),
    S("count_list", "Daily Cash Count (Annexure-14)",
      "Physically counting the cash box and comparing it to the book balance.",
      ["tr.o_data_row", ".o_data_row"], "ACCOUNTS OFFICER",
      goto=f"/odoo/action-{A_COUNT}", wait=3.6),
    S("count_open", "Count by denomination",
      "How many 1000 notes, how many 500 — the system totals it and shows any difference.",
      ["div[name='line_ids']", ".o_field_x2many"], "ACCOUNTS OFFICER",
      goto=f"/odoo/action-{A_COUNT}/{CASHCOUNT}", wait=3.4,
      note="A difference here means the cash box does not agree with the books — investigate it."),
    S("pettybook_wizard", "Petty Cash Book (Annexure-15)",
      "Pick the cash journal and the dates, then print the running-balance cash book.",
      ["div[name='journal_id']", "button:has-text('Print')", ".modal"], "ACCOUNTS OFFICER",
      goto=f"/odoo/action-{A_PETTYBOOK}", wait=3.6),
]

# ======================================================== 12. BUDGETS =====
F12 = [
    L("budgets_list", "Accounting → Budgets",
      "One budget per project per financial year — this is the Annexure-27 budget.",
      ["tr.o_data_row", ".o_data_row"], "FINANCE MANAGER",
      goto=f"/odoo/action-{A_BUDGETS}", wait=4.2),
    S("budget_open", "The project budget",
      "GBViE FY 25-26, funded by CARE. Each line is an activity with its own amount.",
      ["div[name='name']", "h1"], "FINANCE MANAGER",
      goto=f"/odoo/action-{A_BUDGETS}/{BUDGET}", wait=3.6),
    S("budget_lines", "Activity lines",
      "Activity code, cost category, unit, times, unit cost — the amount calculates itself.",
      ["div[name='budget_line_ids']", ".o_field_x2many"], "FINANCE MANAGER", wait=3.0,
      note="Spending against a budgeted line is blocked once the budget is exhausted (BUD-004)."),
    S("wb_list", "MCB Budgets → Working Budgets (Annexure-26)",
      "Field teams break the annual budget into a quarter's activities.",
      ["tr.o_data_row", ".o_data_row"], "FINANCE MANAGER",
      goto=f"/odoo/action-{A_WB}", wait=3.6),
    S("wb_open", "A working budget",
      "Q1 learning-centre construction — cement, labour, transport, with live consumption.",
      ["div[name='activity_name']", "h1"], "FINANCE MANAGER",
      goto=f"/odoo/action-{A_WB}/{WORKBUDGET}", wait=3.4),
    S("wb_consumed", "Budget vs consumed",
      "The consumed figure updates itself from the actual entries coded to that project.",
      ["div[name='amount_consumed']", "div[name='amount_total']"], "FINANCE MANAGER", wait=2.8),
]

# ============================================ 13. REVISION & DONOR REPORT =
F13 = [
    L("rev_list", "MCB Budgets → Budget Revisions",
      "Moving money between budget lines has to be recorded and approved.",
      ["tr.o_data_row", ".o_data_row"], "FINANCE MANAGER",
      goto=f"/odoo/action-{A_REV}", wait=4.0),
    S("rev_open", "A revision",
      "Old amount, new amount, and the reason. The change percentage is calculated.",
      ["div[name='new_amount']", "h1", "div[name='reason']"], "FINANCE MANAGER",
      goto=f"/odoo/action-{A_REV}/{REVISION}", wait=3.4),
    S("rev_ce_gate", "Over 10% needs the Chief Executive",
      "This one moves the line by 30%, so only the CE can approve it. Anyone else is refused.",
      ["div[name='requires_ce']", "div[name='delta_pct']", "[name='requires_ce']"],
      "CHIEF EXECUTIVE", wait=3.0,
      note="BUD-005 — the 10% rule is enforced by the system, not by memory."),
    S("donor_wizard", "Donor Budget vs Actual",
      "Choose the budget and the period — monthly, quarterly, half-yearly or annual.",
      ["div[name='budget_id']", "div[name='granularity']", ".modal"], "FINANCE MANAGER",
      goto=f"/odoo/action-{A_DONOR}", wait=3.6),
    S("donor_currency", "Report in the donor's currency",
      "Optionally convert to the donor's own currency at a rate you supply.",
      ["div[name='display_currency_id']", "div[name='manual_rate']", ".modal"],
      "FINANCE MANAGER", wait=2.8),
]

# ========================================================= 14. ASSETS =====
F14 = [
    L("asset_list", "Accounting → Assets",
      "Everything MCB owns — generators, laptops, furniture — with its donor and custodian.",
      ["tr.o_data_row", ".o_data_row"], "FINANCE MANAGER",
      goto=f"/odoo/action-{A_ASSET}", wait=4.2),
    S("asset_open", "An asset",
      "15 KVA generator at Camp 12, funded by CARE, with a named custodian.",
      ["div[name='name']", "h1"], "FINANCE MANAGER",
      goto=f"/odoo/action-{A_ASSET}/{ASSET_GEN}", wait=3.6),
    S("asset_mcb_fields", "Custodian, location, condition, donor",
      "These four answer the questions an auditor actually asks about an asset.",
      ["div[name='mcb_custodian_id']", "div[name='mcb_location']", "[name='mcb_condition']"],
      "FINANCE MANAGER", wait=3.0),
    S("asset_depreciation", "The depreciation schedule",
      "Odoo posts the depreciation entries for you, month by month.",
      ["div[name='depreciation_move_ids']", ".o_field_x2many", "a:has-text('Depreciation')"],
      "FINANCE MANAGER", wait=2.8),
    S("asset_register_wizard", "Fixed Assets Register (Annexure-07)",
      "Opening value, charge for the period, closing value and written-down value.",
      ["div[name='date_from']", "button:has-text('Print')", ".modal"], "FINANCE MANAGER",
      goto=f"/odoo/action-{A_ASSETREG}", wait=3.6),
    S("asset_inventory", "Physical Inventory (Annexure-22)",
      "Counting what is actually there against what the register says.",
      ["div[name='line_ids']", ".o_field_x2many"], "FINANCE MANAGER",
      goto=f"/odoo/action-{A_ASSETINV}/{ASSET_INV}", wait=3.6),
    S("asset_disposal", "Disposal needs the CE",
      "The old photocopier is marked for disposal — but only the CE can approve writing it off.",
      ["button:has-text('CE Approve')", "div[name='mcb_ce_disposal_approved']",
       ".o_statusbar_buttons button"], "CHIEF EXECUTIVE",
      goto=f"/odoo/action-{A_ASSET}/{ASSET_OLD}", wait=3.4,
      note="AST-005 — no asset leaves MCB without the Chief Executive's approval."),
]

# ================================================== 15. BANK RECONCILE ====
F15 = [
    L("bankrec_wizard", "MCB Registers → Bank Reconciliation",
      "Comparing MCB's cash book against what the bank statement says.",
      ["div[name='journal_id']", ".modal", "button:has-text('Print')"], "FINANCE MANAGER",
      goto=f"/odoo/action-{A_BANKREC}", wait=4.0),
    S("bankrec_fields", "Enter the bank's closing balance",
      "Type the balance from the bank statement, then print. Everything else is worked out.",
      ["div[name='statement_balance']", "[name='statement_balance']", ".modal"],
      "FINANCE MANAGER", wait=2.8,
      note="A = bank balance · B = deposits not yet shown · D = cheques not yet cleared · F = difference."),
    S("chequereg_wizard", "Cheque Issue Register (Annexure-02)",
      "Every cheque written in a period, with number, party, purpose and amount.",
      ["div[name='journal_id']", ".modal", "button:has-text('Print')"], "ACCOUNTS OFFICER",
      goto=f"/odoo/action-{A_CHEQREG}", wait=3.6),
    S("bank_entries", "The bank journal entries",
      "Everything that went through the bank account, in date order.",
      ["tr.o_data_row", ".o_data_row"], "ACCOUNTS OFFICER",
      goto=f"/odoo/action-{A_MOVE}", wait=3.6),
]

# ================================================= 16. REPORTS & CLOSE ====
F16 = [
    L("report_bs", "Reporting → Balance Sheet",
      "What MCB owns and owes on a given date. Assets = Liabilities + Fund Balance.",
      [".o_account_report", "table", ".o_content"], "FINANCE MANAGER",
      goto=f"/odoo/action-{R_BS}", wait=5.0),
    S("report_pl", "Profit and Loss",
      "Income and expenditure for the period — for an NGO, funds received against funds spent.",
      [".o_account_report", "table", ".o_content"], "FINANCE MANAGER",
      goto=f"/odoo/action-{R_PL}", wait=4.5),
    S("report_tb", "Trial Balance",
      "Every account with its debit and credit totals. The two columns must agree.",
      [".o_account_report", "table", ".o_content"], "FINANCE MANAGER",
      goto=f"/odoo/action-{R_TB}", wait=4.5),
    S("report_gl", "General Ledger",
      "Drill into any account to see every entry that made up its balance.",
      [".o_account_report", "table", ".o_content"], "FINANCE MANAGER",
      goto=f"/odoo/action-{R_GL}", wait=4.5,
      note="This is the report auditors ask for first — click any figure to open the entry."),
    S("report_ar", "Aged Receivable",
      "Who owes MCB money, and for how long.",
      [".o_account_report", "table", ".o_content"], "FINANCE MANAGER",
      goto=f"/odoo/action-{R_AR}", wait=4.5),
    S("report_ap", "Aged Payable",
      "Who MCB owes money to, split by how overdue it is.",
      [".o_account_report", "table", ".o_content"], "FINANCE MANAGER",
      goto=f"/odoo/action-{R_AP}", wait=4.5),
    S("report_donor", "Donor / project financial report",
      "Income, expenditure and balance for one project and donor — what the donor asks for.",
      ["div[name='date_from']", ".modal", "button:has-text('Print')"], "FINANCE MANAGER",
      goto=f"/odoo/action-{A_ANALYTIC}", wait=3.6),
    S("year_end", "Year-end closing",
      "At 30 June, one entry moves the year's surplus or deficit into the Fund Balance.",
      ["div[name='fiscal_date']", ".modal", "button:has-text('Closing')"], "FINANCE MANAGER",
      goto=f"/odoo/action-{A_YEAREND}", wait=3.6,
      note="Run this once, after the last entry of the financial year is posted."),
]

ALL = [
    ("acc01_chart", F1), ("acc02_journals", F2), ("acc03_fiscal_tax", F3),
    ("acc04_partners", F4), ("acc05_voucher", F5), ("acc06_receipt", F6),
    ("acc07_payment", F7), ("acc08_bill", F8), ("acc09_vat_tds", F9),
    ("acc10_advance", F10), ("acc11_petty", F11), ("acc12_budget", F12),
    ("acc13_revision", F13), ("acc14_assets", F14), ("acc15_bank", F15),
    ("acc16_reports", F16),
]

if __name__ == "__main__":
    only = sys.argv[1:] or None
    for name, steps in ALL:
        if only and name not in only:
            continue
        print(f"\n=== {name.upper()} ===")
        run_flow(name, steps)
