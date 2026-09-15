"""Project module (SRS Part B) click-path flows — 10 tutorials.

The person on screen is the one the HR videos followed: Rashedul Karim
(MEAL-001), MEAL Officer on the GBViE project in Cox's Bazar, CARE-funded.
Here he does the project side of the job — the work breakdown, his timesheet,
beneficiary data, MEAL indicators and a field trip that needs authorisation.

Navigation is by URL and the click target is ringed, but clicks that would
change a record are suppressed (click=False) so the demo data keeps the state
the guide describes and the capture can be re-run any number of times.
"""
import sys
sys.path.insert(0, "/Data/odoo19_enterprise/custom-addons/mcb_hr/_build")
from flow_recorder import run_flow  # noqa: E402

# ---- record ids in the training database --------------------------------
PROJECT = 10          # GBViE — Gender Based Violence in Emergency
OUTPUT_1 = 83         # Output 1 — case management
ACTIVITY_11 = 84      # Activity 1.1 — the three women-friendly spaces
TASK_SESSIONS = 94    # Hold 60 awareness sessions — 35% done
TASK_KITS = 96        # Procure 300 hygiene kits — 25% done

TAF_DRAFT = 2         # TAF-2627-002 — Submit button visible
TAF_SUBMITTED = 3     # TAF-2627-003 — Finance Review visible
TAF_FINANCE = 4       # TAF-2627-004 — Recommend visible
TAF_RECOMMEND = 5     # TAF-2627-005 — Approve visible
TAF_APPROVED = 1      # TAF-2627-001 — finished

# ---- actions ------------------------------------------------------------
A_PROJECTS = "project.open_view_project_all"
A_TASKS = "project.action_view_all_task"
A_ASSIGN = "mcb_project.action_mcb_assignment"
A_BENEF = "mcb_project.action_mcb_beneficiary"
A_MEAL = "mcb_project.action_mcb_meal"
A_TRAVEL = "mcb_project.action_mcb_travel_auth"
A_QTR = "mcb_project.action_mcb_qtr_wizard"
A_TS_REPORT = "mcb_project.action_mcb_ts_wizard"
A_ATT_REPORT = "mcb_project.action_mcb_att_wizard"
A_ATT_IMPORT = "mcb_project.action_mcb_att_import_wizard"
A_ALLOC = "mcb_project.action_mcb_alloc_wizard"
A_TIMESHEET = "hr_timesheet.timesheet_action_all"
A_MILESTONE = "project.project_milestone_action"
A_BUDGETS = "account_budget.act_budget_analytic_view"

PROJECTS_APP = "/odoo/project"

ROW = ["tr.o_data_row", ".o_data_row"]
KANBAN = [".o_kanban_record", ".o_kanban_renderer"]


def S(slug, headline, instruction, target, role, goto=None, wait=3.2, note="",
      nav=False):
    """nav=True actually performs the click - used to open a tab or a smart
    button, never to change a record."""
    d = dict(slug=slug, headline=headline, instruction=instruction, target=target,
             role=role, wait=wait, click=nav)
    if nav:
        d["after"] = 3.0
    if goto:
        d["goto"] = goto
    if note:
        d["note"] = note
    return d


def L(slug, headline, instruction, target, role, goto=PROJECTS_APP, wait=3.6,
      note="", nav=False):
    d = dict(slug=slug, goto=goto, wait=wait, login=("admin", "admin"), role=role,
             headline=headline, instruction=instruction, target=target, click=nav)
    if nav:
        d["after"] = 3.0
    if note:
        d["note"] = note
    return d


def rec(action, res_id):
    return f"/odoo/action-{action}/{res_id}"


def proj(res_id, sub=""):
    return f"/odoo/project/{res_id}{sub}"


NEW = ["button.o_list_button_add", "button:has-text('New')"]

