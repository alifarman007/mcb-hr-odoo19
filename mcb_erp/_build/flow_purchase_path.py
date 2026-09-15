"""Purchase / Procurement (SRS Part D) click-path flows — 12 tutorials.

Navigation is by URL and the click target is ringed, but the clicks that would
change a record are suppressed (click=False) so the demo data keeps the state
the guide describes and the capture can be re-run any number of times.

All flows run as `admin`. In real life the steps belong to different people —
the requester raises the PR, the Accounts Officer checks the budget, the Chief
Executive approves, the Procurement Committee opens and evaluates the quotations
— and the role badge on every screen says who that is.
"""
import sys
sys.path.insert(0, "/Data/odoo19_enterprise/custom-addons/mcb_hr/_build")
from flow_recorder import run_flow  # noqa: E402

# ---- record ids in the training database --------------------------------
PR_DRAFT = 6        # PR: 0006 hygiene kits — draft, Confirm button visible
PR_CONFIRMED = 7    # PR: 0007 learning centre furniture — Accounts Check visible
PR_ACCOUNTS = 8     # PR: 0008 generator servicing — CE Approve visible
PR_APPROVED = 9     # PR: 0009 solar lights — Send to PC visible
PR_LIVE = 10        # PR: 0010 tube-wells — 3 RFQs out, tools in draft
PR_DONE = 4         # PR: 0004 camp learning centre civil works — IFT, finished
PR_CANCEL = 5       # PR: 0005 stationery — direct purchase, cancelled
PR_FURNITURE = 1    # PR: 0001 office furniture — IFT, finished

OPS_DRAFT, OPS_DONE = 2, 1
TA_DRAFT, TA_DONE = 3, 2
CS_DRAFT, CS_DONE = 3, 2
EV_DRAFT, EV_DONE = 3, 2
NOAL = 1
CHK_DRAFT, CHK_DONE = 2, 1

PO_WINNER = 21      # P00021 BD Builders — NOAL issued, confirmed
RFQ_A, RFQ_B, RFQ_C = 25, 26, 27

# ---- actions ------------------------------------------------------------
A_PR = "mcb_purchase.action_mcb_pr"
A_OPS = "mcb_purchase.action_mcb_opening"
A_TA = "mcb_purchase.action_mcb_ta"
A_CS = "mcb_purchase.action_mcb_cs"
A_EVAL = "mcb_purchase.action_mcb_eval"
A_NOAL = "mcb_purchase.action_mcb_noal"
A_CHK = "mcb_purchase.action_mcb_proc_checklist"
A_PRREP = "mcb_purchase.action_mcb_pr_report_wizard"
A_PENDING = "mcb_purchase.action_mcb_pr_pending"
A_PROJWISE = "mcb_purchase.action_mcb_pr_projectwise"
A_WO = "mcb_purchase.action_mcb_wo_report"
A_VENDORWISE = "mcb_purchase.action_mcb_vendorwise"
A_RFQ = "purchase.purchase_rfq"
A_PO = "purchase.purchase_form_action"
A_VENDORS = "account.res_partner_action_supplier"

PURCHASE = "/odoo/purchase"

ROW = ["tr.o_data_row", ".o_data_row"]
STATUSBAR = ["div.o_statusbar_status", ".o_statusbar_status"]


def S(slug, headline, instruction, target, role, goto=None, wait=3.2, note=""):
    d = dict(slug=slug, headline=headline, instruction=instruction, target=target,
             role=role, wait=wait, click=False)
    if goto:
        d["goto"] = goto
    if note:
        d["note"] = note
    return d


def L(slug, headline, instruction, target, role, goto=PURCHASE, wait=3.6, note=""):
    """First step of a flow — shows the login screen, then lands here."""
    d = dict(slug=slug, goto=goto, wait=wait, login=("admin", "admin"), role=role,
             headline=headline, instruction=instruction, target=target, click=False)
    if note:
        d["note"] = note
    return d


def rec(action, res_id):
    return f"/odoo/action-{action}/{res_id}"


NEW = ["button.o_list_button_add", "button:has-text('New')"]

