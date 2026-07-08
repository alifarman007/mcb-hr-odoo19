{
    "name": "MCB Fixed Assets",
    "version": "19.0.1.0.0",
    "category": "Accounting",
    "summary": "Fixed Assets Register (Annex-07), Physical Inventory (Annex-22), asset codes, "
               "transfers, CE-gated disposal, labels (SRS AST-001..007)",
    "author": "MCB ERP Team",
    "license": "OEEL-1",
    "depends": ["account_asset", "mcb_account"],
    "data": [
        "security/ir.model.access.csv",
        "data/ir_sequence_data.xml",
        "reports/asset_reports.xml",
        "views/account_asset_views.xml",
        "views/mcb_asset_inventory_views.xml",
        "views/wizard_views.xml",
        "views/menus.xml",
    ],
    "demo": [],
    "installable": True,
    "application": False,
}
