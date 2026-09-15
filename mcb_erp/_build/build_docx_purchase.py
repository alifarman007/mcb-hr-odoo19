"""Build MCB_Purchase_Module_Guide.docx — SRS v3 Part B (Procurement).
Run: /Data/odoo19_enterprise/venv/bin/python _build/build_docx_purchase.py
"""
from pathlib import Path

from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

ROOT = Path("/Data/odoo19_enterprise/custom-addons/mcb_erp/_build")
SHOT = ROOT / "screenshots" / "purchase"
OUT = Path("/Data/odoo19_enterprise/mukticox/MCB_Purchase_Module_Guide.docx")

# =============================================================================
# REQUIREMENT INVENTORY — SRS v3 Part B (Procurement), Table-9 / Table-14
# =============================================================================
REQS = [
    ("PR-001", "Part B", "Must", "Purchase Request captures requester, project/donor, budget head, item lines, deadline, delivery point, contact person/phone",
     "Done", "mcb.purchase.request + mcb.purchase.request.line"),
    ("PR-002", "Part B", "Must", "Budget-balance check against the linked Project Budget line before submission; CE override flag if over",
     "Done", "current_balance compute + budget_override boolean"),
    ("PR-003", "Part B", "Must", "Item lines: name of item, specification, unit, quantity, estimated unit price, auto total",
     "Done", "mcb.purchase.request.line + amount_total compute"),
    ("PR-004", "Part B", "Must", "Note Sheet-1 (CE → PC instruction), Note Sheet-2 (PC minutes), Note Sheet-3 (Award recommendation) as auditable rich-text records",
     "Done", "note1_html / note2_html / note3_html + printed on the PR report"),
    ("PR-005", "Part B", "Must", "Multi-level approval chain: Accounts Officer check → CE approve → sent to Procurement Committee",
     "Done", "statusbar draft → accounts_checked → approved(CE) → sent_pc, with accounts_officer_id/ce_id/pc_incharge_id stamped"),
    ("PR-006", "Part B", "Must", "Table-9 auto-selected procurement method (Direct / RFQ / RFP / IFT-Open Tender) by value band, with minimum-quotations rule and NOAL trigger ≥5,00,000",
     "Done", "_compute_method → procurement_method + min_quotations + noal_required"),
    ("PR-007", "Part B", "Must", "PR reference number auto-generated per fiscal year, e.g. PR: 0001/26-27",
     "Done", "_mcb_fy_sequence_next(\"mcb.purchase.request\", \"PR\")"),
    ("PR-008", "Part B", "Must", "One-step RFQ fan-out to every shortlisted vendor from the approved PR",
     "Done", "mcb.pr.rfq.wizard.action_generate() creates one draft RFQ (purchase.order) per vendor"),
    ("PROC-Opening", "Part B", "Must", "Tender/RFQ Opening Sheet recording which vendors responded, opening date and witnesses",
     "Done", "mcb.opening.sheet + action_fill_bidders/action_done"),
    ("PROC-TA", "Part B", "Must", "Technical Analysis (TA-1 for RFQ/RFP, TA-2 for Tender) — pass/fail per vendor on spec & delivery compliance; gates the Comparative Statement",
     "Done", "mcb.technical.analysis (ta_type) + action_fill_vendors/action_done"),
    ("CS-001", "Part B", "Must", "Comparative Statement lists every technically-qualified vendor's price side by side",
     "Done", "mcb.comparative.statement + mcb.comparative.statement.line"),
    ("CS-002", "Part B", "Must", "Minimum 3 technically-qualified quotations required before a Comparative Statement can be finalised (RFQ/RFP/IFT)",
     "Done", "action_done() validates len(qualified vendors) >= request.min_quotations"),
    ("CS-004", "Part B", "Must", "Automatic 1st/2nd/3rd lowest-bid ranking per line and in total",
     "Done", "_compute_rank on comparative.statement.line"),
    ("CS-005", "Part B", "Must", "Only TA-passed vendors' RFQs can be pulled into the Comparative Statement",
     "Done", "action_fill_vendors() reads technical_analysis_id.passed_vendors()"),
    ("CS-006", "Part B", "Should", "Procurement Committee narrative/recommendation captured as rich text and printed on the CS report",
     "Done", "pc_comment Html field, printed under the vendor comparison table"),
    ("EVAL-001", "Part B", "Must", "Vendor Evaluation scores each qualified vendor on price / quality / delivery / experience and recommends a winner",
     "Done", "mcb.vendor.evaluation + mcb.vendor.evaluation.line (4 weighted sub-scores)"),
    ("PO-001", "Part B", "Must", "Confirming the Evaluation converts the recommended vendor's RFQ into the working Purchase Order; the other vendors' RFQs remain as a losing-bid audit trail",
     "Done", "mcb.vendor.evaluation.action_create_po()"),
    ("PO-002", "Part B", "Must", "Separate reference series for Purchase Order / Contract Order / Work Order",
     "Done", "purchase.order.mcb_po_type selection + matching sequences"),
    ("PO-008", "Part B", "Must", "4-level PO authorization (Checked → Reviewed → Approved) mandatory above the direct-purchase threshold before the PO can be confirmed",
     "Done", "action_mcb_check/review/approve + button_confirm() guard, APPROVAL_THRESHOLD_BDT"),
    ("NOAL-001", "Part B", "Must", "Notification of Award Letter auto-required when the PO value is at/above BDT 5,00,000",
     "Done", "mcb.noal linked from purchase.order.mcb_noal_id, gated by mcb_noal_required"),
    ("NOAL-002", "Part B", "Must", "NOAL letter carries contract price, vendor, and an issue/acknowledge workflow",
     "Done", "mcb.noal: contract_price + action_issue()/action_acknowledge()"),
    ("NOAL-006", "Part B", "Must", "A PO at/above the NOAL threshold is hard-blocked from confirmation until its NOAL is issued",
     "Done", "purchase_order.button_confirm() override raises UserError if noal missing/draft"),
    ("PROC-Checklist", "Part B", "Must", "Annexure-29 Procurement Checklist — a per-PO compliance sign-off before the file is closed",
     "Done", "mcb.procurement.checklist + seeded checklist lines + action_done()"),
    ("RPT-Table14", "Part B", "Should", "Table-14 management reports: PR/Process report (days elapsed per stage), PR Pending, Project-wise, Vendor-wise, Work-Order-wise",
     "Done", "mcb.pr.report.wizard + 4 filtered act_window reports on purchase.order/mcb.purchase.request"),
]


