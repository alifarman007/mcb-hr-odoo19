"""All remaining HR click-path flows.

Navigation is done by URL and the click target is marked, but destructive clicks
are suppressed (click=False) so the demo records stay in the state the guide
describes and the capture can be re-run any number of times.
"""
import sys
sys.path.insert(0, "/Data/odoo19_enterprise/custom-addons/mcb_hr/_build")
from flow_recorder import run_flow  # noqa: E402

REQ, JOB = 1, 12
APPLICANT = 50          # Rashedul Karim
EMP = 22                # employee MEAL-001
EXPENSE = 21
RESIGNATION = 3
PAYSLIP, PAYSLIP_RUN = 7, 4

A_REQ = "mcb_hr_recruitment.action_mcb_requisition"
A_APP = "hr_recruitment.crm_case_categ0_act_job"
A_RESIGN = "mcb_hr_separation.action_mcb_resignation"
A_EXP = "hr_expense.hr_expense_actions_all"
A_RUN = "hr_payroll.action_hr_payslip_run"
A_SLIP = "hr_payroll.action_view_hr_payslip_month_form"


def S(slug, headline, instruction, target, role, goto=None, wait=3.2, note=""):
    d = dict(slug=slug, headline=headline, instruction=instruction,
             target=target, role=role, wait=wait, click=False)
    if goto:
        d["goto"] = goto
    if note:
        d["note"] = note
    return d


# =========================================================== 2. EXPENSE =====
EXPENSE_FLOW = [
    dict(slug="open_expenses", goto="/odoo", wait=3.2, login=("rashedul", "rashedul"),
         role="EMPLOYEE (Rashedul)", headline="Open the Expenses app",
         instruction="You came back from a field visit. Click the Expenses tile.",
         target=["a.o_app[href='/odoo/expenses']", "text=Expenses"]),
    dict(slug="expenses_list", wait=3.4, role="EMPLOYEE (Rashedul)",
         headline="Your expense claims",
         instruction="This is your own list. Click New to start a claim.",
         target=["button.o_list_button_add", "button:has-text('New')"]),
    S("new_expense_form", "Describe the trip",
      "Type what the trip was for — for example 'Camp 12 monitoring field visit'.",
      ["div[name='name'] input", "input#name_0", "div[name='name']"],
      "EMPLOYEE (Rashedul)", wait=3.0),
    S("expense_open_existing", "A completed claim",
      "Here is the finished claim. Notice you never typed the amount yourself.",
      ["div[name='total_amount_currency']", "div[name='total_amount']"],
      "EMPLOYEE (Rashedul)", goto=f"/odoo/action-{A_EXP}/{EXPENSE}", wait=3.4),
    S("expense_tada_fields", "Fill the MCB travel details",
      "Distance in km, overnight stay, field-visit hours. Your grade is already filled in.",
      ["div[name='mcb_distance_km']", "div[name='mcb_grade_id']"],
      "EMPLOYEE (Rashedul)", wait=2.6,
      note="The grade came from the contract — that is what decides your rate."),
    S("expense_apply_perdiem", "Click Apply Per Diem",
      "This one button fills in the correct TA/DA amount from MCB's rate table.",
      ["button[name='action_apply_per_diem']", "button:has-text('Per Diem')"],
      "EMPLOYEE (Rashedul)", wait=2.4),
    S("expense_submit", "Send it to your manager",
      "Click Submit to Manager. The claim leaves your hands.",
      ["button[name='action_submit_expenses']", "button:has-text('Submit')"],
      "EMPLOYEE (Rashedul)", wait=2.4),
    dict(slug="approver_expense_login", goto=f"/odoo/action-{A_EXP}", wait=3.6,
         login=("admin", "admin"), role="APPROVER (HoD)",
         headline="The approver opens Expenses",
         instruction="The head of department signs in and opens the expense list.",
         target=["button:has-text('New')", ".o_list_button_add"], click=False),
    S("approver_expense_open", "Open the claim and check it",
      "Check the trip, the distance and the amount, then approve.",
      ["button[name='action_approve_expense_sheets']", "button:has-text('Approve')",
       "div[name='total_amount_currency']"],
      "APPROVER (HoD)", goto=f"/odoo/action-{A_EXP}/{EXPENSE}", wait=3.4,
      note="Air travel or grade G1–G2 needs the Chief Executive to approve as well."),
]

