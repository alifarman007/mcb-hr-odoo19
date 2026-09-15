# -*- coding: utf-8 -*-
"""MCB Logistics click-path flows — 6 tutorials, in the order goods actually move.

Story: one consignment of education materials for the FDMN Education Project —
in-kind from UNICEF, into the head office store, out to the Camp 12 learning
centre, then counted and partly written off.
"""
import sys
sys.path.insert(0, "/Data/odoo19_enterprise/custom-addons/mcb_hr/_build")
from flow_recorder import run_flow  # noqa: E402

GSRN, CHALLAN, PIV, DSP, SRF = 4, 3, 4, 4, 5
CARD_CHALK = 7

A_GSRN = "mcb_logistics.action_mcb_gsrn"
A_CHL = "mcb_logistics.action_mcb_challan"
A_CARD = "mcb_logistics.action_mcb_bin_card"
A_PIV = "mcb_logistics.action_mcb_stock_verification"
A_DSP = "mcb_logistics.action_mcb_stock_disposal"
A_SRF = "mcb_store.action_mcb_srf"
A_WH = "stock.action_warehouse_form"
A_MONTHLY = "mcb_logistics.action_mcb_monthly_stock_wizard"

ROW = ["tr.o_data_row", ".o_data_row"]
INV = "/odoo/inventory"


def S(slug, headline, instruction, target, role="STORE KEEPER", goto=None, wait=3.4,
      note="", nav=False):
    d = dict(slug=slug, headline=headline, instruction=instruction, target=target,
             role=role, wait=wait, click=nav)
    if nav:
        d["after"] = 3.0
    if goto:
        d["goto"] = goto
    if note:
        d["note"] = note
    return d


def L(slug, headline, instruction, target, role="STORE KEEPER", goto="/odoo", wait=3.6):
    return dict(slug=slug, goto=goto, wait=wait, login=("admin", "admin"), role=role,
                headline=headline, instruction=instruction, target=target, click=False)


def rec(a, i):
    return f"/odoo/action-{a}/{i}"


# ===================================================== 1. THE WAREHOUSE ======
F1 = [
    L("open_inventory", "Open the Inventory app",
      "Every store movement lives here. MCB's own documents are under MCB Logistics.",
      ["a.o_app[href='/odoo/inventory']", "text=Inventory"], goto="/odoo"),
    S("wh_list", "Configuration → Warehouses",
      "MCB keeps two stores: the head office store and the Ukhiya field store.",
      ROW, goto=f"/odoo/action-{A_WH}", wait=4.4),
    S("wh_info", "The warehouse information sheet",
      "The SOP asks every warehouse to carry its own record — address, store keeper, "
      "capacity and who the head office focal point is.",
      ["div[name='mcb_storekeeper_id']", "[name='mcb_storekeeper_id']"],
      goto=rec(A_WH, 1), wait=4.4,
      note="Scroll to the MCB Warehouse Information block, below the standard settings."),
    S("wh_layout", "Layout & Storage Plan",
      "Where each purchase order's goods are stacked, and where an arriving lorry can put "
      "its load. Keep it current or the store loses track of its own free space.",
      ["div[name='mcb_layout_plan']", "[name='mcb_layout_plan']"], wait=3.2),
]

# ========================================================== 2. THE GSRN ======
F2 = [
    L("gsrn_menu", "MCB Logistics → Goods & Service Received Notes",
      "Nothing enters an MCB store without a GSRN. It is the document Accounts pays against.",
      ROW, goto=f"/odoo/action-{A_GSRN}", wait=4.6),
    S("gsrn_open", "Open the UNICEF education consignment",
      "The printed pad is a three-part set — one copy each for Accounts, Store and the "
      "Purchaser. This is the same form on screen.",
      ["div[name='source_type']", "[name='source_type']"],
      goto=rec(A_GSRN, GSRN), wait=4.6),
    S("gsrn_source", "Where did the goods come from?",
      "Against a purchase order, or in-kind from a donor, a UN agency or the government. "
      "This consignment came in-kind from UNICEF, so there is no PO — only a reference.",
      ["div[name='reference_no']", "[name='reference_no']", "div[name='donor']"],
      wait=3.4,
      note="In-kind goods still belong to MCB and still go on the register. The SOP is "
           "explicit that donated items are inside its scope."),
    S("gsrn_lines", "Ordered, received, rejected, accepted",
      "The storekeeper types what actually turned up. Two boxes of chalk arrived broken, "
      "so they are rejected — and only the accepted quantity goes into stock.",
      ["div[name='line_ids']", ".o_field_x2many_list"], wait=3.8,
      note="Accepted is worked out for you: received minus rejected. You cannot reject "
           "more than you received — the system refuses."),
    S("gsrn_inspection", "The quality inspection",
      "Accepted in full, partly accepted, or rejected — with the reason. The SOP sends a "
      "copy of this to head office the same day.",
      ["div[name='inspection_result']", "[name='inspection_result']"], wait=3.2),
    S("gsrn_post", "Post to stock",
      "This is the moment the goods become MCB stock and the bin cards are written.",
      ["button[name='action_post']", "button:has-text('Post to Stock')",
       ".o_statusbar_status"], wait=3.4,
      note="Before this the GSRN is only paperwork. After it, the store really holds the "
           "goods and the receipt is done."),
    S("gsrn_print", "Print the GSRN",
      "Print → Goods & Service Received Note. One copy to Accounts, one to the file, one "
      "to the purchaser.",
      ["button:has-text('Print')", ".o_cp_action_menus button"], wait=3.2),
]

