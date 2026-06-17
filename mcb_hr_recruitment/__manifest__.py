{
    "name": "MCB HR — Recruitment",
    "version": "19.0.1.0.0",
    "category": "Human Resources/Recruitment",
    "summary": "Mukti Cox's Bazar — Recruitment pipeline (requisition, admit card, marking sheet, top sheet)",
    "description": """
MCB Recruitment
===============
Extends Odoo `hr_recruitment` for SRS §4 (REC-001 … REC-015): Staff Requisition,
multi-level approval, marks configuration, admit card, attendance sheet, marking
sheets, auto merit ranking, self-declaration, recruitment expenditure top-sheet.
""",
    "author": "MCB ERP Team",
    "license": "LGPL-3",
    "depends": [
        "mcb_hr_employee",
        "hr_recruitment",
        "mail",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/ir_sequence_data.xml",
        "data/hr_recruitment_stage_data.xml",
        "reports/mcb_admit_card_report.xml",
        "reports/mcb_admit_card_topsheet_report.xml",
        "reports/mcb_recruitment_topsheet_report.xml",
        "reports/mcb_job_circular_report.xml",
        "reports/mcb_shortlist_report.xml",
        "views/hr_applicant_views.xml",
        "views/hr_recruitment_stage_views.xml",
        "views/mcb_hr_requisition_views.xml",
        "views/mcb_hr_recruitment_expenditure_views.xml",
        "views/mcb_hr_recruitment_self_declaration_views.xml",
        "views/mcb_hr_recruitment_menus.xml",
    ],
    "demo": [
        "demo/mcb_hr_recruitment_demo.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