# =============================================== 1. THE PROJECT PROFILE ===
F1 = [
    L("open_project_app", "Open the Project app",
      "Every donor-funded piece of work MCB runs is a project in here.",
      ["a.o_app[href='/odoo/project']", "text=Project"], "PROJECT MANAGER", goto="/odoo"),
    S("project_kanban", "The projects MCB is running",
      "One card per project. GBViE is the CARE-funded protection project in Ukhiya.",
      KANBAN, "PROJECT MANAGER", goto=f"/odoo/action-{A_PROJECTS}", wait=4.4),
    S("project_form", "Open the project, then click the MCB Profile tab",
      "Description and Settings are Odoo's own. MCB Profile is where the donor contract lives.",
      ["a:has-text('MCB Profile')", "[name='mcb_profile']"], "PROJECT MANAGER",
      goto=rec(A_PROJECTS, PROJECT), wait=4.6, nav=True),
    S("project_profile", "The donor contract (PRJ-001)",
      "Project code, donor, contract number, activity code and the implementation area.",
      ["div[name='mcb_project_code']", "[name='mcb_project_code']"], "PROJECT MANAGER",
      wait=3.2,
      note="Implementation area matters: Camps 4, 12 and 19 plus host community, Ukhiya."),
    S("project_budget_block", "The budget, in both currencies",
      "Total in BDT, the donor's own figure in their currency, and the Annexure-27 budget behind it.",
      ["div[name='mcb_total_budget_bdt']", "[name='mcb_total_budget_bdt']"],
      "PROJECT MANAGER", wait=3.2,
      note="The activity code ties the project to the chart of accounts, so spending lands in the right place."),
    S("project_assignments_inline", "Who is assigned, and for how much of their time",
      "The staff assignment list sits on the same tab - it drives timesheets and payroll costing.",
      ["div[name='mcb_assignment_ids']", "[name='mcb_assignment_ids']"],
      "PROJECT MANAGER", wait=3.2),
]

# ================================= 2. WORK BREAKDOWN: OUTPUT → TASK =======
F2 = [
    L("wbs_kanban", "Open the project's tasks",
      "MCB writes the log-frame straight into the task list: Output, then Activity, then Task.",
      KANBAN, "PROJECT MANAGER", goto=f"/odoo/project/{PROJECT}/tasks", wait=5.0,
      note="The board shows the three Outputs. Everything else hangs underneath them."),
    S("wbs_list_switch", "Switch to the list view",
      "The list is the one to use for a work breakdown — it shows the levels nested.",
      ["button[data-tooltip='List']", ".o_switch_view.o_list", "button[aria-label='List']"],
      "PROJECT MANAGER", wait=3.4, nav=True),
    S("wbs_list", "Three Outputs, with their sub-tasks counted",
      "0/2 sub-tasks means two Activities sit under that Output. Click the arrow to open them.",
      ROW, "PROJECT MANAGER", wait=3.8),
    S("wbs_output", "An Output — the result the donor is buying",
      "Level is set to Output. Everything under it rolls up to this result.",
      ["div[name='mcb_task_level']", "[name='mcb_task_level']"], "PROJECT MANAGER",
      goto=f"/odoo/project/{PROJECT}/tasks/{OUTPUT_1}", wait=4.4),
    S("wbs_activity", "An Activity underneath it",
      "Same form, Level = Activity, and the parent points back at the Output.",
      ["div[name='mcb_progress']", "[name='mcb_progress']"], "PROJECT MANAGER",
      goto=f"/odoo/project/{PROJECT}/tasks/{ACTIVITY_11}", wait=4.2),
    S("wbs_task_progress", "A Task with its % complete",
      "MON-002 — the progress bar the project manager updates, and the Gantt reads.",
      ["div[name='mcb_progress']", "[name='mcb_progress']"], "PROJECT MANAGER",
      goto=f"/odoo/project/{PROJECT}/tasks/{TASK_SESSIONS}", wait=4.2,
      note="Anything outside 0–100 is refused — the system will not take 120% complete."),
    S("wbs_assignee", "Who owns the task",
      "Assign it to a person, give it a deadline, and it appears on their own list.",
      ["div[name='user_ids']", "[name='user_ids']"], "PROJECT MANAGER", wait=3.0),
    S("wbs_blocked", "A task nobody has started",
      "0% and still in Not Started — this is what the quarterly report will flag.",
      ["div[name='mcb_progress']", "[name='mcb_progress']"], "PROJECT MANAGER",
      goto=f"/odoo/project/{PROJECT}/tasks/{TASK_KITS}", wait=4.0),
]

