"""Shared metadata for the 10 Project module tutorials (video + docx)."""

ADMIN = [("Project Manager / MEAL / Finance", "admin", "admin")]

# key, no, short_name, title, summary, outcome, leads
PRJ = [
    ("prj01_profile", 1, "Project_Profile", "The Project Profile (PRJ-001)",
     "Project code, donor, contract number, implementation area and the budget behind it.",
     "A project set up so every later figure knows where it belongs",
     "Flow 2 — breaking the work down into something you can track."),
    ("prj02_breakdown", 2, "Work_Breakdown", "Outputs, Activities and Tasks (PRJ-002)",
     "The log-frame written straight into the task list, with % complete on every line.",
     "The whole project visible as one nested list",
     "Flow 3 — the few dates the donor actually holds you to."),
    ("prj03_milestones", 3, "Milestones", "Milestones & the Overdue Alert (MON-003)",
     "The promises made to the donor, and the alert that fires when one slips.",
     "Slippage that finds you, instead of you finding it late",
     "Flow 4 — who is working on this, and for how much of their time."),
    ("prj04_assignments", 4, "Staff_Assignments", "Staff Assignments — % Time (PRJ-005)",
     "Which staff member works on which project, and the share of their time each donor pays for.",
     "A cost key that no one can book past 100%",
     "Flow 5 — the hours that key is applied to."),
    ("prj05_timesheets", 5, "Timesheets", "Timesheets (TMS) & Annexure-23",
     "The hours behind the cost — entered daily, printed monthly in MCB's own format.",
     "Every hour charged to a project, and a sheet the staff member signs",
     "Flow 6 — attendance, including the camps."),
    ("prj06_attendance", 6, "Attendance", "Monthly Attendance (Annexure-20) & Camp Import",
     "The month's attendance sheet, and loading a camp's paper register from a CSV.",
     "Attendance on the system for office and field staff alike",
     "Flow 7 — before anyone travels on project money."),
    ("prj07_travel", 7, "Travel_Authorization", "Travel Authorization (Annexure-30)",
     "Where, why, how long and how much — through four signatures before the trip happens.",
     "Authorised travel, tied to the expense claim that follows it",
     "Flow 8 — counting the people the project actually reached."),
    ("prj08_beneficiaries", 8, "Beneficiaries_and_MEAL", "Beneficiary Data (MON-005) & MEAL Indicators",
     "Reach disaggregated by sex, age, camp and direct/indirect — and target against achieved.",
     "Donor-ready reach figures that add themselves up",
     "Flow 9 — turning all of it into the quarterly report."),
    ("prj09_quarterly", 9, "Quarterly_and_Allocation", "Quarterly Report (MON-004) & Payroll Cost Allocation",
     "One button for the donor's quarterly report; one more to split the salary bill across projects.",
     "The quarter reported, and each donor charged their true share",
     "Flow 10 — closing the project properly."),
    ("prj10_closeout", 10, "Budget_and_Closeout", "Project Budget & Close-Out (PRJ-007)",
     "Budget against actual, and the three-tick checklist that has to pass before a project can close.",
     "A project closed on evidence, not on someone's say-so",
     "— the project cycle is complete."),
]

META = {k: (no, title, summary, ADMIN) for k, no, _s, title, summary, _o, _l in PRJ}
END = {k: (outcome, leads) for k, _n, _s, _t, _sm, outcome, leads in PRJ}
SHORT = {k: short for k, _n, short, _t, _s, _o, _l in PRJ}