# ======================================== 1. RAISING A PURCHASE REQUEST ====
F1 = [
    L("open_purchase", "Open the Purchase app",
      "Every purchase MCB makes starts here — nothing is bought without a Purchase Request.",
      ["a.o_app[href='/odoo/purchase']", "text=Purchase"], "PROJECT MANAGER", goto="/odoo"),
    S("pr_menu", "MCB Procurement → Purchase Requests",
      "The list of every request, with its project, its value and where it has reached.",
      ROW, "PROJECT MANAGER", goto=f"/odoo/action-{A_PR}", wait=4.2,
      note="Nothing is ordered from a phone call — the PR is the paper trail (PR-001)."),
    S("pr_new", "Click New to raise one",
      "A new request opens with your name and today's date already filled in.",
      NEW, "PROJECT MANAGER", wait=2.6),
    S("pr_header", "Fill the header: project, donor, budget head",
      "PR-002 — which project pays, which donor funds it, and which budget line it comes off.",
      ["div[name='project_analytic_id']", "[name='project_analytic_id']"],
      "PROJECT MANAGER", goto=rec(A_PR, PR_DRAFT), wait=4.2,
      note="The budget head matters: the system checks the balance before it lets you confirm."),
    S("pr_budget_balance", "Watch the budget balance",
      "Total Budget and Current Balance are pulled from the Annexure-27 budget by themselves.",
      ["div[name='current_balance']", "[name='current_balance']"], "PROJECT MANAGER",
      wait=2.8,
      note="PR-004 — a request bigger than the balance is refused unless the CE overrides it."),
    S("pr_lines", "Add the items (PR-003)",
      "Name of item, specification, unit, quantity, estimated unit price. The total adds itself.",
      ["div[name='line_ids']", ".o_field_x2many_list"], "PROJECT MANAGER", wait=3.0,
      note="Write a real specification — the vendors quote against exactly this wording."),
    S("pr_confirm", "Click Confirm to send it on",
      "The request leaves your desk and goes to Accounts. From here you cannot edit it freely.",
      ["button[name='action_confirm']", "button:has-text('Confirm')"],
      "PROJECT MANAGER", wait=2.6),
]

# ========================================== 2. THE PR APPROVAL CHAIN ======
F2 = [
    L("chain_confirmed", "A confirmed request waits for Accounts",
      "The status bar at the top shows exactly how far the request has travelled.",
      STATUSBAR, "ACCOUNTS OFFICER", goto=rec(A_PR, PR_CONFIRMED), wait=4.2,
      note="Draft → Confirmed → Accounts Checked → Approved (CE) → Sent to PC → In Progress → PO Issued."),
    S("chain_accounts_btn", "Accounts Officer: click Accounts Check",
      "Accounts confirms the budget head is right and the money is actually there.",
      ["button[name='action_accounts_check']", "button:has-text('Accounts Check')"],
      "ACCOUNTS OFFICER", wait=2.8),
    S("chain_ce_ready", "Now it is waiting for the Chief Executive",
      "This request has passed Accounts. Only the CE can move it on.",
      ["button[name='action_ce_approve']", "button:has-text('CE Approve')"],
      "CHIEF EXECUTIVE", goto=rec(A_PR, PR_ACCOUNTS), wait=4.0,
      note="PR-005 — the approval names are stamped on the record, not written on paper."),
    S("chain_approvals_block", "Who approved what, on the record",
      "Accounts Officer, CE and PC In-charge are filled in as each person acts.",
      ["div[name='accounts_officer_id']", "[name='accounts_officer_id']"],
      "CHIEF EXECUTIVE", wait=2.8),
    S("chain_send_pc", "Approved — now send it to the Procurement Committee",
      "The CE has approved. Send to PC hands it over to procurement with Note Sheet-1.",
      ["button[name='action_send_pc']", "button:has-text('Send to PC')"],
      "PROCUREMENT OFFICER", goto=rec(A_PR, PR_APPROVED), wait=4.0),
    S("chain_notesheet", "Note Sheet-1 — the CE's written instruction",
      "PR-006 — the CE's instruction to the Procurement Committee travels with the request.",
      ["div[name='note1_html']", "[name='note1_html']", ".o_notebook"], "PROCUREMENT OFFICER",
      wait=3.0),
]

