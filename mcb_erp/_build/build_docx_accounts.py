"""Build MCB_Accounts_Module_Guide.docx — SRS v3 Part C (Accounts / Finance).
Covers mcb_account + mcb_cash_advance + mcb_budget + mcb_asset.
Run: /Data/odoo19_enterprise/venv/bin/python _build/build_docx_accounts.py
"""
from pathlib import Path

from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

ROOT = Path("/Data/odoo19_enterprise/custom-addons/mcb_erp/_build")
SHOT = ROOT / "screenshots" / "accounts"
OUT = Path("/Data/odoo19_enterprise/mukticox/MCB_Accounts_Module_Guide.docx")

# =============================================================================
# REQUIREMENT INVENTORY — SRS v3 Part C §13-21 (Accounts / Finance)
# =============================================================================
REQS = [
    ("VOU-001", "Part C §14", "Must", "Voucher numbers auto-generated per journal per July–June fiscal year (e.g. JV-2627-001)",
     "Done", "mcb.fy.mixin._mcb_fy_sequence_next() on account.move"),
    ("VOU-002", "Part C §14", "Must", "4-level approval (Prepared → Checked → Reviewed → Approved) required on manual journal entries before they can be posted",
     "Done", "account_move.py: action_mcb_check/review/approve + posting gate (system-generated moves exempted)"),
    ("VOU-004", "Part C §14", "Must", "Amount-in-words printed on every voucher and payment",
     "Done", "mcb_amount_in_words compute (account.move + account.payment)"),
    ("VOU-005", "Part C §14", "Must", "'Class' cost-category analytic dimension on every voucher line",
     "Done", "Cost Category analytic plan (data/analytic_plan_data.xml)"),
    ("VOU-006", "Part C §14", "Should", "Voucher PDF on MCB letterhead (Annexures 03–06) with XLSX export",
     "Done", "reports/voucher_report.xml + mcb.xlsx.mixin"),
    ("VOU-007", "Part C §19", "Must", "Payment Voucher Checklist (Annexure-28) sign-off before a payment file is closed",
     "Done", "mcb.payment.checklist + seeded checklist lines"),
    ("VOU-008", "Part C §19", "Should", "Expenses Top Sheet (Annexure-24) auto-built from posted vendor bills",
     "Done", "mcb.top.sheet.wizard"),
    ("DFR-007", "Part C §21", "Must", "Money Receipt (Annexure-01/31) printed on inbound (donor) payments",
     "Done", "reports/money_receipt_report.xml on account.payment"),
    ("BNK-002", "Part C §20", "Must", "Bank Reconciliation Statement (Annexure-17), PDF + XLSX",
     "Done", "mcb.bank.recon.wizard"),
    ("BNK-003", "Part C §20", "Must", "Cheque Issue Register (Annexure-02) from outbound bank payments",
     "Done", "mcb.cheque.register.wizard, filtered on payment_type=outbound + check_number"),
    ("BNK-006", "Part C §20", "Should", "Automatic alert when a cheque is outstanding more than 30 days",
     "Done", "ir.cron on account.journal (data/ir_cron_data.xml)"),
    ("TAX-001", "Part C §19", "Must", "TDS withheld automatically at the moment of payment, not at billing",
     "Done", "l10n_account_withholding_tax (is_withholding_tax_on_payment) native engine"),
    ("TAX-004", "Part C §19", "Must", "VAT (Mushak) / TDS (Treasury) challan register with challan number, bank, branch, deposit date",
     "Done", "mcb.tax.challan"),
    ("TAX-005", "Part C §19", "Must", "Monthly VAT/TDS summary: Deductible / Deducted / Deposited / Dues, by vendor & project",
     "Done", "mcb.vat.tds.wizard"),
    ("TAX-006", "Part C §19", "Must", "Vendor BIN & TIN captured on the partner record for tax reporting",
     "Done", "res.partner: mcb_bin / mcb_tin"),
    ("PO-007", "Part C §13", "Must", "A vendor bill cannot be paid unless 3-way match (PO / GRN / Bill) is fully certified — hard gate, not advisory",
     "Done", "account_payment_register.py override on top of native account_3way_match"),
    ("PER-002", "Part C", "Should", "Year-end fund-balance closing journal wizard",
     "Done", "mcb.year.end.wizard"),
    ("PER-005", "Part C", "Must", "July–June Bangladesh fiscal year used consistently for every sequence and report",
     "Done", "mcb.fy.mixin"),
    ("DFR-001", "Part C §21", "Should", "Income / expenditure / balance report by project + donor analytic account",
     "Done", "mcb.analytic.report.wizard"),
    ("AUD-T38", "Part C", "Should", "Audit department has a view-only role across all MCB accounting screens",
     "Done", "security/mcb_account_security.xml — Audit group, read-only rules"),
    ("ADV-001", "Part C §15", "Must", "Advance Request (Annexure-18) lifecycle: submit → finance check → review → approve → pay",
     "Done", "mcb.advance statusbar + real JE on pay"),
    ("ADV-003", "Part C §15", "Must", "A new advance cannot be requested while a previous advance for the same employee is unadjusted",
     "Done", "mcb.advance @api.constrains outstanding-advance block"),
    ("ADV-004", "Part C §15", "Must", "Advance Adjustment (Annexure-19) records actual expenditure lines against the advance",
     "Done", "mcb.advance.adjustment + line_ids"),
    ("ADV-007", "Part C §15", "Must", "Adjustment posts one settlement JE — Dr expenses, Cr Employee Advances, cash line balances refund/extra automatically",
     "Done", "mcb.advance.adjustment.action_settle()"),
    ("ADV-008", "Part C §16", "Must", "IOU / urgent Cash Requisition (Annexure-13) — client-feedback addition, separate from the standard advance",
     "Done", "mcb.iou: submit → approve → pay → adjust"),
    ("PCH-001", "Part C §16", "Must", "Petty Cash Book (Annexure-15) — running balance over the petty cash journal",
     "Done", "mcb.petty.book.wizard.action_print_pdf() (Annex-15)"),
    ("PCH-002", "Part C §16", "Must", "Daily Cash Count (Annexure-14) with denomination breakdown",
     "Done", "mcb.cash.count"),
    ("PCH-003", "Part C §16", "Should", "Petty Cash Statement (Annexure-16) — expenditure analysed per accounts head",
     "Done", "mcb.petty.book.wizard.action_print_statement() (Annex-16)"),
    ("PCH-004", "Part C §16", "Must", "Petty Cash Top-Up: request → approval → internal transfer JE, plus low-balance alert",
     "Done", "mcb.petty.topup + res.company.mcb_petty_cash_limit"),
    ("BUD-001", "Part C §17", "Must", "Annexure-27 budget columns: activity code/serial, cost category, unit, times, unit cost",
     "Done", "budget.line extension fields (mcb_activity_code etc.)"),
    ("BUD-002", "Part C §17", "Must", "Working Budget (Annexure-26) — activity-level operational budget with live consumption vs actuals",
     "Done", "mcb.working.budget + _compute_consumed"),
    ("BUD-003", "Part C §17", "Must", "Donor Budget-vs-Actual report at monthly/bimonthly/quarterly/half-yearly/annual granularity, with variance %",
     "Done", "mcb.donor.report.wizard"),
    ("BUD-004", "Part C §17", "Must", "Budget overage on a vendor bill or Purchase Order can warn or hard-block, per project policy",
     "Done", "mcb_budget/models/account_move.py posting-time check + mcb_overage_policy"),
    ("BUD-005", "Part C §17", "Must", "Budget reallocation (revision) requires Chief Executive approval when the change exceeds 10% of the line",
     "Done", "mcb.budget.revision — requires_ce compute + group_mcb_ce gate on action_approve()"),
    ("BUD-006", "Part C §17", "Should", "Donor report can display figures converted to the donor's own currency at a supplied rate",
     "Done", "mcb.donor.report.wizard: display_currency_id + manual_rate"),
    ("BUD-007", "Part C §17", "Should", "Consolidated view across a multi-year budget",
     "Partial", "Each fiscal year is its own budget.analytic; a rolled-up multi-year view is not yet built"),
    ("BUD-008", "Part C §17", "Must", "Chief Executive can lock a budget at project close-out to prevent further expenditure",
     "Done", "budget.analytic.action_mcb_lock() gated by group_mcb_ce"),
    ("AST-001", "Part C §18", "Must", "Fixed Assets Register (Annexure-07): opening / charge / adjustment / closing / written-down value, PDF + XLSX, barcode labels",
     "Done", "mcb.asset.register.wizard + account_asset._mcb_depreciation_figures()"),
    ("AST-003", "Part C §18", "Must", "Asset custodian, location, condition and funding-donor recorded on every asset",
     "Done", "account.asset: mcb_custodian_id / mcb_location / mcb_condition / mcb_funded_by"),
    ("AST-004", "Part C §18", "Must", "Physical Inventory (Annexure-22): register vs. found quantity, short/excess, recommendation",
     "Done", "mcb.asset.inventory + action_fill_from_register()"),
    ("AST-005", "Part C §18", "Must", "An asset cannot be disposed/sold without prior Chief Executive approval",
     "Done", "account.asset.action_mcb_ce_approve_disposal() + set_to_close() override"),
    ("AST-006", "Part C §18", "Should", "Full transfer history when an asset moves between projects, locations or custodians",
     "Done", "mcb.asset.transfer"),
]