# ======================================================= 3. REQUISITION =====
REQUISITION_FLOW = [
    dict(slug="open_mcb_hr", goto="/odoo", wait=3.2, login=("admin", "admin"),
         role="PROJECT MANAGER", headline="Open the MCB HR app",
         instruction="You need a new staff member. Click the MCB HR tile.",
         target=["a.o_app[href='/odoo/action-493']", "text=MCB HR"]),
    S("requisition_list", "Go to Staff Requisitions",
      "Recruitment → Staff Requisitions. Click New to raise a request.",
      ["button.o_list_button_add", "button:has-text('New')"],
      "PROJECT MANAGER", goto=f"/odoo/action-{A_REQ}", wait=3.4),
    S("requisition_form", "Fill the requisition",
      "Position, grade, how many vacancies, where they will work, and the project that pays.",
      ["div[name='position_title']", "div[name='position_title'] input"],
      "PROJECT MANAGER", goto=f"/odoo/action-{A_REQ}/{REQ}", wait=3.4,
      note="The project and donor typed here follow this person for their whole career."),
    S("requisition_budget", "Confirm the budget",
      "Tick Budget Confirmed. Without budget the request should not go forward.",
      ["div[name='budget_available']", "input[id^='budget_available']"],
      "PROJECT MANAGER", wait=2.4),
    S("requisition_marks", "Set the marks scheme",
      "Written 50, Computer 20, Oral 30 — MCB's standard for every candidate.",
      ["div[name='marks_written']", "div[name='marks_computer']"],
      "PROJECT MANAGER", wait=2.4),
    S("requisition_statusbar", "Send it for approval",
      "The status bar along the top moves: Project Manager → HR → Chief Executive.",
      ["button:has-text('Submit')", ".o_statusbar_buttons button", ".o_statusbar_status"],
      "PROJECT MANAGER", wait=2.4),
    S("requisition_published", "Approved and published",
      "Once the CE approves you publish it, and the vacancy is open.",
      [".o_statusbar_status", "button:has-text('Published')", ".o_statusbar_buttons button"],
      "CHIEF EXECUTIVE", wait=2.6),
    S("requisition_circular", "Print the Job Circular",
      "The circular is written for you from what you already typed.",
      ["button:has-text('Job Circular')", "button:has-text('Print')"],
      "HR", wait=2.6),
]