# ===================================== 3. PROCUREMENT METHOD (TABLE-9) ====
F3 = [
    L("method_list", "Group the requests by method",
      "The method is never chosen by hand — the system reads it off the value.",
      ROW, "PROCUREMENT OFFICER", goto=f"/odoo/action-{A_PR}", wait=4.2,
      note="Table-9: under 10,000 direct · to 2,00,000 RFQ · to 5,00,000 RFP · above that open tender."),
    S("method_direct", "Under 10,000 — direct purchase",
      "Small everyday buying. One quotation is enough, petty cash can pay for it.",
      ["div[name='procurement_method']", "[name='procurement_method']"],
      "PROCUREMENT OFFICER", goto=rec(A_PR, PR_CANCEL), wait=3.6),
    S("method_rfq", "Between 10,000 and 2,00,000 — RFQ",
      "Three written quotations. This request is 1,83,000, so RFQ with 3 quotations.",
      ["div[name='min_quotations']", "[name='min_quotations']"], "PROCUREMENT OFFICER",
      goto=rec(A_PR, PR_CONFIRMED), wait=3.6),
    S("method_rfp", "Between 2,00,001 and 5,00,000 — RFP",
      "A fuller proposal, still three suppliers. 4,08,000 falls here.",
      ["div[name='procurement_method']", "[name='procurement_method']"],
      "PROCUREMENT OFFICER", goto=rec(A_PR, PR_LIVE), wait=3.6),
    S("method_ift", "Above 5,00,000 — open tender, and a NOAL is required",
      "6,50,000 of civil works. Open tender, and the award letter becomes compulsory.",
      ["div[name='noal_required']", "[name='noal_required']"], "PROCUREMENT OFFICER",
      goto=rec(A_PR, PR_DONE), wait=3.8,
      note="NOAL Required = Yes is the system telling you the order cannot be confirmed without it."),
]

# ================================================ 4. SENDING OUT RFQs =====
F4 = [
    L("rfq_pr", "Open the approved request",
      "The Procurement Committee has it. Now the quotations go out.",
      ["button[name='action_create_rfqs']", "button:has-text('Create RFQs')"],
      "PROCUREMENT OFFICER", goto=rec(A_PR, PR_LIVE), wait=4.2),
    S("rfq_count", "The RFQs/POs counter",
      "Three quotations went out from this one request. Click the counter to see them.",
      ["button[name='action_view_orders']", ".oe_stat_button"], "PROCUREMENT OFFICER",
      wait=2.8,
      note="One click makes one draft order per vendor, each carrying the PR's item lines."),
    S("rfq_list", "The three RFQs",
      "Same items, same quantities, three different suppliers — that is what makes them comparable.",
      ROW, "PROCUREMENT OFFICER", goto=f"/odoo/action-{A_RFQ}", wait=4.2),
    S("rfq_one", "Inside one RFQ",
      "The vendor, the items copied from the PR, and the project it is charged to.",
      ["div[name='partner_id']", "[name='partner_id']"], "PROCUREMENT OFFICER",
      goto=rec(A_PO, RFQ_A), wait=4.0),
    S("rfq_link_back", "It remembers where it came from",
      "MCB Procurement → Purchase Request. Every order can be traced back to its request.",
      ["div[name='mcb_pr_id']", "[name='mcb_pr_id']"], "PROCUREMENT OFFICER", wait=3.0,
      note="Scroll down on any order to find the MCB Procurement block."),
]

