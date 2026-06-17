{
    "name": "MCB HR — Leave Management",
    "version": "19.0.1.0.0",
    "category": "Human Resources/Time Off",
    "summary": "Mukti Cox's Bazar — Leave types, 2-level approval, BD public holiday calendar",
    "description": """
MCB Leave Management
====================
Extends Odoo `hr_holidays` with the leave types listed in SRS §6 (LVE-001 …
LVE-008): Annual, Sick, Casual, Maternity, Paternity, Compensatory, LWP, WFH.
Adds Bangladesh public holidays + a CE-only approval for WFH.
""",
    "author": "MCB ERP Team",
    "license": "LGPL-3",
    "depends": [
        "mcb_hr_employee",
        "hr_holidays",
    ],
    "data": [
        "views/hr_leave_type_views.xml",
        "views/hr_leave_views.xml",
        "data/hr_leave_type_data.xml",
        "data/resource_calendar_leaves_data.xml",
    ],
    "demo": [
        "demo/mcb_hr_holidays_demo.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
