{
    "name": "MCB Volunteers (FDMN/HTV/RTV)",
    "version": "19.0.1.0.0",
    "category": "Human Resources",
    "summary": "Volunteer database, attendance, incentive batches (days × rate, cash/bKash), "
               "camp-wise reports, analytic posting (SRS VOL-001..007, ATT-005)",
    "author": "MCB ERP Team",
    "license": "OEEL-1",
    "depends": ["mcb_project"],
    "data": [
        "security/ir.model.access.csv",
        "reports/volunteer_reports.xml",
        "views/mcb_volunteer_views.xml",
        "views/menus.xml",
    ],
    "demo": ["demo/mcb_volunteer_demo.xml"],
    "installable": True,
    "application": True,
}