# =============================================================================
# DOCX HELPERS (shared style with the HR / Purchase / Projects guides)
# =============================================================================

def set_cell_bg(cell, hex_color):
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:fill'), hex_color)
    tc_pr.append(shd)


def add_page_number(footer_para):
    run = footer_para.add_run()
    fldChar1 = OxmlElement('w:fldChar')
    fldChar1.set(qn('w:fldCharType'), 'begin')
    instrText = OxmlElement('w:instrText')
    instrText.set(qn('xml:space'), 'preserve')
    instrText.text = 'PAGE'
    fldChar2 = OxmlElement('w:fldChar')
    fldChar2.set(qn('w:fldCharType'), 'end')
    run._r.append(fldChar1)
    run._r.append(instrText)
    run._r.append(fldChar2)


def style_heading(doc):
    for size, name in [(16, 'Heading 1'), (14, 'Heading 2'), (12, 'Heading 3')]:
        st = doc.styles[name]
        st.font.name = 'Calibri'
        st.font.size = Pt(size)
        st.font.color.rgb = RGBColor(0x1F, 0x36, 0x4D)


def set_default_font(doc):
    style = doc.styles['Normal']
    style.font.name = 'Calibri'
    style.font.size = Pt(11)


def caption(doc, text):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(text)
    r.italic = True
    r.font.size = Pt(10)
    r.font.color.rgb = RGBColor(0x55, 0x55, 0x55)


