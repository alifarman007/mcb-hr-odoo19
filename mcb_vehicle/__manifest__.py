{
    "name": "MCB Vehicles & Movement",
    "version": "19.0.1.0.0",
    "category": "Human Resources/Fleet",
    "summary": "Vehicle/MC Log Book (Annex-10), Daily Movement Register (Annex-09), Travel "
               "Bill (Annex-25), insurance/fitness expiry alerts (SRS VEH-001..005, MOV-001..004)",
    "author": "MCB ERP Team",
    "license": "OEEL-1",
    "depends": ["fleet", "hr_expense", "mcb_project"],
    "data": [
        "security/ir.model.access.csv",
        "data/ir_cron_data.xml",
        "reports/vehicle_reports.xml",
        "views/fleet_vehicle_views.xml",
        "views/mcb_vehicle_log_views.xml",
        "views/mcb_movement_views.xml",
        "views/menus.xml",
    ],
    "demo": [],
    "installable": True,
    "application": False,
}