# ====================================================== 3. THE BIN CARD ======
F3 = [
    L("card_list", "MCB Logistics → Bin / Stack Cards",
      "One card per item per consignment. The SOP is strict: one bin holds one item from "
      "one purchase order.",
      ROW, goto=f"/odoo/action-{A_CARD}", wait=4.6),
    S("card_open", "The chalk card",
      "Warehouse, page number, PO or donation reference, unit, and the expiry date if the "
      "item has one — exactly the header of the printed card.",
      ["div[name='product_id']", "[name='product_id']"],
      goto=rec(A_CARD, CARD_CHALK), wait=4.4),
    S("card_balances", "Opening, in, out, closing",
      "The card does the arithmetic. Nobody keeps a running total in their head.",
      ["div[name='balance']", "[name='balance']"], wait=3.2),
    S("card_movements", "Every movement, in date order",
      "98 in from the GSRN, 20 out on the challan to Camp 12, 2 written off at the count. "
      "76 left. Each line names the document and the record keeper.",
      ["div[name='line_ids']", ".o_field_x2many_list"], wait=3.8,
      note="This is the line the storekeeper signs on the paper card. On screen the "
           "signature is the record keeper's name, and it cannot be back-dated quietly."),
    S("card_print", "Print the card for the bin",
      "The printed card is fitted to the physical bin so anyone at the rack can see the "
      "same balance the system holds.",
      ["button:has-text('Print')", ".o_cp_action_menus button"], wait=3.2),
]

# ============================================ 4. REQUISITION AND CHALLAN =====
F4 = [
    L("srf_list", "MCB Store → Store Requisitions",
      "Goods leave the store only against an approved requisition. The field raises it.",
      ROW, goto=f"/odoo/action-{A_SRF}", wait=4.6, role="LOGISTICS OFFICER"),
    S("srf_open", "The Camp 12 requisition",
      "What the learning centre asked for, by when, and what they could still see on their "
      "own shelf when they asked.",
      ["div[name='line_ids']", ".o_field_x2many_list"],
      goto=rec(A_SRF, SRF), wait=4.4, role="LOGISTICS OFFICER"),
    S("srf_signatures", "Four signatures, four people",
      "Requested, recommended, reviewed, and the Programme Coordinator. The person who "
      "raised it cannot be the person who approves it.",
      ["div[name='recommended_by_id']", "[name='recommended_by_id']"], wait=3.4,
      role="LOGISTICS OFFICER",
      note="Try approving your own requisition during training. The system names you and "
           "refuses — segregation of duties on store issues."),
    S("chl_list", "MCB Logistics → Materials Supply Notes / Challans",
      "The challan is the issuing document. It certifies that the goods left the store.",
      ROW, goto=f"/odoo/action-{A_CHL}", wait=4.4),
    S("chl_open", "The challan for Camp 12",
      "Who is receiving, for which camp, and against which requisition.",
      ["div[name='recipient_name']", "[name='recipient_name']"],
      goto=rec(A_CHL, CHALLAN), wait=4.4),
    S("chl_carrier", "The carrier block makes it a waybill",
      "Vehicle, driver, packages, weight and final destination. Fill these and the challan "
      "doubles as the waybill the lorry carries.",
      ["div[name='vehicle_no']", "[name='vehicle_no']"], wait=3.4,
      note="Head office rarely uses waybills; the field offices do. It is the same "
           "document either way — the carrier block is what differs."),
    S("chl_folio", "Stock Register Folio",
      "Each issued line records which bin card it came off, so the paper trail runs both "
      "ways: challan to card, card back to challan.",
      ["div[name='line_ids']", ".o_field_x2many_list"], wait=3.4),
    S("chl_delivered", "Delivered — with a name",
      "A challan is not closed until someone at the far end is recorded as having received "
      "the goods. That name is the proof of delivery.",
      ["div[name='received_by_name']", "[name='received_by_name']",
       ".o_statusbar_status"], wait=3.4),
]