# ================================================== 3. MILESTONES =========
F3 = [
    L("ms_list", "The project's milestones",
      "The handful of dates the donor actually holds MCB to.",
      ROW, "PROJECT MANAGER",
      goto=f"/odoo/project/{PROJECT}/action-{A_MILESTONE}", wait=5.0,
      note="MON-003 — a milestone is a promise to the donor, not an internal to-do. Keep them few."),
    S("ms_reached", "One that has been reached",
      "Tick Reached when it is genuinely done — that tick is what the donor report reads.",
      ["tbody tr.o_data_row:nth-child(1) td:last-child",
       "tbody tr.o_data_row:nth-child(1)"], "PROJECT MANAGER", wait=3.2),
    S("ms_overdue", "One that has slipped",
      "Shown in red: past its deadline and still not reached.",
      ["tbody tr.o_data_row:nth-child(2)"], "PROJECT MANAGER", wait=3.2),
    S("ms_deadline", "The deadline column is what the alert watches",
      "Move a date only with the donor's agreement — moving it silently is how projects drift.",
      ["th:has-text('Deadline')", "tbody tr.o_data_row:nth-child(3)"],
      "PROJECT MANAGER", wait=3.0),
    S("ms_activity", "The overdue alert lands as an activity",
      "Every night a scheduled job puts a To-Do on the project manager for any late milestone.",
      [".o_menu_systray i.fa-clock-o", ".o_activity_summary_cell", ".o_menu_systray"],
      "PROJECT MANAGER", goto="/odoo", wait=4.2,
      note="It is created once per milestone, so the alert does not turn into daily noise."),
]

# =========================================== 4. STAFF ASSIGNMENTS (%) =====
F4 = [
    L("assign_list", "MCB → Staff Assignments (% Time)",
      "Which staff member works on which project, and for what share of their time.",
      ROW, "MEAL OFFICER", goto=f"/odoo/action-{A_ASSIGN}", wait=4.4),
    S("assign_new", "Add an assignment",
      "Employee, project, period, and the percentage of their time.",
      NEW, "PROJECT MANAGER", wait=2.8,
      note="PRJ-005 — the same person cannot be booked more than 100% across overlapping dates."),
    S("assign_rows", "The current allocation",
      "Rashedul is 100% GBViE; others are split across projects.",
      ROW, "PROJECT MANAGER", wait=3.2),
    S("assign_why", "Why the percentage matters",
      "It splits the salary cost between donors, and it pre-fills the daily timesheet.",
      ROW, "FINANCE MANAGER", wait=3.0,
      note="Get this wrong and every donor report afterwards is wrong — it is the cost key."),
]

# ================================================== 5. TIMESHEETS ========
F5 = [
    L("ts_all", "Timesheets - the hours behind the cost",
      "Every hour a staff member charges to a project sits here, week by week.",
      [".o_grid_row_title", ".o_grid_renderer", ".o_grid_view", ".o_content"],
      "MEAL OFFICER", goto=f"/odoo/action-{A_TIMESHEET}", wait=5.0,
      note="TMS-003 — last night's attendance is turned into draft lines, split by the assignment %."),
    S("ts_project_lines", "Switch to the list to see every line",
      "Person, date, task and hours - one row per entry, ready to filter by project.",
      ["button[data-tooltip='List']", ".o_switch_view.o_list", ".o_cp_switch_buttons"],
      "PROJECT MANAGER", wait=3.6, nav=True),
    S("ts_project_rows", "The lines behind the hours",
      "Filter by project and group by employee - this is what the donor is invoiced for.",
      ROW, "PROJECT MANAGER", wait=3.6),
    S("ts_report_wizard", "MCB → Individual Timesheet (Annexure-23)",
      "Pick a staff member and a month, and print their sheet in the MCB format.",
      ["div[name='employee_id']", ".modal", "[name='employee_id']"], "MEAL OFFICER",
      goto=f"/odoo/action-{A_TS_REPORT}", wait=4.2),
    S("ts_report_print", "Print it, or export it to Excel",
      "The PDF is the one the staff member signs; the Excel is for the donor pack.",
      ["button:has-text('Print')", "button:has-text('PDF')", ".modal-footer button"],
      "MEAL OFFICER", wait=3.0),
]

# ======================================== 6. ATTENDANCE (ANNEXURE-20) ====
F6 = [
    L("att_report", "MCB → Monthly Attendance (Annexure-20)",
      "The month's attendance sheet for a department or a field office.",
      ["div[name='month_date']", ".modal", "[name='month_date']"], "HR / ADMIN OFFICER",
      goto=f"/odoo/action-{A_ATT_REPORT}", wait=4.4),
    S("att_fields", "Month, department, project and funder",
      "Project and Funder print on the sheet — the donor wants to see who they paid for.",
      ["div[name='funded_by']", "[name='funded_by']", ".modal"], "HR / ADMIN OFFICER",
      wait=3.2),
    S("att_print", "Print the sheet, or take the Excel",
      "Same figures either way — the PDF for the file, the Excel for the report pack.",
      ["button:has-text('Print')", "button:has-text('XLSX')", ".modal-footer button"],
      "HR / ADMIN OFFICER", wait=3.0),
    S("att_import", "MCB → Camp Attendance Import (ATT-004)",
      "Field staff who sign a paper register in the camp are loaded in from a CSV.",
      ["div[name='file_data']", ".modal", "input[type='file']"], "HR / ADMIN OFFICER",
      goto=f"/odoo/action-{A_ATT_IMPORT}", wait=4.2,
      note="One row per person per day — employee code, date, check-in, check-out."),
]

