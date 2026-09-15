# -*- coding: utf-8 -*-
"""PAYSLIP — the detailed click path, in strict serial order.

The short payroll flow jumped straight to a finished payslip, which is why it was
hard to follow. This one starts where the money actually comes from (the employee's
contract), walks through the structure and the rules that turn one wage figure into
nine lines, then builds the month's batch, reads the payslip line by line, shows what
changes in a bonus month, and ends with the bank file.

Worked example: Rashedul Karim, wage 42,000 BDT/month, MCB Permanent Monthly.
"""
import sys
sys.path.insert(0, "/Data/odoo19_enterprise/custom-addons/mcb_hr/_build")
from flow_recorder import run_flow  # noqa: E402

EMP = 22                 # Rashedul Karim, MEAL-001
STRUCT = 6               # MCB Permanent Monthly
BATCH_AUG, BATCH_APR = 9, 10
SLIP_AUG, SLIP_APR = 12, 18
R_BASIC, R_HRA, R_GROSS, R_PFEE, R_TAX, R_NET = 73, 74, 77, 80, 83, 84

A_RUN = "hr_payroll.action_hr_payslip_run"
A_SLIP = "hr_payroll.action_view_hr_payslip_month_form"
A_STRUCT = "hr_payroll.action_view_hr_payroll_structure_list_form"
A_RULE = "hr_payroll.action_salary_rule_form"
A_PARAM = "hr_payroll.hr_rule_parameter_action"
A_BANK = "mcb_hr_payroll.action_mcb_bank_transfer_wizard"

ROW = ["tr.o_data_row", ".o_data_row"]
NOTEBOOK = [".o_notebook .nav-link", ".o_notebook"]