# ======================================================= 4. RECRUITMENT =====
RECRUITMENT_FLOW = [
    dict(slug="open_recruitment", goto="/odoo", wait=3.2, login=("admin", "admin"),
         role="RECRUITMENT COMMITTEE", headline="Open the Recruitment app",
         instruction="Applications have arrived. Click the Recruitment tile.",
         target=["a.o_app[href='/odoo/recruitment']", "text=Recruitment"]),
    S("pipeline", "The applicants board",
      "Each card is one candidate. Drag a card to move them to the next stage.",
      [".o_kanban_record", ".o_column_title"],
      "RECRUITMENT COMMITTEE", goto="/odoo/recruitment", wait=4.0),
    S("applicant_list", "See everyone with their marks",
      "Switch to the list to see admit card numbers, total score and merit rank together.",
      ["tr.o_data_row", ".o_data_row"],
      "RECRUITMENT COMMITTEE", goto=f"/odoo/action-{A_APP}", wait=3.6),
    dict(slug="applicant_open", goto=f"/odoo/action-{A_APP}/{APPLICANT}", wait=3.4,
         role="RECRUITMENT COMMITTEE", headline="Open a candidate",
         instruction="This is Rashedul Karim — father's and mother's name, NID, education and experience.",
         target=["div[name='partner_name']", "h1"], click=False,
         then=[lambda pg: pg.get_by_role("tab", name="MCB Recruitment").first.click(timeout=4000)]),
    S("admit_card_btn", "Issue the admit card",
      "One click gives this candidate a unique admit card number and exam details.",
      ["button[name='action_issue_admit_card']", "button:has-text('Admit Card')", "div[name='mcb_admit_card_id']", "[name='mcb_admit_card_id']"],
      "HR", wait=2.6),
    S("enter_marks", "Enter the exam marks",
      "Written out of 50, computer out of 20, then oral: skills 15 + knowledge 15.",
      ["div[name='mcb_written_score']", "[name='mcb_written_score']", "div[name='mcb_total_score']", "[name='mcb_merit_rank']"],
      "RECRUITMENT COMMITTEE", wait=2.6,
      note="Two examiners score the oral separately — that is why it is split in two."),
    S("compute_merit", "Compute the merit rank",
      "The system sorts everyone by total score and numbers them 1, 2, 3…",
      ["button[name='action_compute_merit_rank']", "button:has-text('Merit')"],
      "RECRUITMENT COMMITTEE", wait=2.6),
    S("merit_list", "The merit list",
      "Rashedul Karim is first with 92. This list is your proof the choice was made on marks.",
      ["tr.o_data_row", ".o_data_row"],
      "RECRUITMENT COMMITTEE", goto=f"/odoo/action-{A_APP}", wait=3.6),
]

# ========================================================= 5. ONBOARDING ====
ONBOARDING_FLOW = [
    dict(slug="open_selected_applicant", goto=f"/odoo/action-{A_APP}/{APPLICANT}", wait=3.6,
         login=("admin", "admin"), role="HR",
         headline="Open the selected candidate",
         instruction="The committee picked Rashedul. Now HR turns him into an employee.",
         target=["button:has-text('Create Employee')", "button[name='create_employee_from_applicant']",
                 "div[name='partner_name']"], click=False),
    S("employee_created", "He is now an employee",
      "Everything typed during recruitment has moved across — nothing is re-typed.",
      ["div[name='name']", "h1"],
      "HR", goto=f"/odoo/employees/{EMP}", wait=3.6),
    S("mcb_profile_tab", "Fill the MCB Profile tab",
      "NID, parents, blood group, service dates, probation dates and the PF nominee.",
      ["a:has-text('MCB Profile')", "[name='mcb_nid']"],
      "HR", wait=2.8),
    S("employee_code", "The employee code is generated",
      "MEAL-001 — the project prefix plus a number, created automatically.",
      ["div[name='mcb_employee_code']", "[name='mcb_employee_code']"],
      "HR", wait=2.4),
    S("contract_grade", "Attach the grade and contract",
      "Employment type, grade, project and donor. This drives leave, TA/DA and salary.",
      ["a:has-text('HR Settings')", "div[name='mcb_grade_id']"],
      "HR", wait=2.6,
      note="Set the grade correctly here and every later calculation follows it."),
    S("onboarding_plan", "Launch the orientation plan",
      "Ten mandatory sessions plus ID card, email, bank details and contract signing.",
      ["button:has-text('Activity')", "button:has-text('Plan')", ".o_ActivityBox"],
      "HR", wait=2.8),
]

