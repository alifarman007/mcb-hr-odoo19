{
    "name": "MCB HR — Employee",
    "version": "19.0.1.0.0",
    "category": "Human Resources",
    "summary": "Mukti Cox's Bazar — Employee master extensions (grade, NID, PF nominee, project assignment)",
    "description": """
MCB Employee Management
=======================
Extends Odoo's hr application with MCB-specific fields, security groups and
grade-structure model required by SRS §3 (EMP-001 … EMP-008).
""",
    "author": "MCB ERP Team",
    "website": "https://mukticox.org",
    "license": "LGPL-3",
    "depends": [
        "hr",
        "hr_skills",
        "mail",
    ],
    "data": [
        "security/mcb_hr_security.xml",
        "security/ir.model.access.csv",
        "data/mcb_hr_grade_data.xml",
        "data/ir_sequence_data.xml",
        "views/mcb_hr_grade_views.xml",
        "views/hr_employee_views.xml",
        "views/hr_version_views.xml",
        "views/mcb_hr_menus.xml",
    ],
    "demo": [
        "demo/mcb_hr_employee_demo.xml",
    ],
    "installable": True,
    "application": True,
    "auto_install": False,
}