# =============================================== 5. THE OPENING SHEET =====
F5 = [
    L("ops_list", "MCB Procurement → Opening Sheets",
      "On the opening day the committee opens the sealed quotations together and records them.",
      ROW, "PROCUREMENT COMMITTEE", goto=f"/odoo/action-{A_OPS}", wait=4.2),
    S("ops_open", "Open the sheet for this request",
      "Date and time of opening, and which committee members were present.",
      ["div[name='member_ids']", "[name='member_ids']"], "PROCUREMENT COMMITTEE",
      goto=rec(A_OPS, OPS_DRAFT), wait=4.0,
      note="Who was in the room is part of the record — this is what an auditor checks first."),
    S("ops_fill", "Fill Bidders pulls the quotations in",
      "One line per supplier, with the total each one quoted, straight from their RFQ.",
      ["button[name='action_fill_bidders']", "button:has-text('Fill Bidders')"],
      "PROCUREMENT COMMITTEE", wait=3.0),
    S("ops_lines", "Bidder, quoted total, security money, remarks",
      "Tick the security money and write what the envelope actually looked like.",
      ["div[name='line_ids']", ".o_field_x2many_list"], "PROCUREMENT COMMITTEE", wait=3.2),
    S("ops_done", "Click Record to close the sheet",
      "Once recorded the opening is final — the technical analysis works from these figures.",
      ["button[name='action_done']", "button:has-text('Record')"],
      "PROCUREMENT COMMITTEE", wait=2.8),
]

# ========================================== 6. THE TECHNICAL ANALYSIS =====
F6 = [
    L("ta_list", "MCB Procurement → Technical Analysis",
      "Before anyone looks at price, the committee asks: does this offer meet the specification?",
      ROW, "PROCUREMENT COMMITTEE", goto=f"/odoo/action-{A_TA}", wait=4.2),
    S("ta_open", "TA-1 for a quotation, TA-2 for a tender",
      "Same idea either way — a pass or a fail against the written specification.",
      ["div[name='ta_type']", "[name='ta_type']"], "PROCUREMENT COMMITTEE",
      goto=rec(A_TA, TA_DRAFT), wait=4.0),
    S("ta_lines", "Judge each vendor on specification and delivery",
      "Meets Specifications · Meets Delivery Requirements · Pass or Fail · Remarks.",
      ["div[name='line_ids']", ".o_field_x2many_list"], "PROCUREMENT COMMITTEE", wait=3.4,
      note="Here one supplier failed — the bore depth was below specification. Write the reason down."),
    S("ta_done", "Complete the analysis",
      "From now on only the vendors that passed can appear on the Comparative Statement.",
      ["button[name='action_done']", "button:has-text('Complete')"],
      "PROCUREMENT COMMITTEE", wait=2.8,
      note="CS-005 — the system blocks a failed vendor from being compared on price at all."),
]

# ======================================= 7. THE COMPARATIVE STATEMENT =====
F7 = [
    L("cs_list", "MCB Procurement → Comparative Statements",
      "Now the prices. Side by side, only the offers that passed the technical analysis.",
      ROW, "PROCUREMENT COMMITTEE", goto=f"/odoo/action-{A_CS}", wait=4.2),
    S("cs_open", "Circular date, opening date, evaluation date",
      "The dates prove the process was run in the right order.",
      ["div[name='technical_analysis_id']", "[name='technical_analysis_id']"],
      "PROCUREMENT COMMITTEE", goto=rec(A_CS, CS_DRAFT), wait=4.0),
    S("cs_vendors", "The vendor columns and the bidding position",
      "CS-003 grand total, CS-004 position — 1st, 2nd, 3rd lowest, worked out automatically.",
      ["div[name='vendor_line_ids']", ".o_field_x2many_list"], "PROCUREMENT COMMITTEE",
      wait=3.4,
      note="The failed vendor is simply not here — that is CS-005 doing its job."),
    S("cs_comment", "The committee writes its comment (CS-006)",
      "Why this comparison is fair, and anything unusual about an offer.",
      ["div[name='pc_comment']", "[name='pc_comment']"], "PROCUREMENT COMMITTEE", wait=3.0),
    S("cs_done", "Finalise the statement",
      "Fewer than the minimum number of qualified quotations and the system refuses to finalise.",
      ["button[name='action_done']", "button:has-text('Finalise')"],
      "PROCUREMENT COMMITTEE", wait=2.8),
    S("cs_finished", "A finalised statement, for comparison",
      "This is what one looks like when it is done — ranked, commented and locked.",
      ["div[name='vendor_line_ids']", ".o_field_x2many_list"], "PROCUREMENT COMMITTEE",
      goto=rec(A_CS, CS_DONE), wait=3.6),
]

