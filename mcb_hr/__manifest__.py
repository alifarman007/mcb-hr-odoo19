{
    "name": "MCB HR (Suite)",
    "version": "19.0.1.0.0",
    "category": "Human Resources",
    "summary": "Mukti Cox's Bazar — Umbrella module installing all MCB HR area extensions",
    "description": """
MCB HR Suite
============
Installs the complete Mukti Cox's Bazar HR implementation covering SRS §3 — §9:
Employee, Recruitment, Payroll, Leave, Onboarding, Expense & TA/DA, Separation.
""",
    "author": "MCB ERP Team",
    "license": "LGPL-3",
    "depends": [
        "mcb_hr_employee",
        "mcb_hr_recruitment",
        "mcb_hr_payroll",
        "mcb_hr_holidays",
        "mcb_hr_onboarding",
        "mcb_hr_expense",
        "mcb_hr_separation",
    ],
    "data": [],
    "installable": True,
    "application": True,
    "auto_install": False,
}