def S(slug, headline, instruction, target, role="FINANCE", goto=None, wait=3.2,
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


def L(slug, headline, instruction, target, role="FINANCE", goto="/odoo", wait=3.4):
    return dict(slug=slug, goto=goto, wait=wait, login=("admin", "admin"), role=role,
                headline=headline, instruction=instruction, target=target, click=False)


def rec(action, res_id):
    return f"/odoo/action-{action}/{res_id}"


STEPS = [
    # ============================ PART A — where the salary comes from ======
    L("open_payroll_app", "Open the Payroll app",
      "Everything about salary lives here. Click the Payroll tile.",
      ["a.o_app[href='/odoo/payroll']", "text=Payroll"]),

    S("employee_open", "Open the employee and click the Payroll tab",
      "The salary is not on the payslip — it is on the person. Start here, every time.",
      ["a:has-text('Payroll')", ".o_notebook .nav-link"],
      goto=f"/odoo/employees/{EMP}", wait=4.8, nav=True),

    S("employee_contract", "One number drives the whole payslip",
      "The monthly Wage, and the Structure Type that decides which rules will run.",
      ["div[name='wage']", "[name='wage']", "div[name='structure_type_id']"], wait=3.6,
      note="Rashedul Karim — wage 42,000 BDT, structure type MCB Permanent / Regular."),

    S("structures_list", "Configuration → Salary Structures",
      "MCB has three: Permanent, Project (consolidated) and Support / Driver.",
      [".o_group_header", "tr.o_group_header"] + ROW,
      goto=f"/odoo/action-{A_STRUCT}", wait=4.6,
      note="The employee's structure TYPE decides which of these three is used."),

    S("structure_rules", "Open MCB Permanent Monthly",
      "The rule list. Each line here becomes a line on every payslip using this structure.",
      ROW + [".o_field_x2many_list"], goto=rec(A_STRUCT, STRUCT), wait=4.4),

    S("rule_basic", "The first rule: Basic Salary",
      "Basic is 60% of the contract wage. This is the number every other rule builds on.",
      ["div[name='amount_python_compute']", "[name='amount_python_compute']",
       "div[name='code']"],
      goto=rec(A_RULE, R_BASIC), wait=4.2,
      note="42,000 × 0.60 = 25,200"),

    S("rule_hra", "House Rent is a percentage of Basic",
      "40% of Basic — not of the wage. Get Basic wrong and everything below it is wrong.",
      ["div[name='amount_python_compute']", "[name='amount_python_compute']"],
      goto=rec(A_RULE, R_HRA), wait=4.0,
      note="25,200 × 0.40 = 10,080. Medical is 10% and Conveyance 5% of Basic."),

    S("rule_gross", "Gross adds the four together",
      "Basic + House Rent + Medical + Conveyance. Nothing else is in Gross.",
      ["div[name='amount_python_compute']", "[name='amount_python_compute']"],
      goto=rec(A_RULE, R_GROSS), wait=4.0,
      note="25,200 + 10,080 + 2,520 + 1,260 = 39,060"),

    S("rule_pf", "Provident Fund — the employee's 10%",
      "A deduction, so the formula is negative. The employer's matching 10% is a separate rule.",
      ["div[name='amount_python_compute']", "[name='amount_python_compute']"],
      goto=rec(A_RULE, R_PFEE), wait=4.0),

    S("rule_tax", "Income tax follows the Bangladesh slabs",
      "It annualises the gross, walks the slabs, then divides back to one month.",
      ["div[name='amount_python_compute']", "[name='amount_python_compute']"],
      goto=rec(A_RULE, R_TAX), wait=4.0),

    S("rule_parameters", "Configuration → Rule Parameters",
      "The rates the rules read: PF percentages, the tax slabs, and which months carry a bonus.",
      ROW, goto=f"/odoo/action-{A_PARAM}", wait=4.4,
      note="Change a rate here and every future payslip follows. Never edit the rule code."),

    # ============================ PART B — build the month's batch ==========
    S("batches_list", "Payroll → Pay Runs",
      "One card per month. Employer cost, gross and net are shown on the card itself.",
      [".o_kanban_record"], goto=f"/odoo/action-{A_RUN}", wait=4.8,
      note="Ready → Done → Paid across the right of each card is the month's progress."),

    S("batch_new", "New starts a fresh month",
      "You would name it for the month and set the period. Ours is already made.",
      ["button.o_list_button_add", "button:has-text('New')"], wait=3.2),

    S("batch_open", "Open the August 2026 pay run",
      "Click the card to see the payslips inside it.",
      ["text=MCB Payroll — August 2026", ".o_kanban_record"], wait=4.0, nav=True),

    S("batch_slips", "Six payslips, one per staff member",
      "Grade, donor, employer cost, basic, gross and net — the whole month on one screen.",
      ROW, wait=4.2,
      note="Scan the Net Wage column first. An obviously wrong figure shows up here fastest."),

    S("batch_totals", "The batch totals and the Validate button",
      "Gross 171,400 and net 163,056.49 for the whole batch, with Validate on the right.",
      ["button:has-text('Validate')", ".o_control_panel button"], wait=3.4,
      note="Validate closes the whole run at once — do it only after checking the payslips."),

    # ============================ PART C — read one payslip line by line ====
    S("slip_open", "Open Rashedul Karim's payslip",
      "Now we read a single payslip from top to bottom.",
      ["div[name='employee_id']", "[name='employee_id']"],
      goto=rec(A_SLIP, SLIP_AUG), wait=4.6),

    S("slip_header", "The header tells you which rules will run",
      "Employee, period, contract and — most importantly — the Structure.",
      ["div[name='struct_id']", "[name='struct_id']"], wait=3.4,
      note="Wrong structure here means the wrong rules. Check it before anything else."),

    S("slip_worked_days", "Worked Days — the days being paid for",
      "Days present, and any unpaid leave. This is where absence enters the calculation.",
      ["a:has-text('Worked Days')", ".o_notebook .nav-link"], wait=3.6, nav=True),

    S("slip_worked_days_lines", "What the worked-days table shows",
      "Number of days and the hours behind them, for the period on the header.",
      [".o_field_x2many_list", "table"], wait=3.2),

    S("slip_computation_tab", "Switch to Salary Computation",
      "This is the payslip proper — the nine lines the rules produced.",
      ["a:has-text('Salary Computation')", ".o_notebook .nav-link"], wait=3.6, nav=True),

    S("slip_all_lines", "The whole calculation, in order",
      "Read it downward: earnings first, then Gross, then the deductions, then Net.",
      [".o_field_x2many_list", "table"], wait=4.0,
      note="Basic 25,200 · House Rent 10,080 · Medical 2,520 · Conveyance 1,260 · "
           "Gross 39,060 · PF −2,520 · Tax −572.67 · Net 35,967.33"),

    S("slip_basic_line", "Line 1 — Basic Salary 25,200",
      "60% of the 42,000 wage we saw on the contract at the very beginning.",
      [".o_field_x2many_list", "table"], wait=3.2),

    S("slip_allowances", "Lines 2–4 — the three allowances",
      "House Rent 10,080, Medical 2,520, Conveyance 1,260 — all worked out from Basic.",
      [".o_field_x2many_list", "table"], wait=3.2),

    S("slip_gross_line", "Line 5 — Gross Salary 39,060",
      "The four earnings added up. This is the figure the tax slabs work on.",
      [".o_field_x2many_list", "table"], wait=3.2),

    S("slip_pf_lines", "Lines 6–7 — the two Provident Fund lines",
      "The employee's 10% is taken off the pay. The employer's 10% is MCB's cost, not a deduction.",
      [".o_field_x2many_list", "table"], wait=3.4,
      note="Only the negative one changes what the staff member receives."),

    S("slip_tax_line", "Line 8 — Income tax 572.67",
      "One twelfth of the year's tax, worked out from the annualised gross.",
      [".o_field_x2many_list", "table"], wait=3.2),

    S("slip_net_line", "Line 9 — Net Salary 35,967.33",
      "Gross 39,060, less PF 2,520, less tax 572.67. This is what reaches the bank.",
      [".o_field_x2many_list", "table"], wait=3.4),

    S("slip_print", "Print the payslip",
      "The PDF the staff member receives, on MCB letterhead.",
      ["button:has-text('Print')", ".o_cp_action_menus button"], wait=3.2),

    # ============================ PART D — a month with bonuses =============
    S("slip_april", "Now the same person in April",
      "April carries the Baishakhi bonus and a festival bonus, so two extra lines appear.",
      [".o_field_x2many_list", "table"], goto=rec(A_SLIP, SLIP_APR), wait=4.6,
      note="Festival Bonus 25,200 (one month's Basic) + Baishakhi 5,040 (20% of Basic). "
           "Net rises to 66,207.33 — the deductions do not change."),

    S("slip_april_net", "Why the Net is so different",
      "Same wage, same rules — only the month changed. The bonuses are month-gated.",
      [".o_field_x2many_list", "table"], wait=3.4,
      note="Bonus months are set in Rule Parameters, not written into the rule."),

    # ============================ PART E — finish the month =================
    S("slip_confirm", "Confirm the payslip",
      "Once Finance has checked it, confirm. The accounting entry follows from this.",
      ["button[name='action_payslip_done']", "button:has-text('Confirm')",
       ".o_statusbar_buttons button"], goto=rec(A_SLIP, SLIP_AUG), wait=4.2),

    S("bank_wizard", "Generate the bank disbursement file",
      "Choose the pay run and the transfer date, then Generate.",
      ["div[name='payslip_run_id']", ".modal", "button:has-text('Generate')"],
      goto=f"/odoo/action-{A_BANK}", wait=4.4,
      note="The CSV carries employee code, account number, bank, project, donor and net "
           "amount — one row per person, then a TOTAL row."),

    S("payslips_all", "All payslips, any month",
      "Payroll → Payslips lists every payslip. Filter by month or by employee from here.",
      ROW, goto=f"/odoo/action-{A_SLIP}", wait=4.4),
]

if __name__ == "__main__":
    run_flow("payslip", STEPS)