# ==================================== 8. EVALUATION AND THE AWARD =========
F8 = [
    L("eval_list", "MCB Procurement → Evaluations",
      "The scoring sheet that decides who wins the work.",
      ROW, "PROCUREMENT COMMITTEE", goto=f"/odoo/action-{A_EVAL}", wait=4.2),
    S("eval_open", "Score out of 100",
      "Price 40 · Quality and specification 30 · Delivery 15 · Experience 15.",
      ["div[name='line_ids']", ".o_field_x2many_list"], "PROCUREMENT COMMITTEE",
      goto=rec(A_EVAL, EV_DRAFT), wait=4.2,
      note="Price is only 40 of the 100 — the cheapest offer does not automatically win."),
    S("eval_recommend", "The recommended vendor",
      "Leave it blank and Approve, and the highest total score is picked for you.",
      ["div[name='recommended_vendor_id']", "[name='recommended_vendor_id']"],
      "PROCUREMENT COMMITTEE", wait=3.0),
    S("eval_done", "Approve the evaluation",
      "This is the moment the decision is made, and it is stamped with who made it.",
      ["button[name='action_done']", "button:has-text('Approve')"],
      "PROCUREMENT MANAGER", wait=2.8),
    S("eval_create_po", "Create PO turns the winner into the order",
      "The winning RFQ becomes the purchase order — and if the value demands it, a draft NOAL appears with it.",
      ["button[name='action_create_po']", "button:has-text('Create PO')"],
      "PROCUREMENT MANAGER", goto=rec(A_EVAL, EV_DONE), wait=4.0,
      note="Note Sheet-3 on the request carries the award recommendation to the CE."),
]

# ================================================== 9. THE NOAL ===========
F9 = [
    L("noal_list", "MCB Procurement → NOAL",
      "Above 5,00,000 the winner must be told in writing before any order is confirmed.",
      ROW, "PROCUREMENT OFFICER", goto=f"/odoo/action-{A_NOAL}", wait=4.2),
    S("noal_open", "Vendor, contract price, order",
      "The letter is built from the order — nobody retypes the figures.",
      ["div[name='vendor_id']", "[name='vendor_id']"], "PROCUREMENT OFFICER",
      goto=rec(A_NOAL, NOAL), wait=4.0),
    S("noal_issue", "Issue the letter, then record the acknowledgement",
      "Issued when it goes out; Acknowledged when the vendor signs it back.",
      STATUSBAR, "PROCUREMENT OFFICER", wait=3.0,
      note="NOAL-006 — while the NOAL is still draft, the purchase order simply refuses to confirm."),
    S("noal_print", "Print the award letter",
      "Print → Notification of Award Letter. That is the document the vendor signs.",
      ["button:has-text('Print')", ".o_cp_action_menus button"], "PROCUREMENT OFFICER",
      wait=3.0),
]

# ================================= 10. PURCHASE ORDER & 4-LEVEL SIGN-OFF ==
F10 = [
    L("po_list", "The purchase orders",
      "One order per award. PO, Contract Order or Work Order — the type decides the numbering.",
      ROW, "PROCUREMENT OFFICER", goto=f"/odoo/action-{A_PO}", wait=4.2),
    S("po_draft", "A fresh order waiting to be checked",
      "Check (MCB) is the first of the four signatures. Only a Procurement Officer sees it.",
      ["button[name='action_mcb_check']", "button:has-text('Check')"],
      "PROCUREMENT OFFICER", goto=rec(A_PO, RFQ_A), wait=4.2),
    S("po_mcb_block", "The MCB Procurement block",
      "Order type, PO/CO/WO number, the request, the evaluation, the NOAL, and the three signatures.",
      ["div[name='mcb_po_type']", "[name='mcb_po_type']"], "PROCUREMENT OFFICER", wait=3.2,
      note="Scroll below the order lines — this block is on the main form, not on a tab."),
    S("po_signed", "A fully authorised order",
      "Checked by, Reviewed by, Approved by (CE) — three different people, recorded by the system.",
      ["div[name='mcb_approved_by_id']", "[name='mcb_approved_by_id']"],
      "CHIEF EXECUTIVE", goto=rec(A_PO, PO_WINNER), wait=4.2),
    S("po_confirmed", "Confirm the order",
      "PO-008 — below the four signatures, or without an issued NOAL, Confirm refuses to run.",
      STATUSBAR, "PROCUREMENT OFFICER", wait=3.0,
      note="Deliberately try it early once: the error message tells you exactly what is missing."),
    S("po_print", "Print the order for the vendor",
      "The MCB purchase order format, with the order reference and the project it belongs to.",
      ["button:has-text('Print')", ".o_cp_action_menus button"], "PROCUREMENT OFFICER",
      wait=3.0),
]

