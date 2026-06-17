{
    "name": "MCB HR — Expense & TA/DA",
    "version": "19.0.1.0.0",
    "category": "Human Resources/Expenses",
    "summary": "Mukti Cox's Bazar — TA/DA per diem, approval chain, donor analytic coding",
    "description": """
MCB Expense & TA/DA
===================
Extends Odoo `hr_expense` for SRS §8 (EXP-001 … EXP-007): grade-based per
diem auto-fill (table 14), HoD/CE approval, air-travel restriction, donor
analytic coding and Field Visit (6-hour rule).
""",
    "author": "MCB ERP Team",
    "license": "LGPL-3",
    "depends": [
        "mcb_hr_employee",
        "hr_expense",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/mcb_hr_per_diem_data.xml",
        "data/product_data.xml",
        "views/mcb_hr_per_diem_views.xml",
        "views/hr_expense_views.xml",
        "views/mcb_hr_expense_menus.xml",
    ],
    "demo": [
        "demo/mcb_hr_expense_demo.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
