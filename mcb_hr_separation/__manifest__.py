{
    "name": "MCB HR — Separation",
    "version": "19.0.1.0.0",
    "category": "Human Resources",
    "summary": "Mukti Cox's Bazar — Resignation flow, exit interview, final settlement, offboarding",
    "description": """
MCB Separation & Offboarding
============================
Implements SRS §9 (SEP-001 … SEP-008): resignation submission, notice-period
enforcement, exit interview, final settlement calc (salary + leave encash +
PF + gratuity), property handover checklist, deactivation on final day, and
optional experience-certificate generation.
""",
    "author": "MCB ERP Team",
    "license": "LGPL-3",
    "depends": [
        "mcb_hr_employee",
        "mcb_hr_holidays",
        "mcb_hr_payroll",
        "mail",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/ir_sequence_data.xml",
        "data/mail_activity_type_data.xml",
        "views/mcb_hr_resignation_views.xml",
        "views/mcb_hr_exit_interview_views.xml",
        "views/mcb_hr_separation_menus.xml",
        "reports/experience_certificate_report.xml",
    ],
    "demo": [],
    "installable": True,
    "application": False,
    "auto_install": False,
}
