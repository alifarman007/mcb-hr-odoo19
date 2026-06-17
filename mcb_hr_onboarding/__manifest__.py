{
    "name": "MCB HR — Onboarding",
    "version": "19.0.1.0.0",
    "category": "Human Resources",
    "summary": "Mukti Cox's Bazar — Onboarding plan, probation reminder, progress tracker",
    "description": """
MCB Onboarding
==============
Implements SRS §7 (ONB-001 … ONB-007): auto-create an Onboarding Plan on hire
(tasks for HR, Finance, IT, Line Manager), track mandatory orientations,
issue of ID card / email / equipment, auto-reminder 15 days before probation
ends, PF membership task after 1-year regularization, contract-signing, and a
visual progress bar.
""",
    "author": "MCB ERP Team",
    "license": "LGPL-3",
    "depends": [
        "mcb_hr_employee",
        "hr",
        "mail",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/mail_activity_type_data.xml",
        "data/mail_activity_plan_data.xml",
        "data/ir_cron_data.xml",
        "views/hr_employee_views.xml",
    ],
    "demo": [],
    "installable": True,
    "application": False,
    "auto_install": False,
}
