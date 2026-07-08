{
    "name": "MCB Budget Management",
    "version": "19.0.1.0.0",
    "category": "Accounting",
    "summary": "Project Budget (Annex-27), Working Budget (Annex-26), Variance (Annex-11), "
               "revision >10% CE approval, budget lock, donor/quarterly reports "
               "(SRS BUD-001..008, DFR-002..004)",
    "author": "MCB ERP Team",
    "license": "OEEL-1",
    "depends": ["account_budget", "mcb_account"],
    "data": [
        "security/ir.model.access.csv",
        "data/ir_sequence_data.xml",
        "reports/budget_reports.xml",
        "views/budget_analytic_views.xml",
        "views/mcb_working_budget_views.xml",
        "views/mcb_budget_revision_views.xml",
        "views/wizard_views.xml",
        "views/menus.xml",
    ],
    "demo": ["demo/mcb_budget_demo.xml"],
    "installable": True,
    "application": False,
}