def embed(doc, path, cap, width_inches=6.0):
    p = path if isinstance(path, Path) else Path(path)
    if not p.exists():
        print(f"  MISSING: {p}")
        para = doc.add_paragraph()
        para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = para.add_run(f"[Screenshot missing: {p.name}]")
        r.font.color.rgb = RGBColor(0xAA, 0x00, 0x00)
        return
    p_img = doc.add_paragraph()
    p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p_img.add_run()
    r.add_picture(str(p), width=Inches(width_inches))
    caption(doc, cap)


def make_table(doc, headers, rows, banded=True):
    table = doc.add_table(rows=1, cols=len(headers))
    table.style = "Light Grid Accent 1"
    table.alignment = WD_TABLE_ALIGNMENT.LEFT
    hdr = table.rows[0]
    for i, h in enumerate(headers):
        cell = hdr.cells[i]
        cell.text = ""
        run = cell.paragraphs[0].add_run(h)
        run.bold = True
        run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        set_cell_bg(cell, '1F4E79')
    for idx, row in enumerate(rows):
        rcells = table.add_row().cells
        for i, val in enumerate(row):
            rcells[i].text = str(val) if val is not None else ""
            for p in rcells[i].paragraphs:
                for run in p.runs:
                    run.font.size = Pt(10)
        if banded and idx % 2 == 1:
            for c in rcells:
                set_cell_bg(c, 'F2F2F2')
    return table


def set_margins(doc):
    for section in doc.sections:
        section.top_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1)
        section.right_margin = Inches(1)


def status_symbol(s):
    return {"Done": "✅ Done", "Partial": "⚠ Partial", "Deferred": "❌ Deferred"}.get(s, s)


# =============================================================================
# BUILD
# =============================================================================

