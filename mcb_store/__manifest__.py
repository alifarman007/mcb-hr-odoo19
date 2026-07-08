{
    "name": "MCB Store & Inventory",
    "version": "19.0.1.0.0",
    "category": "Inventory",
    "summary": "SRF issue workflow, Store Register (Annex-08), Monthly Stock Report, "
               "NFI distribution muster roll (SRS STO-001..007)",
    "author": "MCB ERP Team",
    "license": "OEEL-1",
    "depends": ["stock", "purchase_stock", "project", "mcb_account"],
    "data": [
        "security/ir.model.access.csv",
        "reports/store_reports.xml",
        "views/mcb_srf_views.xml",
        "views/mcb_muster_roll_views.xml",
        "views/wizard_views.xml",
        "views/menus.xml",
    ],
    "demo": [],
    "installable": True,
    "application": False,
}