# ============================================================= 6. PAYROLL ===
PAYROLL_FLOW = [
    dict(slug="open_payroll", goto="/odoo", wait=3.2, login=("admin", "admin"),
         role="FINANCE", headline="Open the Payroll app",
         instruction="It is the end of the month. Click the Payroll tile.",
         target=["a.o_app[href='/odoo/payroll']", "text=Payroll"]),
    S("batches_list", "Go to payslip batches",
      "One batch per month. Click New to create this month's batch.",
      ["button.o_list_button_add", "button:has-text('New')"],
      "FINANCE", goto=f"/odoo/action-{A_RUN}", wait=3.6),
    S("batch_form", "Name the batch and generate payslips",
      "Name it for the month, then generate the payslips for everyone in it.",
      ["button:has-text('Generate')", "div[name='name']", "[name='name'] input", "h1"],
      "FINANCE", goto=f"/odoo/action-{A_RUN}/{PAYSLIP_RUN}", wait=3.6),
    S("open_payslip", "Open one payslip",
      "Every line can be traced to a rule — nothing is a mystery number.",
      ["div[name='employee_id']", "h1"],
      "FINANCE", goto=f"/odoo/action-{A_SLIP}/{PAYSLIP}", wait=3.6),
    S("payslip_lines", "Check the calculation",
      "Basic, PF at 10% + 10%, festival bonus, gratuity, and the Bangladesh tax slabs.",
      ["a:has-text('Salary Computation')", ".o_field_x2many"],
      "FINANCE", wait=2.8),
    S("payslip_confirm", "Confirm the payslip",
      "When Finance is satisfied, confirm it. Then the batch can be paid.",
      ["button[name='action_payslip_done']", "button:has-text('Confirm')"],
      "FINANCE", wait=2.6),
    S("bank_file", "Generate the bank transfer file",
      "One file goes to the bank and pays everyone, with their code, project and donor.",
      ["button:has-text('Bank')", "button:has-text('Transfer')", ".o_statusbar_buttons button", "button.o_form_button_create", "button:has-text('New')"],
      "FINANCE", goto=f"/odoo/action-{A_RUN}/{PAYSLIP_RUN}", wait=3.4),
]

# ========================================================= 7. SEPARATION ====
SEPARATION_FLOW = [
    dict(slug="open_resignations", goto=f"/odoo/action-{A_RESIGN}", wait=3.6,
         login=("admin", "admin"), role="HR",
         headline="Open Resignations",
         instruction="MCB HR → Separation → Resignations. Click New to record one.",
         target=["button.o_list_button_add", "button:has-text('New')"], click=False),
    S("resignation_form", "Record the resignation",
      "Choose the employee, the submission date and the intended last working day.",
      ["div[name='employee_id']", "div[name='intended_last_day']"],
      "HR", goto=f"/odoo/action-{A_RESIGN}/{RESIGNATION}", wait=3.6),
    S("notice_check", "The system checks the notice period",
      "Permanent staff owe 60 days. She gave 20 — so it shows 40 days short, in red.",
      ["div[name='notice_short_by_days']", "div[name='required_notice_days']"],
      "HR", wait=2.6,
      note="60 days permanent · 30 days project · 15 days on probation — applied automatically."),
    S("salary_in_lieu", "Salary in lieu is calculated",
      "Nobody has to look up the rule or argue about the amount.",
      ["div[name='salary_in_lieu']"],
      "HR", wait=2.4),
    S("approval_chain", "Send it through the approvals",
      "Line Manager review, then HR, then the Chief Executive.",
      ["button:has-text('Send to Manager')", ".o_statusbar_buttons button"],
      "HR", wait=2.6),
    S("settlement", "The final settlement adds up",
      "Outstanding salary + leave encashment + provident fund + gratuity − short notice.",
      ["div[name='final_settlement_total']", "div[name='leave_encashment_amount']"],
      "HR", wait=2.6,
      note="PF rule: under 1 year own share only · over 1 year own + MCB's share · "
           "dismissal forfeits the employer share."),
    S("offboarding", "Close the file",
      "Property returned, experience certificate printed, and system access switched off.",
      ["div[name='property_returned']", "div[name='experience_cert_issued']"],
      "HR", wait=2.6),
]

ALL = [
    ("expense", EXPENSE_FLOW),
    ("requisition", REQUISITION_FLOW),
    ("recruitment", RECRUITMENT_FLOW),
    ("onboarding", ONBOARDING_FLOW),
    ("payroll", PAYROLL_FLOW),
    ("separation", SEPARATION_FLOW),
]

if __name__ == "__main__":
    only = sys.argv[1:] or None
    for name, steps in ALL:
        if only and name not in only:
            continue
        print(f"\n=== {name.upper()} ===")
        run_flow(name, steps)
