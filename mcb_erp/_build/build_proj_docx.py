"""Build MCB_Project_Flow_Guides.docx — the click-by-click project guide."""
import sys
from pathlib import Path

sys.path.insert(0, "/Data/odoo19_enterprise/custom-addons/mcb_hr/_build")
sys.path.insert(0, "/Data/odoo19_enterprise/custom-addons/mcb_erp/_build")

import build_flow_docx as D    # noqa: E402
from proj_meta import PRJ      # noqa: E402

EXTRA = {
    "prj01_profile":      ([("Project Manager", "Sets up the donor contract", "Part A")], {}),
    "prj02_breakdown":    ([("Project Manager", "Builds the work breakdown", "Part A"),
                            ("Project Manager", "Works on the individual levels", "Part B")],
                           {6: "PART B — Output, Activity and Task, one at a time"}),
    "prj03_milestones":   ([("Project Manager", "Keeps the donor's dates", "Part A")], {}),
    "prj04_assignments":  ([("Project Manager", "Allocates staff time", "Part A")], {}),
    "prj05_timesheets":   ([("MEAL Officer", "Records the hours", "Part A"),
                            ("MEAL Officer", "Prints the monthly sheet", "Part B")],
                           {6: "PART B — The Annexure-23 sheet"}),
    "prj06_attendance":   ([("HR / Admin Officer", "Runs the monthly sheet", "Part A"),
                            ("HR / Admin Officer", "Imports the camp register", "Part B")],
                           {6: "PART B — Camp attendance import"}),
    "prj07_travel":       ([("MEAL Officer", "Raises the travel form", "Part A"),
                            ("Accounts Officer", "Reviews the cost", "Part B"),
                            ("Project Manager", "Recommends the trip", "Part B"),
                            ("Chief Executive", "Approves it", "Part B")],
                           {6: "PART B — Three more signatures"}),
    "prj08_beneficiaries": ([("MEAL Officer", "Records who was reached", "Part A"),
                             ("MEAL Officer", "Keeps the indicators up to date", "Part B")],
                            {7: "PART B — MEAL indicators"}),
    "prj09_quarterly":    ([("Project Manager", "Produces the quarterly report", "Part A"),
                            ("Finance Manager", "Allocates the salary cost", "Part B")],
                           {7: "PART B — Payroll cost allocation"}),
    "prj10_closeout":     ([("Finance Manager", "Checks budget against actual", "Part A"),
                            ("Project Manager", "Works the close-out checklist", "Part B")],
                           {4: "PART B — Closing the project"}),
}

D.FLOW_DEFS = []
for key, no, _short, title, summary, outcome, leads in PRJ:
    who, parts = EXTRA[key]
    D.FLOW_DEFS.append(dict(
        key=key, title=f"Flow {no} — {title}", summary=summary, who=who,
        logins=[("Project Manager / MEAL / Finance", "admin", "admin")],
        parts=parts or {1: "PART A"}, outcome=outcome, leads=leads,
    ))

D.OUT = Path("/Data/odoo19_enterprise/mukticox/MCB_Project_Flow_Guides.docx")
D.HEADER_TEXT = "MCB · Project — Click-by-Click Flow Guides"
D.DOC_TITLE = "Project Management — Click-by-Click Flow Guides"
D.DOC_SUB = ("Setting up a donor project, running it week by week, reporting it\n"
             "and closing it — screen by screen, click by click.")
D.INTRO_COUNT = "ten"

if __name__ == "__main__":
    D.build()
