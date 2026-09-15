"""Build MCB_Accounts_Flow_Guides.docx — the click-by-click Accounts guide."""
import sys
from pathlib import Path

sys.path.insert(0, "/Data/odoo19_enterprise/custom-addons/mcb_hr/_build")
sys.path.insert(0, "/Data/odoo19_enterprise/custom-addons/mcb_erp/_build")

import build_flow_docx as D    # noqa: E402
from acc_meta import ACC       # noqa: E402

# who acts in each flow, and where Part B begins (by step number)
EXTRA = {
    "acc01_chart":     ([("Administrator", "Sets up the account codes", "Part A")], {}),
    "acc02_journals":  ([("Administrator", "Configures the journals and numbering", "Part A")], {}),
    "acc03_fiscal_tax": ([("Administrator", "Sets the financial year and tax rates", "Part A")], {}),
    "acc04_partners":  ([("Accounts Officer", "Records BIN and TIN on vendors and donors", "Part A")], {}),
    "acc05_voucher":   ([("Accounts Officer", "Prepares the voucher", "Part A"),
                         ("Finance Manager", "Checks and reviews it", "Part B"),
                         ("Chief Executive", "Gives the final approval", "Part B")],
                        {6: "PART B — Approval and posting"}),
    "acc06_receipt":   ([("Accounts Officer", "Records the donor receipt", "Part A"),
                         ("Accounts Officer", "Prints the money receipt", "Part B")],
                        {6: "PART B — Printing the money receipt"}),
    "acc07_payment":   ([("Accounts Officer", "Records the cheque payment", "Part A"),
                         ("Finance Manager", "Signs off the payment checklist", "Part B")],
                        {6: "PART B — The payment checklist"}),
    "acc08_bill":      ([("Accounts Officer", "Enters the vendor bill", "Part A"),
                         ("Finance Manager", "Checks the 3-way match and pays", "Part B")],
                        {6: "PART B — Match and pay"}),
    "acc09_vat_tds":   ([("Accounts Officer", "Records the challan", "Part A"),
                         ("Finance Manager", "Runs the monthly summary", "Part B")],
                        {6: "PART B — Monthly returns"}),
    "acc10_advance":   ([("Accounts Officer", "Raises the advance", "Part A"),
                         ("Finance Manager", "Approves and pays it", "Part A"),
                         ("Accounts Officer", "Settles it afterwards", "Part B")],
                        {6: "PART B — Adjustment and settlement"}),
    "acc11_petty":     ([("Accounts Officer", "IOU and petty cash top-up", "Part A"),
                         ("Accounts Officer", "Counts the cash and prints the book", "Part B")],
                        {7: "PART B — Counting and reporting"}),
    "acc12_budget":    ([("Finance Manager", "Sets the project budget", "Part A"),
                         ("Finance Manager", "Breaks it into working budgets", "Part B")],
                        {6: "PART B — Working budget"}),
    "acc13_revision":  ([("Finance Manager", "Raises the revision", "Part A"),
                         ("Chief Executive", "Approves anything over 10%", "Part A"),
                         ("Finance Manager", "Produces the donor report", "Part B")],
                        {6: "PART B — Donor budget vs actual"}),
    "acc14_assets":    ([("Finance Manager", "Maintains the asset register", "Part A"),
                         ("Finance Manager", "Runs the physical inventory", "Part B"),
                         ("Chief Executive", "Approves any disposal", "Part B")],
                        {7: "PART B — Inventory and disposal"}),
    "acc15_bank":      ([("Finance Manager", "Reconciles the bank", "Part A"),
                         ("Accounts Officer", "Prints the cheque register", "Part B")],
                        {5: "PART B — Cheque register"}),
    "acc16_reports":   ([("Finance Manager", "Reads the financial reports", "Part A"),
                         ("Finance Manager", "Donor report and year-end close", "Part B")],
                        {9: "PART B — Donor report and closing the year"}),
}

D.FLOW_DEFS = []
for key, no, _short, title, summary, outcome, leads in ACC:
    who, parts = EXTRA[key]
    D.FLOW_DEFS.append(dict(
        key=key, title=f"Flow {no} — {title}", summary=summary, who=who,
        logins=[("Accounts / Finance / CE", "admin", "admin")],
        parts=parts or {1: "PART A"}, outcome=outcome, leads=leads,
    ))

D.OUT = Path("/Data/odoo19_enterprise/mukticox/MCB_Accounts_Flow_Guides.docx")
D.HEADER_TEXT = "MCB \u00b7 Accounts — Click-by-Click Flow Guides"
D.DOC_TITLE = "Accounts & Finance — Click-by-Click Flow Guides"
D.DOC_SUB = ("Setting up the books, recording every voucher, and reading the\n"
             "reports back out — screen by screen, click by click.")
D.INTRO_COUNT = "sixteen"

if __name__ == "__main__":
    D.build()