# =============================================== 5. THE PHYSICAL COUNT =======
F5 = [
    L("piv_list", "MCB Logistics → Physical Stock Verification",
      "The SOP requires a full count every quarter, another every year, and one whenever "
      "the storekeeper changes.",
      ROW, goto=f"/odoo/action-{A_PIV}", wait=4.6, role="LOGISTICS OFFICER"),
    S("piv_open", "The Q1 count",
      "Type, period, warehouse — and the committee. The SOP names a store keeper, a "
      "warehouse focal point and the Coordinator of Finance & Accounts.",
      ["div[name='storekeeper_id']", "[name='storekeeper_id']"],
      goto=rec(A_PIV, PIV), wait=4.4, role="LOGISTICS OFFICER"),
    S("piv_sheet", "The count sheet",
      "Load Count Sheet fills what the system believes is on hand. The team then walks the "
      "store and types what they actually find.",
      ["div[name='line_ids']", ".o_field_x2many_list"], wait=3.8,
      role="LOGISTICS OFFICER"),
    S("piv_difference", "The line that does not agree",
      "Two boxes of chalk short. The row turns red, and the reason box has to be filled.",
      ["div[name='line_ids']", ".o_field_x2many_list"], wait=3.6,
      role="LOGISTICS OFFICER",
      note="Try to reconcile with the reason blank. The system counts the unexplained "
           "lines and refuses — the SOP says every discrepancy is investigated."),
    S("piv_explain_tab", "Open the Explanation tab",
      "The overall write-up sits on its own tab, next to the count sheet.",
      ["a:has-text('Explanation')", ".o_notebook .nav-link"], wait=3.2,
      role="LOGISTICS OFFICER", nav=True),
    S("piv_explanation", "The written explanation",
      "One overall explanation goes to Senior Management with the count. Without it the "
      "count cannot be submitted.",
      ["div[name='explanation']", "[name='explanation']"], wait=3.4,
      role="LOGISTICS OFFICER"),
    S("piv_submit", "Submit to Management",
      "The count is now on record: what was expected, what was found, and why.",
      ["button[name='action_submit']", ".o_statusbar_status"], wait=3.2,
      role="LOGISTICS OFFICER"),
]

# ============================================ 6. DISPOSAL AND REPORTING ======
F6 = [
    L("dsp_list", "MCB Logistics → Stock Disposal Requests",
      "Damaged or expired stock cannot simply be thrown away. Head office approves first.",
      ROW, goto=f"/odoo/action-{A_DSP}", wait=4.6, role="LOGISTICS MANAGER"),
    S("dsp_open", "The damaged chalk",
      "Raised straight off the count that found it, with the reason and the method of "
      "disposal written down.",
      ["div[name='reason']", "[name='reason']"],
      goto=rec(A_DSP, DSP), wait=4.4, role="LOGISTICS MANAGER"),
    S("dsp_approval", "Approval comes before disposal",
      "Requested, then approved by head office, and only then disposed. The order matters.",
      ["div[name='approved_by_id']", "[name='approved_by_id']", ".o_statusbar_status"],
      wait=3.4, role="LOGISTICS MANAGER",
      note="Press Dispose while the request is still unapproved and the system stops you. "
           "That is the control the SOP asks for."),
    S("dsp_print", "Print the approved disposal list",
      "The SOP says the approved list is printed and filed. This is that print.",
      ["button:has-text('Print')", ".o_cp_action_menus button"], wait=3.2,
      role="LOGISTICS MANAGER"),
    S("monthly_report", "MCB Logistics → Monthly Stock Report",
      "Opening, received, issued, loss, closing and value — per item per consignment, for "
      "the month.",
      ["div[name='month_date']", ".modal", "[name='month_date']"],
      goto=f"/odoo/action-{A_MONTHLY}", wait=4.4, role="LOGISTICS OFFICER"),
    S("monthly_print", "Print it, or take the Excel",
      "The PDF goes in the file; the Excel goes to the donor pack and to Finance for the "
      "monthly reconciliation.",
      ["button:has-text('Print')", "button:has-text('Export')", ".modal-footer button"],
      wait=3.2, role="LOGISTICS OFFICER"),
]

ALL = [
    ("log1_warehouse", F1), ("log2_gsrn", F2), ("log3_bincard", F3),
    ("log4_issue", F4), ("log5_count", F5), ("log6_disposal", F6),
]

if __name__ == "__main__":
    only = sys.argv[1:] or None
    for name, steps in ALL:
        if only and name not in only:
            continue
        print(f"\n=== {name.upper()} ===")
        run_flow(name, steps)