# =============================================================================
# DOCX HELPERS (shared style with the HR / Accounts / Projects guides)
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
    hp.text = "Mukti Cox's Bazar — Purchase / Procurement Module on Odoo 19 Enterprise"
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
    r = sub.add_run("Purchase & Procurement Module on Odoo 19 Enterprise")
    r.bold = True
    r.font.size = Pt(20)
    sub2 = doc.add_paragraph()
    sub2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = sub2.add_run("A Plain-English User Guide — SRS v3, Part B (Procurement)")
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
        ("1", "How Procurement Fits Together (Steps 1–11)"),
        ("2", "Chapter 1 — Purchase Requests & Note Sheets"),
        ("3", "Chapter 2 — Opening Sheet"),
        ("4", "Chapter 3 — Technical Analysis"),
        ("5", "Chapter 4 — Comparative Statement"),
        ("6", "Chapter 5 — Vendor Evaluation"),
        ("7", "Chapter 6 — Notification of Award Letter (NOAL)"),
        ("8", "Chapter 7 — Purchase Order & 4-Level Authorization"),
        ("9", "Chapter 8 — Procurement Checklist (Annexure-29)"),
        ("10", "Chapter 9 — Management Reports (Table-14)"),
        ("11", "Consolidated SRS Traceability Matrix"),
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
        "This guide is written for anyone at Mukti Cox's Bazar (MCB) who requests, "
        "processes, or approves a purchase — Procurement Committee members, Project "
        "Managers, Accounts staff, and the Chief Executive — with no assumption of "
        "prior software experience. It explains, step by step and with a screenshot "
        "for every screen, how MCB's full Table-9 procurement procedure — from a "
        "Purchase Request to a signed Purchase Order — works inside Odoo."
    )
    doc.add_paragraph(
        "Every feature described here traces back to a specific requirement in the "
        "SRS v3 document, Part B (Procurement). The traceability tables at the end "
        "of each chapter, and the consolidated matrix in Chapter 11, show exactly "
        "which requirement each screen satisfies."
    )
    doc.add_heading("Scope & Coverage", level=2)
    total = len(REQS)
    done = sum(1 for r in REQS if r[4] == "Done")
    make_table(doc, ["Metric", "Value"], [
        ("Requirements indexed (SRS v3, Part B)", f"{total}"),
        ("✅ Done", f"{done}"),
        ("Odoo module", "mcb_purchase (depends on native purchase, purchase_stock, purchase_requisition)"),
    ])
    doc.add_paragraph(
        "Everything in this guide was captured directly from a live, running copy "
        "of the system using real (demo) data driven through the actual approval "
        "buttons — nothing here is a mock-up."
    )
    doc.add_page_break()

    # ---- CHAPTER 1: HOW IT FITS TOGETHER ----
    doc.add_heading("1. How Procurement Fits Together", level=1)
    doc.add_paragraph(
        "MCB's Procurement Guidelines (2018) define an 11-step process. Odoo "
        "implements each step as its own screen, chained together by statusbar "
        "buttons so nobody can skip a step by accident."
    )
    make_table(doc, ["Step", "What happens", "Odoo screen"], [
        ("1", "Requester raises a Purchase Request (PR) with item lines and a budget line", "Purchase Requests"),
        ("2", "Accounts Officer checks budget availability", "PR statusbar → Accounts Checked"),
        ("3", "Chief Executive approves the PR and instructs the Procurement Committee (Note Sheet-1)", "PR statusbar → Approved (CE)"),
        ("4", "Procurement Committee opens the RFQ/Tender responses", "Opening Sheet"),
        ("5", "Technical Analysis passes/fails each vendor on specification & delivery", "Technical Analysis (TA-1/TA-2)"),
        ("6", "Comparative Statement ranks the technically-qualified vendors by price", "Comparative Statement"),
        ("7", "Vendor Evaluation scores and recommends a winner", "Vendor Evaluation"),
        ("8", "The recommended vendor's RFQ becomes the working Purchase Order", "Purchase Order (draft)"),
        ("9", "NOAL issued if the value is ≥ BDT 5,00,000", "Notification of Award Letter"),
        ("10", "4-level authorization (Checked → Reviewed → Approved) then PO confirmed", "Purchase Order statusbar"),
        ("11", "Procurement Checklist signed off; management reports available any time", "Checklist + MCB Reports menu"),
    ])
    doc.add_paragraph(
        "Table-9 of the SRS decides which of four procurement methods applies, "
        "purely from the estimated value of the PR:"
    )
    make_table(doc, ["Value band (BDT)", "Method", "Minimum quotations", "NOAL required?"], [
        ("Up to 10,000", "Direct Purchase / Petty Cash", "1 (no competitive quotation needed)", "No"),
        ("10,001 – 2,00,000", "RFQ (Request for Quotation)", "3", "No"),
        ("2,00,001 – 5,00,000", "RFP (Request for Proposal)", "3", "No"),
        ("Above 5,00,000", "IFT / Open Tender", "3", "Yes"),
    ])
    doc.add_paragraph(
        "This guide walks through one real example of each: PR 0005/26-27 (Direct, "
        "8,000 BDT), PR 0001/26-27 (RFP, 300,000 BDT) and PR 0004/26-27 (IFT, "
        "650,000 BDT, NOAL required)."
    )
    doc.add_page_break()

    def chapter_trace(prefix_list, chapter_no):
        rows = [r for r in REQS if r[0].startswith(tuple(prefix_list))]
        body = [[r[0], r[1], r[2], r[3], status_symbol(r[4]), r[5]] for r in rows]
        doc.add_heading(f"{chapter_no} SRS Traceability", level=3)
        make_table(doc, ["Req ID", "SRS §", "Priority", "Requirement", "Status", "Implementation"], body)

    # ====== CHAPTER 2: PURCHASE REQUEST ======
    doc.add_heading("2. Purchase Requests & Note Sheets", level=1)
    doc.add_heading("2.1 What this screen does", level=2)
    doc.add_paragraph(
        "Every purchase at MCB starts here. A Purchase Request (PR) records what is "
        "needed, for which project/donor, and against which budget line. Odoo "
        "automatically works out the correct procurement method from the total "
        "value (Table-9) and blocks submission if the budget line doesn't have "
        "enough balance — unless the Chief Executive overrides it."
    )
    doc.add_heading("2.2 Odoo concepts used here", level=2)
    make_table(doc, ["Concept", "Plain-English meaning"], [
        ("Statusbar", "The row of stage names at the top of the form (Draft → Accounts Checked → ...). Click a button to move forward."),
        ("Computed field", "A value Odoo works out for you — e.g. Procurement Method is computed from the PR's total value."),
        ("One2many", "A list of child rows living inside a parent record — the PR's item lines."),
        ("Sequence", "An auto-numbering generator — every PR gets 'PR: NNNN/YY-YY' automatically."),
    ])
    doc.add_heading("2.3 Where to find it", level=2)
    doc.add_paragraph("MCB Procurement → Purchase Requests (Step 1).")
    embed(doc, SHOT / "00_overview/01_apps_mcb_filtered.png", "Figure 2.1 — MCB apps on the home dashboard")
    doc.add_heading("2.4 Walk-through", level=2)
    doc.add_paragraph("Step 1 — The Purchase Requests list shows every PR, its method, amount and current stage.")
    embed(doc, SHOT / "01_pr/01_pr_list.png", "Figure 2.2 — Purchase Requests list — 3 PRs at 3 different value bands")
    doc.add_paragraph(
        "Step 2 — PR 0001/26-27 (300,000 BDT) sits in the RFP band. Notice the "
        "Method (Table-9), Min Quotations, and NOAL Required fields are all "
        "computed automatically the moment the item total changes."
    )
    embed(doc, SHOT / "01_pr/02_pr1_form_rfp_method.png", "Figure 2.3 — PR 0001/26-27 — RFP method, 3 minimum quotations")
    doc.add_paragraph("Step 3 — The Note Sheet-1 tab holds the CE's written instruction to the Procurement Committee — a permanent, auditable record.")
    embed(doc, SHOT / "01_pr/03_pr1_note_sheet_1.png", "Figure 2.4 — Note Sheet-1 — CE instruction to PC")
    doc.add_paragraph(
        "Step 4 — PR 0004/26-27 (650,000 BDT, GBViE Camp 12 civil works) is above "
        "the NOAL threshold, so Odoo automatically ticks 'Noal Required' and sets "
        "the IFT/Open Tender method."
    )
    embed(doc, SHOT / "01_pr/04_pr4_form_ift_method_noal_required.png", "Figure 2.5 — PR 0004/26-27 — IFT method, NOAL required")
    doc.add_paragraph(
        "Step 5 — PR 0005/26-27 (8,000 BDT) is small enough for Direct Purchase / "
        "Petty Cash — no competitive quotation is demanded, and it only needs CE "
        "approval to proceed."
    )
    embed(doc, SHOT / "01_pr/05_pr5_form_direct_method_small_value.png", "Figure 2.6 — PR 0005/26-27 — Direct Purchase, small value")
    doc.add_paragraph("Step 6 — Any PR can be printed with all three Note Sheets on MCB letterhead.")
    embed(doc, SHOT / "01_pr/06_pr1_report_notesheets_preview.png", "Figure 2.7 — PR report — items + Note Sheet-1 preview")
    chapter_trace(["PR-"], "2.5")
    doc.add_heading("2.6 Files touched", level=3)
    make_table(doc, ["File", "Purpose"], [
        ("mcb_purchase/models/mcb_purchase_request.py", "PR model, Table-9 method compute, budget check, FY sequence"),
        ("mcb_purchase/models/mcb_purchase_request_line.py", "Item lines"),
        ("mcb_purchase/wizard/mcb_pr_rfq_wizard.py", "One-click RFQ fan-out to selected vendors"),
        ("mcb_purchase/reports/pr_reports.xml", "PR + Note Sheets PDF"),
        ("mcb_purchase/views/mcb_purchase_request_views.xml", "PR form/list/menus"),
    ])
    doc.add_page_break()

    # ====== CHAPTER 3: OPENING SHEET ======
    doc.add_heading("3. Opening Sheet", level=1)
    doc.add_paragraph(
        "Once RFQs are sent to vendors, the Procurement Committee formally records "
        "when and how each vendor's quotation was received — this is the tender/RFQ "
        "'opening' event, witnessed and dated."
    )
    doc.add_heading("3.1 Where to find it", level=2)
    doc.add_paragraph("MCB Procurement → Opening Sheets (Step 4).")
    embed(doc, SHOT / "02_opening/01_opening_sheet_list.png", "Figure 3.1 — Opening Sheets list")
    doc.add_heading("3.2 Walk-through", level=2)
    doc.add_paragraph("The 'Fill Bidders' button pulls in every vendor who has an RFQ against this PR; the committee then marks the sheet Done.")
    embed(doc, SHOT / "02_opening/02_opening_sheet_form.png", "Figure 3.2 — Opening Sheet form")
    embed(doc, SHOT / "02_opening/03_opening_sheet_report_preview.png", "Figure 3.3 — Opening Sheet — printable report")
    chapter_trace(["PROC-Opening"], "3.3")
    doc.add_page_break()

    # ====== CHAPTER 4: TECHNICAL ANALYSIS ======
    doc.add_heading("4. Technical Analysis", level=1)
    doc.add_paragraph(
        "Before price is even considered, each vendor's offer is checked against "
        "the specification and delivery requirements. Only vendors marked 'Pass' "
        "here are allowed into the Comparative Statement — this is what stops a "
        "cheaper but non-compliant vendor from winning."
    )
    doc.add_heading("4.1 Where to find it", level=2)
    doc.add_paragraph("MCB Procurement → Technical Analysis (Step 5).")
    embed(doc, SHOT / "03_ta/01_ta_list.png", "Figure 4.1 — Technical Analysis list (TA-1 for RFQ/RFP, TA-2 for Tender)")
    doc.add_heading("4.2 Walk-through", level=2)
    doc.add_paragraph(
        "TA-2 for the 650,000 BDT civil-works PR shows all 3 vendors (a minimum "
        "of 3 is compulsory for IFT) marked Pass on spec and delivery compliance."
    )
    embed(doc, SHOT / "03_ta/02_ta2_form_ift_3vendors.png", "Figure 4.2 — TA-2 — 3 vendors, all Pass")
    embed(doc, SHOT / "03_ta/03_ta2_report_preview.png", "Figure 4.3 — Technical Analysis — printable report")
    chapter_trace(["PROC-TA"], "4.3")
    doc.add_page_break()

    # ====== CHAPTER 5: COMPARATIVE STATEMENT ======
    doc.add_heading("5. Comparative Statement", level=1)
    doc.add_paragraph(
        "The Comparative Statement (CS) is the heart of a transparent tender: every "
        "technically-qualified vendor's price is placed side by side, the system "
        "automatically ranks the 1st/2nd/3rd lowest bidder, and the Procurement "
        "Committee records its recommendation as a narrative that gets printed on "
        "the report."
    )
    doc.add_heading("5.1 Where to find it", level=2)
    doc.add_paragraph("MCB Procurement → Comparative Statements (Step 6).")
    embed(doc, SHOT / "04_cs/01_cs_list.png", "Figure 5.1 — Comparative Statements list")
    doc.add_heading("5.2 Walk-through", level=2)
    doc.add_paragraph(
        "For PR 0001/26-27, the Comparative Statement shows Gemini Furniture as "
        "the lowest, technically-qualified bidder — the PC's narrative explains "
        "why they are recommended."
    )
    embed(doc, SHOT / "04_cs/02_cs1_form_gemini_lowest.png", "Figure 5.2 — Comparative Statement — Gemini Furniture lowest")
    embed(doc, SHOT / "04_cs/03_cs1_report_preview.png", "Figure 5.3 — Comparative Statement — printable report")
    doc.add_paragraph(
        "Odoo will not let the Comparative Statement be marked Done if fewer than "
        "the PR's Min Quotations vendors are technically qualified (CS-002) — this "
        "is what protects MCB from a rushed or under-competed tender."
    )
    chapter_trace(["CS-"], "5.3")
    doc.add_page_break()

    # ====== CHAPTER 6: VENDOR EVALUATION ======
    doc.add_heading("6. Vendor Evaluation", level=1)
    doc.add_paragraph(
        "Each qualified vendor is scored on four weighted criteria — price, "
        "quality, delivery and past experience. The highest total score becomes "
        "the recommended vendor, and confirming the evaluation is what actually "
        "creates the working Purchase Order."
    )
    doc.add_heading("6.1 Where to find it", level=2)
    doc.add_paragraph("MCB Procurement → Evaluations (Step 7).")
    embed(doc, SHOT / "05_eval/01_evaluation_list.png", "Figure 6.1 — Vendor Evaluations list")
    doc.add_heading("6.2 Walk-through", level=2)
    doc.add_paragraph("Gemini Furniture scores highest (87/100) on PR 0001/26-27 and is recommended.")
    embed(doc, SHOT / "05_eval/02_eval1_form_scores.png", "Figure 6.2 — Evaluation scores — Gemini Furniture recommended")
    embed(doc, SHOT / "05_eval/03_eval1_report_preview.png", "Figure 6.3 — Vendor Evaluation — printable report")
    chapter_trace(["EVAL-"], "6.3")
    doc.add_page_break()

    # ====== CHAPTER 7: NOAL ======
    doc.add_heading("7. Notification of Award Letter (NOAL)", level=1)
    doc.add_paragraph(
        "For any award at or above BDT 5,00,000, MCB's procurement rules require "
        "a formal Notification of Award Letter to be issued to the winning vendor "
        "and acknowledged by them, before the Purchase Order can be confirmed. "
        "Odoo enforces this as a hard rule, not a suggestion."
    )
    doc.add_heading("7.1 Where to find it", level=2)
    doc.add_paragraph("MCB Procurement → NOAL (Step 9).")
    embed(doc, SHOT / "06_noal/01_noal_list.png", "Figure 7.1 — NOAL list")
    doc.add_heading("7.2 Walk-through", level=2)
    doc.add_paragraph(
        "PR 0004/26-27's PO (747,500 BDT to BD Builders Ltd) is above the "
        "threshold. Trying to confirm the PO without an issued NOAL is blocked "
        "with the message: \"NOAL-006 — an issued Notification of Award Letter is "
        "required before confirmation.\" Once the NOAL is issued and the vendor's "
        "acknowledgement recorded, the PO can proceed."
    )
    embed(doc, SHOT / "06_noal/02_noal1_form_acknowledged.png", "Figure 7.2 — NOAL — issued and acknowledged")
    embed(doc, SHOT / "06_noal/03_noal1_letter_preview.png", "Figure 7.3 — NOAL letter — printable preview")
    chapter_trace(["NOAL-"], "7.3")
    doc.add_page_break()

    # ====== CHAPTER 8: PURCHASE ORDER ======
    doc.add_heading("8. Purchase Order & 4-Level Authorization", level=1)
    doc.add_paragraph(
        "The Purchase Order (PO) is the legal commitment to the vendor. Above the "
        "direct-purchase threshold, MCB requires it to be Checked, then Reviewed, "
        "then Approved by three separate people before it can be confirmed — a "
        "classic 'maker-checker-approver' control."
    )
    doc.add_heading("8.1 Where to find it", level=2)
    doc.add_paragraph("Purchase → Orders, or the 'RFQs/POs' smart button on any Purchase Request.")
    embed(doc, SHOT / "07_po/01_po_list_all.png", "Figure 8.1 — Purchase Orders list")
    doc.add_heading("8.2 Walk-through", level=2)
    doc.add_paragraph(
        "P00018, the Purchase Order for Gemini Furniture (the recommended vendor "
        "from Chapter 6), is now confirmed. The other two vendors' quotations "
        "(Ready Mat, Modern Furnishing BD) remain visible as draft RFQs — a "
        "complete, honest audit trail of who else quoted."
    )
    embed(doc, SHOT / "07_po/02_po18_gemini_confirmed_form.png", "Figure 8.2 — PO P00018 — confirmed, Gemini Furniture")
    embed(doc, SHOT / "07_po/03_po18_pdf_preview.png", "Figure 8.3 — Purchase Order — PDF preview")
    chapter_trace(["PO-"], "8.3")
    doc.add_page_break()

    # ====== CHAPTER 9: CHECKLIST ======
    doc.add_heading("9. Procurement Checklist (Annexure-29)", level=1)
    doc.add_paragraph(
        "Before a procurement file is considered closed, the Procurement Committee "
        "works through a standard checklist (Annexure-29) confirming every step — "
        "from PR approval to vendor NOAL acknowledgement — actually happened."
    )
    doc.add_heading("9.1 Where to find it", level=2)
    doc.add_paragraph("MCB Procurement → Checklists (Annexure-29).")
    embed(doc, SHOT / "08_checklist/01_checklist_list.png", "Figure 9.1 — Procurement Checklists list")
    doc.add_heading("9.2 Walk-through", level=2)
    embed(doc, SHOT / "08_checklist/02_checklist1_form_all_yes.png", "Figure 9.2 — Checklist — all items confirmed Yes")
    embed(doc, SHOT / "08_checklist/03_checklist1_report_preview.png", "Figure 9.3 — Checklist — printable report")
    chapter_trace(["PROC-Checklist"], "9.3")
    doc.add_page_break()

    # ====== CHAPTER 10: REPORTS ======
    doc.add_heading("10. Management Reports (Table-14)", level=1)
    doc.add_paragraph(
        "The MCB Reports menu gives managers an always-up-to-date view across all "
        "procurement, without needing to open every individual PR."
    )
    doc.add_heading("10.1 Where to find it", level=2)
    doc.add_paragraph("MCB Reports (Step 11).")
    embed(doc, SHOT / "09_reports/01_pr_pending_report.png", "Figure 10.1 — PR Pending Report — what's still open")
    embed(doc, SHOT / "09_reports/02_project_wise_report.png", "Figure 10.2 — Project-wise Procurement")
    embed(doc, SHOT / "09_reports/03_vendor_wise_report.png", "Figure 10.3 — Vendor-wise Report")
    embed(doc, SHOT / "09_reports/04_work_order_wise_report.png", "Figure 10.4 — Work-Order-wise Report")
    doc.add_paragraph(
        "The PR / Process Report (Table-14) adds turnaround-time columns — days "
        "to confirm, days to CE approval, days to PC, days to PO — for spotting "
        "bottlenecks."
    )
    embed(doc, SHOT / "09_reports/05_pr_process_report_wizard_form.png", "Figure 10.5 — PR / Process Report wizard")
    chapter_trace(["RPT-"], "10.2")
    doc.add_page_break()

    # ====== CHAPTER 11: MASTER MATRIX ======
    doc.add_heading("11. Consolidated SRS Traceability Matrix", level=1)
    doc.add_paragraph(
        "Every Part B (Procurement) requirement implemented in the mcb_purchase "
        "module, in one place."
    )
    body = [["Req ID", "Priority", "Requirement", "Status"]]
    rows = [[r[0], r[2], r[3], status_symbol(r[4])] for r in REQS]
    make_table(doc, body[0], rows)
    doc.add_page_break()

    # ====== APPENDIX A: GLOSSARY ======
    doc.add_heading("Appendix A — Glossary of Odoo Terms", level=1)
    glossary = [
        ("RFQ", "Request for Quotation — the draft purchase.order Odoo creates per vendor before it becomes a real order."),
        ("Statusbar", "The row of stage buttons at the top of a form; click to move a record to the next stage."),
        ("Computed field", "A value Odoo calculates automatically from other fields (e.g. procurement method from PR value)."),
        ("Sequence", "Auto-incrementing reference generator, e.g. PR: 0001/26-27."),
        ("Analytic account", "The cost/donor dimension attached to each line, used for donor financial reporting."),
        ("QWeb report", "Odoo's PDF templating engine — used for every printed form in this guide."),
        ("Chatter", "The message/activity panel on the right of every record — full audit history."),
        ("Wizard / Transient model", "A pop-up form used once to run an action or print a report; it doesn't live in a permanent list."),
        ("purchase.order", "Odoo's native Purchase Order model — mcb_purchase adds MCB's authorization levels and NOAL gate on top of it."),
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