# ================================= 11. THE PROCUREMENT CHECKLIST ==========
F11 = [
    L("chk_list", "MCB Procurement → Checklists (Annexure-29)",
      "Before the file is closed, seventeen questions confirm the process was followed.",
      ROW, "PROCUREMENT OFFICER", goto=f"/odoo/action-{A_CHK}", wait=4.2),
    S("chk_open", "The checklist for this request",
      "Every line is a question with a yes, a no and a remark.",
      ["div[name='line_ids']", ".o_field_x2many_list"], "PROCUREMENT OFFICER",
      goto=rec(A_CHK, CHK_DRAFT), wait=4.2,
      note="Was the PR approved? Were three quotations received? Was the CS signed? — all of it."),
    S("chk_verify", "Click Verify when every line is answered",
      "The checklist locks, and the procurement file is complete.",
      ["button[name='action_done']", "button:has-text('Verif')"],
      "PROCUREMENT OFFICER", wait=2.8),
    S("chk_done", "A verified checklist",
      "This is what the auditor asks to see alongside the vouchers.",
      ["div[name='line_ids']", ".o_field_x2many_list"], "PROCUREMENT OFFICER",
      goto=rec(A_CHK, CHK_DONE), wait=3.6),
]

# ======================================== 12. THE PROCUREMENT REPORTS =====
F12 = [
    L("rep_process", "MCB Reports → PR / Process Report",
      "How long each request took at every stage — raised, confirmed, approved, ordered.",
      ["div[name='date_from']", ".modal", "button:has-text('Print')"],
      "PROCUREMENT MANAGER", goto=f"/odoo/action-{A_PRREP}", wait=4.2,
      note="Table-14 — this is the report that shows where procurement is actually getting stuck."),
    S("rep_pending", "PR Pending Report",
      "Everything raised that has not yet turned into an order, grouped by where it is stuck.",
      [".o_group_header", "tr.o_group_header"] + ROW, "PROCUREMENT MANAGER",
      goto=f"/odoo/action-{A_PENDING}", wait=4.6),
    S("rep_projectwise", "Project-wise procurement",
      "What each project has bought, grouped by project — the figure a donor asks for.",
      [".o_pivot", ".o_list_renderer", ".o_content"], "PROCUREMENT MANAGER",
      goto=f"/odoo/action-{A_PROJWISE}", wait=4.4),
    S("rep_wo", "Work Order wise",
      "Only the work orders — civil works and services, separated from goods.",
      [".o_list_renderer", ".o_content"], "PROCUREMENT MANAGER",
      goto=f"/odoo/action-{A_WO}", wait=4.0),
    S("rep_vendorwise", "Vendor-wise procurement",
      "How much business went to each supplier — the check against favouring one vendor.",
      [".o_pivot", ".o_content"], "PROCUREMENT MANAGER",
      goto=f"/odoo/action-{A_VENDORWISE}", wait=4.4),
    S("rep_vendors", "The supplier register",
      "Every vendor with their BIN and TIN, ready for the challan and the return.",
      ROW, "PROCUREMENT MANAGER", goto=f"/odoo/action-{A_VENDORS}", wait=4.2),
]

ALL = [
    ("pur01_request", F1), ("pur02_approval", F2), ("pur03_method", F3),
    ("pur04_rfq", F4), ("pur05_opening", F5), ("pur06_technical", F6),
    ("pur07_comparative", F7), ("pur08_evaluation", F8), ("pur09_noal", F9),
    ("pur10_order", F10), ("pur11_checklist", F11), ("pur12_reports", F12),
]

if __name__ == "__main__":
    only = sys.argv[1:] or None
    for name, steps in ALL:
        if only and name not in only:
            continue
        print(f"\n=== {name.upper()} ===")
        run_flow(name, steps)
