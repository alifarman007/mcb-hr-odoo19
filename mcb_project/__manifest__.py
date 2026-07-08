{
    "name": "MCB Projects & Donor Reporting",
    "version": "19.0.1.0.0",
    "category": "Services/Project",
    "summary": "Project profiles, staff % assignments + payroll cost allocation, timesheet "
               "(Annex-23), monthly attendance (Annex-20), beneficiaries, Travel Authorization "
               "(Annex-30), quarterly report, milestone alerts, MEAL scaffold "
               "(SRS PRJ, TMS, ATT, MON)",
    "author": "MCB ERP Team",
    "license": "OEEL-1",
    "depends": [
        "project_enterprise",
        "hr_timesheet",
        "timesheet_grid",
        "hr_attendance",
        "hr_payroll_attendance",
        "hr_expense",
        "mcb_account",
        "mcb_hr_holidays",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/ir_cron_data.xml",
        "reports/project_reports.xml",
        "views/project_views.xml",
        "views/mcb_assignment_views.xml",
        "views/mcb_beneficiary_views.xml",
        "views/mcb_travel_auth_views.xml",
        "views/wizard_views.xml",
        "views/menus.xml",
    ],
    "demo": ["demo/mcb_project_demo.xml"],
    "installable": True,
    "application": False,
}
