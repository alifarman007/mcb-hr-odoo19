{
    "name": "MCB Procurement (11-Step)",
    "version": "19.0.1.0.0",
    "category": "Inventory/Purchase",
    "summary": "PR with budget check & note sheets, thresholds (Direct/RFQ/RFP/IFT), Opening "
               "Sheet, Technical Analysis, Comparative Statement, Evaluation, NOAL ≥5 lakh, "
               "PO/CO/WO with 4-level authorization, Annexure-29 checklist, procurement reports "
               "(SRS PR-001..008, CS-001..008, NOAL-001..006, PO-001..011, Table-14 reports)",
    "author": "MCB ERP Team",
    "license": "OEEL-1",
    "depends": [
        "purchase",
        "purchase_stock",
        "purchase_requisition",
        "mcb_budget",
    ],
    "data": [
        "security/mcb_purchase_security.xml",
        "security/ir.model.access.csv",
        "data/ir_sequence_data.xml",
        "reports/pr_reports.xml",
        "reports/cs_noal_reports.xml",
        "reports/purchase_order_report.xml",
        "views/mcb_purchase_request_views.xml",
        "views/mcb_procurement_tools_views.xml",
        "views/purchase_order_views.xml",
        "views/menus.xml",
    ],
    "demo": ["demo/mcb_purchase_demo.xml"],
    "installable": True,
    "application": True,
}
