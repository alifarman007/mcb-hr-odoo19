{
    "name": "MCB Logistics & Warehouse",
    "version": "19.0.1.0.0",
    "category": "Inventory",
    "summary": "GSRN goods receipt, Materials Supply Note/Challan (waybill), Bin/Stack Cards, "
               "physical stock verification, stock disposal, warehouse information sheet "
               "(SOP on Warehouse & Inventory Management, LOG-001..012)",
    "description": """
MCB Logistics & Warehouse
=========================
Implements the parts of MCB's *SOP on Warehouse & Inventory Management* that were not
already covered by mcb_store (SRF + Store Register), mcb_asset (Annex-07/22) and
mcb_vehicle (Annex-10):

* **GSRN** — Goods and Service Received Note. The SOP's "base document for financial
  transactions"; raised against a PO/PR/WR or for in-kind donations from a donor,
  UN agency or GoB. Records ordered vs received quantity and the quality inspection.
* **Materials Supply Note / Challan** — the warehouse *issuing* document (waybill).
  Certifies release of goods, carries the carrier details, and is signed on delivery.
* **Bin / Stack Card** — the running balance card kept at the storage location.
  Per the SOP, one card holds one item from one unique PO number in one bin.
* **Physical Stock Verification** — the quarterly / yearly / handover count, with a
  system-vs-physical reconciliation that must be explained before it can be submitted.
* **Stock Disposal Request** — approved disposal of expired or damaged stock.
* **Warehouse Information Sheet** — the SOP's warehouse master record and storekeeper.
* **Monthly Stock Report** — the 17-column period report, by waybill/PO batch.
""",
    "author": "MCB ERP Team",
    "license": "OEEL-1",
    "depends": [
        "stock",
        "purchase_stock",
        "product_expiry",
        "mcb_store",
        "mcb_account",
        "mcb_project",
    ],
    "data": [
        "security/mcb_logistics_security.xml",
        "security/ir.model.access.csv",
        "data/ir_sequence_data.xml",
        "reports/logistics_reports.xml",
        "views/stock_warehouse_views.xml",
        "views/mcb_gsrn_views.xml",
        "views/mcb_challan_views.xml",
        "views/mcb_bin_card_views.xml",
        "views/mcb_stock_verification_views.xml",
        "views/mcb_stock_disposal_views.xml",
        "views/mcb_srf_views.xml",
        "views/wizard_views.xml",
        "views/menus.xml",
    ],
    "demo": [],
    "installable": True,
    "application": False,
    "auto_install": False,
}
