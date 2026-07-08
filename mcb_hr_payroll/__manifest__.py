{
    "name": "MCB HR — Payroll",
    "version": "19.0.1.0.0",
    "category": "Human Resources/Payroll",
    "summary": "Mukti Cox's Bazar — Salary structures, PF, gratuity, festival bonus, BD income tax",
    "description": """
MCB Payroll
===========
Extends Odoo Enterprise `hr_payroll` for SRS §5 (PAY-001 … PAY-010):
grade-based MCB Permanent / Project / Support structures, PF 10+10,
gratuity 30/45 day accrual, 2× festival bonus, Baishakhi 20% basic,
overtime rule, and Bangladesh income-tax slabs via `hr.rule.parameter`.
""",
    "author": "MCB ERP Team",
    "license": "OEEL-1",
    "depends": [
        "mcb_hr_employee",
        "hr_payroll",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/res_currency_data.xml",
        "data/hr_payroll_structure_type_data.xml",
        "data/hr_payroll_structure_data.xml",
        "data/hr_rule_parameter_data.xml",
        "data/hr_salary_rule_data.xml",
        "data/hr_payslip_input_type_data.xml",
        "reports/mcb_salary_letters.xml",
        "reports/mcb_payroll_sheet.xml",
        "wizard/mcb_hr_salary_revision_views.xml",
        "wizard/mcb_hr_bank_transfer_views.xml",
        "views/hr_payslip_views.xml",
    ],
    "demo": [
        "demo/mcb_hr_payroll_demo.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