# ====================================== 7. TRAVEL AUTHORIZATION ==========
F7 = [
    L("taf_list", "MCB → Travel Authorizations (Annexure-30)",
      "Nobody travels on project money without this form approved first.",
      ROW, "MEAL OFFICER", goto=f"/odoo/action-{A_TRAVEL}", wait=4.4),
    S("taf_draft", "Fill it in: where, why, how long, how much",
      "Destination, purpose, dates, transport — and the cost split into travel, lodging, food.",
      ["div[name='destination']", "[name='destination']"], "MEAL OFFICER",
      goto=rec(A_TRAVEL, TAF_DRAFT), wait=4.2),
    S("taf_submit", "Click Submit",
      "It leaves your desk. Total cost is added up for you — you cannot fudge the arithmetic.",
      ["button[name='action_submit']", "button:has-text('Submit')"], "MEAL OFFICER",
      wait=2.8),
    S("taf_finance", "Finance reviews the cost",
      "Accounts check the budget line has cover, and write a comment on the form.",
      ["button[name='action_finance']", "button:has-text('Finance Review')"],
      "ACCOUNTS OFFICER", goto=rec(A_TRAVEL, TAF_SUBMITTED), wait=4.2),
    S("taf_recommend", "The project manager recommends it",
      "Third signature. The manager confirms the trip is actually needed for the project.",
      ["button[name='action_recommend']", "button:has-text('Recommend')"],
      "PROJECT MANAGER", goto=rec(A_TRAVEL, TAF_FINANCE), wait=4.2),
    S("taf_approve", "The Chief Executive approves",
      "Fourth and last signature. Only now is the travel authorised.",
      ["button[name='action_approve']", "button:has-text('Approve')"],
      "CHIEF EXECUTIVE", goto=rec(A_TRAVEL, TAF_RECOMMEND), wait=4.2),
    S("taf_expenses", "Afterwards, the expense claim ties back to it",
      "MOV-004 — the TA/DA claim carries the Travel Authorization number, so the two must agree.",
      ["div[name='expense_ids']", "[name='expense_ids']", ".o_notebook"],
      "MEAL OFFICER", goto=rec(A_TRAVEL, TAF_APPROVED), wait=4.2),
    S("taf_print", "Print (Annexure-30)",
      "The signed form for the file, in MCB's own format.",
      ["button:has-text('Print (Annexure-30)')", "button:has-text('Print')"],
      "MEAL OFFICER", wait=3.0),
]

# ============================== 8. BENEFICIARY DATA & MEAL INDICATORS ====
F8 = [
    L("ben_list", "MCB → Beneficiary Data (MON-005)",
      "How many people were reached, where, and who they were.",
      ROW, "MEAL OFFICER", goto=f"/odoo/action-{A_BENEF}", wait=4.4),
    S("ben_new", "One entry per activity per reporting period",
      "Date, activity, camp or union, direct or indirect — then the disaggregation.",
      NEW, "MEAL OFFICER", wait=2.8),
    S("ben_disagg", "Male, female, other · children, adults, elderly",
      "The total counts itself from male + female + other. Never type the total by hand.",
      ROW, "MEAL OFFICER", wait=3.2,
      note="Direct means MCB served them; indirect means the household or community around them."),
    S("ben_pivot", "The pivot view does the totals for you",
      "Switch to Pivot and group by camp, by month, by type — this is the donor table.",
      [".o_pivot", "button:has-text('Pivot')", ".o_switch_view"], "MEAL OFFICER",
      wait=3.6),
    S("meal_list", "MCB → MEAL Indicators (MON-007)",
      "Each indicator with its target, what has been achieved, and the percentage.",
      ROW, "MEAL OFFICER", goto=f"/odoo/action-{A_MEAL}", wait=4.4),
    S("meal_pct", "Target against achieved",
      "The achievement % is calculated — update the achieved figure, the percentage follows.",
      ROW, "MEAL OFFICER", wait=3.2,
      note="Link each indicator to the activity that produces it, so the numbers can be traced."),
]