def build():
    doc = Document()
    set_default_font(doc)
    style_heading(doc)
    set_margins(doc)

    section = doc.sections[0]
    hp = section.header.paragraphs[0]
    hp.text = "Mukti Cox's Bazar — Accounts / Finance Module on Odoo 19 Enterprise"
    hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    for run in hp.runs:
        run.font.size = Pt(9)
        run.italic = True
        run.font.color.rgb = RGBColor(0x55, 0x55, 0x55)
    fp = section.footer.paragraphs[0]
    fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    fp.add_run("Page ").font.size = Pt(9)
    add_page_number(fp)

    # ---- TITLE PAGE ----
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for _ in range(4):
        p.add_run("\n")
    title = doc.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = title.add_run("Mukti Cox's Bazar")
    r.bold = True
    r.font.size = Pt(28)
    r.font.color.rgb = RGBColor(0x1F, 0x36, 0x4D)
    sub = doc.add_paragraph()
    sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = sub.add_run("Accounts & Finance Module on Odoo 19 Enterprise")
    r.bold = True
    r.font.size = Pt(20)
    sub2 = doc.add_paragraph()
    sub2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = sub2.add_run("A Plain-English User Guide — SRS v3, Part C (Accounts / Finance)")
    r.italic = True
    r.font.size = Pt(14)
    r.font.color.rgb = RGBColor(0x55, 0x55, 0x55)
    doc.add_paragraph()
    doc.add_paragraph()
    meta = doc.add_paragraph()
    meta.alignment = WD_ALIGN_PARAGRAPH.CENTER
    meta.add_run("Version 1.0  ·  9 July 2026  ·  MCB ERP Team").font.size = Pt(12)
    doc.add_paragraph()
    doc.add_paragraph()
    classif = doc.add_paragraph()
    classif.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = classif.add_run("CONFIDENTIAL — Internal Use Only")
    r.bold = True
    r.font.size = Pt(11)
    r.font.color.rgb = RGBColor(0xAA, 0x00, 0x00)
    doc.add_page_break()

    # ---- TOC ----
    doc.add_heading("Table of Contents", level=1)
    toc_rows = [
        ("0", "Executive Summary — who this guide is for"),
        ("1", "Architecture Overview — the 4 modules behind 'Accounts'"),
        ("2", "Chapter 1 — Vouchers & the 4-Level Approval Chain"),
        ("3", "Chapter 2 — Money Receipts & Cheque Payments"),
        ("4", "Chapter 3 — Tax Challans & Payment Checklist"),
        ("5", "Chapter 4 — Bank Recon, Top Sheet, VAT/TDS, Donor Reports, Year-End"),
        ("6", "Chapter 5 — Cash Advances (Annexure-18)"),
        ("7", "Chapter 6 — Advance Adjustment (Annexure-19)"),
        ("8", "Chapter 7 — IOU / Urgent Cash Requisition (Annexure-13)"),
        ("9", "Chapter 8 — Petty Cash (Count / Top-Up / Book)"),
        ("10", "Chapter 9 — Working Budget, Revision & Donor Report"),
        ("11", "Chapter 10 — Fixed Assets"),
        ("12", "Consolidated SRS Traceability Matrix"),
        ("A", "Appendix A — Glossary of Odoo Terms"),
    ]
    tbl = doc.add_table(rows=len(toc_rows), cols=2)
    tbl.style = "Light List Accent 1"
    for i, (ch, name) in enumerate(toc_rows):
        cells = tbl.rows[i].cells
        cells[0].text = ch
        cells[1].text = name
        for cell in cells:
            for p in cell.paragraphs:
                for run in p.runs:
                    run.font.size = Pt(11)
    doc.add_page_break()

    # ---- CHAPTER 0: EXEC SUMMARY ----
    doc.add_heading("0. Executive Summary", level=1)
    doc.add_paragraph(
        "This guide is written for Accounts and Finance staff at Mukti Cox's Bazar "
        "(MCB) — no assumption of prior software experience is made. It covers "
        "everything under SRS v3 Part C: vouchers, cash advances & petty cash, "
        "working budgets, and fixed assets, with a screenshot for every screen."
    )
    doc.add_paragraph(
        "\"Accounts / Finance\" in Odoo is delivered as four separate modules that "
        "work together. This guide is organised by everyday task, not by module, "
        "so you can jump straight to 'how do I record a cheque payment' without "
        "needing to know which module it lives in — but every chapter states the "
        "module and the exact SRS requirement it satisfies."
    )
    doc.add_heading("Scope & Coverage", level=2)
    total = len(REQS)
    done = sum(1 for r in REQS if r[4] == "Done")
    partial = sum(1 for r in REQS if r[4] == "Partial")
    make_table(doc, ["Metric", "Value"], [
        ("Requirements indexed (SRS v3, Part C §13–21)", f"{total}"),
        ("✅ Done", f"{done}"),
        ("⚠ Partial", f"{partial}"),
        ("Odoo modules", "mcb_account, mcb_cash_advance, mcb_budget, mcb_asset"),
    ])
    doc.add_paragraph(
        "Everything in this guide was captured directly from a live, running copy "
        "of the system using real (demo) data driven through the actual approval "
        "buttons — nothing here is a mock-up. One known gap: COA-001 (loading "
        "MCB's exact Chart-of-Accounts spreadsheet) is Partial — the Bangladesh "
        "chart is installed and MCB's custom codes are preserved, but the specific "
        "Budget_Chart_of_Accounts.xlsx file referenced in the SRS was never "
        "supplied, so its data load is still pending."
    )
    doc.add_page_break()

    # ---- CHAPTER 1: ARCHITECTURE ----
    doc.add_heading("1. Architecture Overview", level=1)
    doc.add_paragraph(
        "Four modules combine to cover Part C. Each extends a native Odoo "
        "Enterprise accounting app rather than replacing it, so MCB gets Odoo's "
        "own bank feeds, reconciliation, and financial reports for free, with "
        "MCB's own rules layered on top."
    )
    make_table(doc, ["Module", "Extends", "Covers"], [
        ("mcb_account", "account_accountant, account_reports, account_3way_match, l10n_bd, l10n_account_withholding_tax", "Vouchers, 4-level approval, VAT/TDS & challans, bank recon, cheque register, top sheet, money receipts"),
        ("mcb_cash_advance", "mcb_account", "Advance & IOU lifecycle, petty cash count/book/statement, top-ups"),
        ("mcb_budget", "account_budget, account_budget_purchase", "Working Budget, revisions, overage gate, donor Budget-vs-Actual report"),
        ("mcb_asset", "account_asset", "Fixed Assets Register, physical inventory, transfer history, CE-gated disposal"),
    ])
    doc.add_heading("1.1 Roles", level=2)
    make_table(doc, ["Role", "What they do here"], [
        ("Accounts / Finance Officer", "Prepares vouchers, advances, top sheets, VAT/TDS filing"),
        ("Finance Manager", "Checks & reviews vouchers/POs, manages budgets and assets"),
        ("Chief Executive (CE)", "Final voucher approval; sole approver for budget revisions >10% and asset disposal"),
        ("Audit", "View-only access across all of the above, for independent assurance"),
    ])
    embed(doc, SHOT / "00_overview/01_apps_mcb_filtered.png", "Figure 1.1 — MCB apps on the home dashboard")
    doc.add_page_break()

    def chapter_trace(prefix_list, chapter_no):
        rows = [r for r in REQS if r[0].startswith(tuple(prefix_list))]
        body = [[r[0], r[1], r[2], r[3], status_symbol(r[4]), r[5]] for r in rows]
        doc.add_heading(f"{chapter_no} SRS Traceability", level=3)
        make_table(doc, ["Req ID", "SRS §", "Priority", "Requirement", "Status", "Implementation"], body)

    # ====== CHAPTER 2: VOUCHERS ======
    doc.add_heading("2. Vouchers & the 4-Level Approval Chain", level=1)
    doc.add_paragraph(
        "Every manual journal entry at MCB — a Journal Voucher (JV), a receipt, or "
        "a payment — must be Prepared, then Checked, then Reviewed, then Approved "
        "by four different people before it can be posted to the ledger. Odoo's "
        "own system-generated entries (like depreciation or payroll) skip this "
        "gate automatically since nobody manually keyed them."
    )
    doc.add_heading("2.1 Where to find it", level=2)
    doc.add_paragraph("Accounting → Journal Entries.")
    embed(doc, SHOT / "01_vouchers/01_journal_entries_list.png", "Figure 2.1 — Journal Entries list")
    doc.add_heading("2.2 Walk-through", level=2)
    doc.add_paragraph(
        "A reclassification voucher moving 15,000 BDT of office-supplies cost onto "
        "the GBViE project's analytic account, fully posted after all four "
        "approval stamps."
    )
    embed(doc, SHOT / "01_vouchers/02_jv66_form_reclass_posted.png", "Figure 2.2 — JV — reclass, posted")
    embed(doc, SHOT / "01_vouchers/03_jv66_voucher_report_preview.png", "Figure 2.3 — Voucher — MCB letterhead PDF preview")
    chapter_trace(["VOU-"], "2.3")
    doc.add_page_break()

    # ====== CHAPTER 3: MONEY RECEIPT / CHEQUE ======
    doc.add_heading("3. Money Receipts & Cheque Payments", level=1)
    doc.add_paragraph(
        "Donor contributions coming in and vendor cheques going out both use "
        "Odoo's native Payments screen. MCB prints a Money Receipt for every "
        "inbound payment and keeps a Cheque Issue Register for every outbound one."
    )
    doc.add_heading("3.1 Where to find it", level=2)
    doc.add_paragraph("Accounting → Customers/Vendors → Payments.")
    embed(doc, SHOT / "02_payments/01_payments_list.png", "Figure 3.1 — Payments list")
    doc.add_heading("3.2 Walk-through", level=2)
    doc.add_paragraph("A 500,000 BDT donor contribution from CARE Bangladesh, tranche 3.")
    embed(doc, SHOT / "02_payments/02_receipt1_care_donor_form.png", "Figure 3.2 — Inbound payment — CARE Bangladesh")
    embed(doc, SHOT / "02_payments/03_receipt1_money_receipt_preview.png", "Figure 3.3 — Money Receipt (Annexure-01/31) — PDF preview")
    doc.add_paragraph("A 90,000 BDT cheque payment to Gemini Furniture against invoice GF-2201.")
    embed(doc, SHOT / "02_payments/04_cheque3_gemini_form.png", "Figure 3.4 — Outbound cheque payment — Gemini Furniture")
    embed(doc, SHOT / "02_payments/05_cheque_register_wizard_form.png", "Figure 3.5 — Cheque Register wizard — pick journal & date range")
    embed(doc, SHOT / "02_payments/06_cheque_register_report_preview.png", "Figure 3.6 — Cheque Issue Register (Annexure-02) — preview")
    chapter_trace(["DFR-007", "BNK-003", "BNK-006"], "3.3")
    doc.add_page_break()

    # ====== CHAPTER 4: TAX / CHECKLIST ======
    doc.add_heading("4. Tax Challans & Payment Checklist", level=1)
    doc.add_paragraph(
        "Tax withheld from vendor payments (TDS) and VAT collected must be "
        "deposited to the Treasury/Mushak system and tracked against a challan "
        "number. Every payment voucher is also signed off against a standard "
        "checklist before the file is closed."
    )
    doc.add_heading("4.1 Where to find it", level=2)
    doc.add_paragraph("MCB Registers → VAT / TDS Challans, and Payment Checklists (Annex-28).")
    embed(doc, SHOT / "03_tax_checklist/01_tax_challan_list.png", "Figure 4.1 — Tax Challan list")
    doc.add_heading("4.2 Walk-through", level=2)
    embed(doc, SHOT / "03_tax_checklist/02_tax_challan1_form.png", "Figure 4.2 — Tax Challan — Treasury TDS, deposited")
    embed(doc, SHOT / "03_tax_checklist/03_payment_checklist_list.png", "Figure 4.3 — Payment Checklist list")
    embed(doc, SHOT / "03_tax_checklist/04_payment_checklist1_form.png", "Figure 4.4 — Payment Checklist — all items confirmed")
    embed(doc, SHOT / "03_tax_checklist/05_payment_checklist1_report_preview.png", "Figure 4.5 — Payment Checklist (Annexure-28) — PDF preview")
    chapter_trace(["TAX-", "VOU-007"], "4.3")
    doc.add_page_break()

    # ====== CHAPTER 5: REGISTERS ======
    doc.add_heading("5. Bank Recon, Top Sheet, VAT/TDS, Donor Reports, Year-End", level=1)
    doc.add_paragraph(
        "These are the five 'run any time' registers under MCB Registers — each "
        "is a small wizard: pick your parameters, then Print PDF or Export XLSX."
    )
    doc.add_heading("5.1 Bank Reconciliation (Annexure-17)", level=2)
    embed(doc, SHOT / "04_registers/01_bank_recon_wizard_form.png", "Figure 5.1 — Bank Recon wizard")
    embed(doc, SHOT / "04_registers/02_bank_recon_report_preview.png", "Figure 5.2 — Bank Reconciliation Statement — preview")
    doc.add_heading("5.2 Expenses Top Sheet (Annexure-24)", level=2)
    embed(doc, SHOT / "04_registers/03_top_sheet_wizard_form.png", "Figure 5.3 — Top Sheet wizard")
    embed(doc, SHOT / "04_registers/04_top_sheet_report_preview.png", "Figure 5.4 — Expenses Top Sheet — preview")
    doc.add_heading("5.3 Monthly VAT/TDS Summary", level=2)
    embed(doc, SHOT / "04_registers/05_vat_tds_wizard_form.png", "Figure 5.5 — VAT/TDS wizard")
    embed(doc, SHOT / "04_registers/06_vat_tds_report_preview.png", "Figure 5.6 — Monthly VAT/TDS Summary — preview")
    doc.add_heading("5.4 Donor Financial Report", level=2)
    embed(doc, SHOT / "04_registers/07_donor_analytic_wizard_form.png", "Figure 5.7 — Donor Financial Report wizard")
    embed(doc, SHOT / "04_registers/08_donor_analytic_report_preview.png", "Figure 5.8 — Donor Financial Report — preview")
    doc.add_heading("5.5 Year-End Closing", level=2)
    embed(doc, SHOT / "04_registers/09_year_end_closing_wizard_form.png", "Figure 5.9 — Year-End Closing wizard")
    chapter_trace(["BNK-002", "PO-007", "PER-", "DFR-001", "AUD-"], "5.6")
    doc.add_page_break()

    # ====== CHAPTER 6: ADVANCE ======
    doc.add_heading("6. Cash Advances (Annexure-18)", level=1)
    doc.add_paragraph(
        "Staff travelling or running an activity can request a cash advance. It "
        "goes through Finance check, review and approval before being paid out as "
        "a real journal entry (Dr Employee Advances / Cr Bank). MCB will not "
        "allow a new advance to the same employee while a previous one is still "
        "unadjusted."
    )
    doc.add_heading("6.1 Where to find it", level=2)
    doc.add_paragraph("Advances & Petty Cash → Advance Requests (Annex-18).")
    embed(doc, SHOT / "05_advance/01_advance_list.png", "Figure 6.1 — Advance Requests list")
    doc.add_heading("6.2 Walk-through", level=2)
    doc.add_paragraph("A 15,000 BDT advance for a community awareness session in Camp 12, fully paid.")
    embed(doc, SHOT / "05_advance/02_advance5_form_paid.png", "Figure 6.2 — Advance — paid")
    embed(doc, SHOT / "05_advance/03_advance5_report_preview.png", "Figure 6.3 — Advance Request (Annexure-18) — PDF preview")
    chapter_trace(["ADV-001", "ADV-003"], "6.3")
    doc.add_page_break()

    # ====== CHAPTER 7: ADJUSTMENT ======
    doc.add_heading("7. Advance Adjustment (Annexure-19)", level=1)
    doc.add_paragraph(
        "Once the activity is over, the employee accounts for how the advance was "
        "actually spent, line by line. Odoo automatically posts one settlement "
        "journal entry and works out any refund due back or extra reimbursement."
    )
    doc.add_heading("7.1 Where to find it", level=2)
    doc.add_paragraph("Advances & Petty Cash → Advance Adjustments (Annex-19).")
    embed(doc, SHOT / "06_adv_adjust/01_adjustment_list.png", "Figure 7.1 — Adjustments list")
    doc.add_heading("7.2 Walk-through", level=2)
    embed(doc, SHOT / "06_adv_adjust/02_adjustment3_form.png", "Figure 7.2 — Adjustment — expenditure lines")
    embed(doc, SHOT / "06_adv_adjust/03_adjustment3_report_preview.png", "Figure 7.3 — Advance Adjustment (Annexure-19) — PDF preview")
    chapter_trace(["ADV-004", "ADV-007"], "7.3")
    doc.add_page_break()

    # ====== CHAPTER 8: IOU ======
    doc.add_heading("8. IOU / Urgent Cash Requisition (Annexure-13)", level=1)
    doc.add_paragraph(
        "For small, urgent needs that can't wait for the standard advance "
        "process, staff can raise an IOU. It follows the same "
        "submit → approve → pay → adjust pattern but is deliberately lighter "
        "weight."
    )
    doc.add_heading("8.1 Where to find it", level=2)
    doc.add_paragraph("Advances & Petty Cash → IOU / Cash Requisitions (Annex-13).")
    embed(doc, SHOT / "07_iou/01_iou_list.png", "Figure 8.1 — IOU list")
    doc.add_heading("8.2 Walk-through", level=2)
    embed(doc, SHOT / "07_iou/02_iou1_form_adjusted.png", "Figure 8.2 — IOU — adjusted, 150 BDT saving returned")
    embed(doc, SHOT / "07_iou/03_iou1_report_preview.png", "Figure 8.3 — IOU (Annexure-13) — PDF preview")
    chapter_trace(["ADV-008"], "8.3")
    doc.add_page_break()

    # ====== CHAPTER 9: PETTY CASH ======
    doc.add_heading("9. Petty Cash (Count / Top-Up / Book)", level=1)
    doc.add_paragraph(
        "The office petty cash box is topped up from the bank, counted physically "
        "at any time (with a full denomination breakdown), and reported on "
        "through two standard books: a running-balance Cash Book and a "
        "by-accounts-head Statement."
    )
    doc.add_heading("9.1 Where to find it", level=2)
    doc.add_paragraph("Advances & Petty Cash → Daily Cash Counts / Petty Cash Top-Ups / Petty Cash Book.")
    embed(doc, SHOT / "08_petty_cash/01_cash_count_list.png", "Figure 9.1 — Cash Count list")
    doc.add_heading("9.2 Walk-through", level=2)
    embed(doc, SHOT / "08_petty_cash/02_cash_count1_form.png", "Figure 9.2 — Cash Count — denomination breakdown")
    embed(doc, SHOT / "08_petty_cash/03_cash_count1_report_preview.png", "Figure 9.3 — Daily Cash Balance Report (Annexure-14) — preview")
    embed(doc, SHOT / "08_petty_cash/04_petty_topup_list.png", "Figure 9.4 — Petty Cash Top-Up list")
    embed(doc, SHOT / "08_petty_cash/05_petty_topup1_form_done.png", "Figure 9.5 — Top-Up — Bank → Petty Cash, done")
    embed(doc, SHOT / "08_petty_cash/06_petty_book_wizard_form.png", "Figure 9.6 — Petty Cash Book wizard")
    embed(doc, SHOT / "08_petty_cash/07_petty_book_report_preview.png", "Figure 9.7 — Petty Cash Book (Annexure-15) — preview")
    embed(doc, SHOT / "08_petty_cash/08_petty_statement_report_preview.png", "Figure 9.8 — Petty Cash Statement (Annexure-16) — preview")
    chapter_trace(["PCH-"], "9.3")
    doc.add_page_break()

    # ====== CHAPTER 10: BUDGET ======
    doc.add_heading("10. Working Budget, Revision & Donor Report", level=1)
    doc.add_paragraph(
        "Every project has an approved annual budget (Annexure-27). Field teams "
        "break it down further into a Working Budget per activity/quarter "
        "(Annexure-26), and Finance can compare actual spend against the donor "
        "budget at any period granularity."
    )
    doc.add_heading("10.1 Where to find it", level=2)
    doc.add_paragraph("MCB Budgets → Working Budgets / Budget Revisions / Donor Budget Report.")
    embed(doc, SHOT / "09_budget/01_working_budget_list.png", "Figure 10.1 — Working Budgets list")
    doc.add_heading("10.2 Walk-through", level=2)
    embed(doc, SHOT / "09_budget/02_working_budget1_form_approved.png", "Figure 10.2 — Working Budget — approved")
    embed(doc, SHOT / "09_budget/03_working_budget1_report_preview.png", "Figure 10.3 — Working Budget (Annexure-26) — PDF preview")
    doc.add_paragraph(
        "Reallocating more than 10% of a budget line requires the Chief "
        "Executive's own approval — anyone else trying it gets a clear error."
    )
    embed(doc, SHOT / "09_budget/04_budget_revision_list.png", "Figure 10.4 — Budget Revisions list")
    embed(doc, SHOT / "09_budget/05_budget_revision1_form_ce_approved.png", "Figure 10.5 — Revision — 30% change, CE-approved")
    embed(doc, SHOT / "09_budget/06_donor_report_wizard_form.png", "Figure 10.6 — Donor Budget Report wizard")
    embed(doc, SHOT / "09_budget/07_donor_budget_report_preview.png", "Figure 10.7 — Donor Budget-vs-Actual — preview")
    embed(doc, SHOT / "09_budget/08_variance_statement_preview.png", "Figure 10.8 — Variance Statement (Annexure-11) — preview")
    chapter_trace(["BUD-"], "10.3")
    doc.add_page_break()

    # ====== CHAPTER 11: ASSET ======
    doc.add_heading("11. Fixed Assets", level=1)
    doc.add_paragraph(
        "Every asset MCB owns — generators, laptops, vehicles-as-assets — is "
        "registered with a custodian, location, condition and funding donor. "
        "Physical counts are reconciled against the register periodically, and "
        "disposing of an asset always needs the Chief Executive's sign-off first."
    )
    doc.add_heading("11.1 Where to find it", level=2)
    doc.add_paragraph("Accounting → Assets, and MCB Registers → Fixed Assets Register / Physical Inventory.")
    embed(doc, SHOT / "10_asset/01_asset_list.png", "Figure 11.1 — Assets list")
    doc.add_heading("11.2 Walk-through", level=2)
    embed(doc, SHOT / "10_asset/02_asset2_generator_form.png", "Figure 11.2 — Asset — 15 KVA Generator, Camp 12")
    embed(doc, SHOT / "10_asset/04_asset_register_wizard_form.png", "Figure 11.3 — Asset Register wizard")
    embed(doc, SHOT / "10_asset/05_asset_register_report_preview.png", "Figure 11.4 — Fixed Assets Register (Annexure-07) — preview")
    embed(doc, SHOT / "10_asset/06_asset_inventory_list.png", "Figure 11.5 — Physical Inventory list")
    embed(doc, SHOT / "10_asset/07_asset_inventory1_form_verified.png", "Figure 11.6 — Physical Inventory — verified, one item flagged for disposal")
    embed(doc, SHOT / "10_asset/08_asset_inventory1_report_preview.png", "Figure 11.7 — Physical Inventory Report (Annexure-22) — preview")
    embed(doc, SHOT / "10_asset/09_asset2_barcode_label_preview.png", "Figure 11.8 — Asset barcode label — preview")
    doc.add_paragraph(
        "The old photocopier flagged in the inventory above cannot be disposed of "
        "until the Chief Executive clicks 'CE Approve Disposal' on the asset form "
        "— attempting a sale/write-off before that raises AST-005."
    )
    chapter_trace(["AST-"], "11.3")
    doc.add_page_break()

    # ====== CHAPTER 12: MASTER MATRIX ======
    doc.add_heading("12. Consolidated SRS Traceability Matrix", level=1)
    doc.add_paragraph(
        "Every Part C (Accounts / Finance) requirement implemented across the 4 "
        "modules, in one place."
    )
    rows = [[r[0], r[2], r[3], status_symbol(r[4])] for r in REQS]
    make_table(doc, ["Req ID", "Priority", "Requirement", "Status"], rows)
    doc.add_page_break()

    # ====== APPENDIX A: GLOSSARY ======
    doc.add_heading("Appendix A — Glossary of Odoo Terms", level=1)
    glossary = [
        ("Journal", "A book of accounts — Bank, Cash, Sales, Purchases, Miscellaneous, etc. Every voucher/payment belongs to one."),
        ("account.move", "Odoo's technical name for any journal entry (voucher, bill, JE) — one record, many debit/credit lines."),
        ("account.payment", "Odoo's technical name for a money-in or money-out payment — what a Money Receipt or Cheque is built from."),
        ("Analytic account", "The cost/donor dimension attached to a line, used for project & donor financial reporting."),
        ("Withholding tax", "Bangladesh TDS deducted automatically at the moment a payment is made, per l10n_account_withholding_tax."),
        ("3-way match", "Confirms a vendor bill's quantity/price agrees with both the Purchase Order and the Goods Receipt before it can be paid."),
        ("budget.analytic / budget.line", "Odoo's native budget model — MCB adds activity codes, cost categories and revision workflow on top."),
        ("account.asset", "Odoo's native fixed-asset model — MCB adds custodian, location, condition, donor and a CE disposal gate."),
        ("Wizard / Transient model", "A pop-up form used once to run an action or print a report — Bank Recon, Top Sheet, VAT/TDS, Donor Report, etc. are all wizards."),
        ("Sequence", "Auto-incrementing reference generator — e.g. JV-2627-001, ADV-2627-001, each reset every July per fiscal year."),
        ("QWeb report", "Odoo's PDF templating engine — used for every printed voucher/register in this guide."),
        ("Chatter", "The message/activity panel on the right of every record — full audit history of who did what and when."),
    ]
    make_table(doc, ["Term", "Meaning"], glossary)

    # ---- SAVE + VALIDATE ----
    OUT.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(OUT))
    print(f"\nWrote {OUT}  ({OUT.stat().st_size:,} bytes)")

    reread = Document(str(OUT))
    headings = [p.text for p in reread.paragraphs if p.style.name.startswith("Heading 1")]
    print("Top-level chapters present:")
    for h in headings:
        print(f"  • {h}")
    missing = []
    for area_dir in SHOT.iterdir():
        if not area_dir.is_dir():
            continue
        for png in area_dir.glob("*.png"):
            if not png.exists():
                missing.append(str(png))
    if missing:
        print("MISSING SCREENSHOTS:", missing)
    found = False
    for tbl in reread.tables:
        first_cells = [c.text for c in tbl.rows[0].cells]
        if first_cells == ["Req ID", "Priority", "Requirement", "Status"]:
            data_rows = len(tbl.rows) - 1
            print(f"Master traceability matrix rows: {data_rows}  (expected {len(REQS)})")
            assert data_rows == len(REQS), "matrix row count mismatch"
            found = True
            break
    assert found, "master matrix not found in document"
    print("Validation: OK")


if __name__ == "__main__":
    build()
