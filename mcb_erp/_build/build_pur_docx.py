"""Build MCB_Purchase_Flow_Guides.docx — the click-by-click procurement guide."""
import sys
from pathlib import Path

sys.path.insert(0, "/Data/odoo19_enterprise/custom-addons/mcb_hr/_build")
sys.path.insert(0, "/Data/odoo19_enterprise/custom-addons/mcb_erp/_build")

import build_flow_docx as D    # noqa: E402
from pur_meta import PUR       # noqa: E402

# who acts in each flow, and where Part B begins (by step number)
EXTRA = {
    "pur01_request":     ([("Requester / Project Manager", "Raises the request", "Part A"),
                           ("Requester / Project Manager", "Adds the items and confirms", "Part B")],
                          {6: "PART B — The items, and confirming"}),
    "pur02_approval":    ([("Accounts Officer", "Checks the budget head", "Part A"),
                           ("Chief Executive", "Approves the request", "Part A"),
                           ("Procurement Officer", "Takes it over from the CE", "Part B")],
                          {6: "PART B — Over to the Procurement Committee"}),
    "pur03_method":      ([("Procurement Officer", "Reads the method off the value", "Part A")], {}),
    "pur04_rfq":         ([("Procurement Officer", "Generates the RFQs", "Part A"),
                           ("Procurement Officer", "Checks one of them", "Part B")],
                          {6: "PART B — Inside a single RFQ"}),
    "pur05_opening":     ([("Procurement Committee", "Records the opening", "Part A")], {}),
    "pur06_technical":   ([("Procurement Committee", "Judges each offer on specification", "Part A")], {}),
    "pur07_comparative": ([("Procurement Committee", "Builds the comparison", "Part A"),
                           ("Procurement Committee", "Comments and finalises", "Part B")],
                          {6: "PART B — Comment and finalise"}),
    "pur08_evaluation":  ([("Procurement Committee", "Scores the vendors", "Part A"),
                           ("Procurement Manager", "Approves and creates the order", "Part B")],
                          {6: "PART B — Approval and award"}),
    "pur09_noal":        ([("Procurement Officer", "Issues the award letter", "Part A")], {}),
    "pur10_order":       ([("Procurement Officer", "Checks the order", "Part A"),
                           ("Procurement Manager", "Reviews it", "Part A"),
                           ("Chief Executive", "Approves, then it can be confirmed", "Part B")],
                          {6: "PART B — Authorised, confirmed and printed"}),
    "pur11_checklist":   ([("Procurement Officer", "Works through Annexure-29", "Part A")], {}),
    "pur12_reports":     ([("Procurement Manager", "Reads the process reports", "Part A"),
                           ("Procurement Manager", "Project, work order and vendor views", "Part B")],
                          {5: "PART B — Where the money went"}),
}

D.FLOW_DEFS = []
for key, no, _short, title, summary, outcome, leads in PUR:
    who, parts = EXTRA[key]
    D.FLOW_DEFS.append(dict(
        key=key, title=f"Flow {no} — {title}", summary=summary, who=who,
        logins=[("Requester / Accounts / CE / PC", "admin", "admin")],
        parts=parts or {1: "PART A"}, outcome=outcome, leads=leads,
    ))

D.OUT = Path("/Data/odoo19_enterprise/mukticox/MCB_Purchase_Flow_Guides.docx")
D.HEADER_TEXT = "MCB · Purchase & Procurement — Click-by-Click Flow Guides"
D.DOC_TITLE = "Purchase & Procurement — Click-by-Click Flow Guides"
D.DOC_SUB = ("From the request on somebody's desk to the signed order and the\n"
             "closed file — screen by screen, click by click.")
D.INTRO_COUNT = "twelve"

if __name__ == "__main__":
    D.build()