# ============================ 9. QUARTERLY REPORT & COST ALLOCATION ======
F9 = [
    L("qtr_wizard", "MCB → Quarterly Report (MON-004)",
      "One button produces the quarter's report for the donor.",
      ["div[name='project_id']", ".modal", "[name='project_id']"], "PROJECT MANAGER",
      goto=f"/odoo/action-{A_QTR}", wait=4.4),
    S("qtr_dates", "Project, and the quarter's dates",
      "The report pulls activities, progress, beneficiaries and indicators for that window.",
      ["div[name='date_from']", "[name='date_from']", ".modal"], "PROJECT MANAGER",
      wait=3.2),
    S("qtr_narrative", "The two boxes you have to write yourself",
      "Key challenges this quarter, and the plan for next quarter. Nothing can generate those.",
      ["div[name='challenges']", "[name='challenges']", ".modal"], "PROJECT MANAGER",
      wait=3.2),
    S("qtr_print", "Print the quarterly report",
      "Progress against target, beneficiaries reached, indicator achievement, your narrative.",
      ["button:has-text('Print')", ".modal-footer button"], "PROJECT MANAGER", wait=3.0),
    S("alloc_wizard", "MCB → Payroll Cost Allocation (TMS-004)",
      "The month's salaries split across projects by the assignment percentages.",
      ["div[name='month_date']", ".modal", "[name='month_date']"], "FINANCE MANAGER",
      goto=f"/odoo/action-{A_ALLOC}", wait=4.4,
      note="This is the entry that puts each donor's share of the salary bill on their project."),
    S("alloc_post", "Post the allocation, or export it first",
      "Export to Excel and check it against the payroll before posting the journal entry.",
      ["button:has-text('Post')", "button:has-text('Export')", ".modal-footer button"],
      "FINANCE MANAGER", wait=3.0),
]

# ============================== 10. BUDGET AND PROJECT CLOSE-OUT =========
F10 = [
    L("close_budget", "The project's budget, and what it has spent",
      "Annexure-27 budget lines with the achieved figure filled in as the money is spent.",
      ROW, "FINANCE MANAGER", goto=f"/odoo/action-{A_BUDGETS}", wait=4.6),
    S("close_tab", "Open the project's MCB Profile tab",
      "The close-out checklist lives with the rest of the donor contract.",
      ["a:has-text('MCB Profile')", "[name='mcb_profile']"], "PROJECT MANAGER",
      goto=rec(A_PROJECTS, PROJECT), wait=4.6, nav=True),
    S("close_checklist", "The close-out checklist (PRJ-007)",
      "Final report submitted, assets handed over, budget reconciled. Three ticks.",
      ["div[name='mcb_closeout_final_report']", "[name='mcb_closeout_final_report']"],
      "PROJECT MANAGER", wait=3.4),
    S("close_blocked", "Try to close out early — on purpose",
      "With a box unticked, Close Out Project refuses and names exactly what is missing.",
      ["button[name='action_mcb_closeout']", "button:has-text('Close Out')"],
      "PROJECT MANAGER", wait=3.2,
      note="This is the control: a project cannot be quietly closed with the assets unaccounted for."),
    S("close_done", "When all three are ticked",
      "The project is marked Closed Out and archived, so it stops appearing in day-to-day lists.",
      ["div[name='mcb_closed_out']", "[name='mcb_closed_out']"], "PROJECT MANAGER",
      wait=3.0),
    S("close_reports", "The project is closed, the record is not",
      "Everything — tasks, timesheets, beneficiaries, indicators, spending — stays available.",
      KANBAN, "PROJECT MANAGER", goto=f"/odoo/action-{A_PROJECTS}", wait=4.0),
]

ALL = [
    ("prj01_profile", F1), ("prj02_breakdown", F2), ("prj03_milestones", F3),
    ("prj04_assignments", F4), ("prj05_timesheets", F5), ("prj06_attendance", F6),
    ("prj07_travel", F7), ("prj08_beneficiaries", F8), ("prj09_quarterly", F9),
    ("prj10_closeout", F10),
]

if __name__ == "__main__":
    only = sys.argv[1:] or None
    for name, steps in ALL:
        if only and name not in only:
            continue
        print(f"\n=== {name.upper()} ===")
        run_flow(name, steps)
