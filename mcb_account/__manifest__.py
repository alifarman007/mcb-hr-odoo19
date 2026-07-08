{
    "name": "MCB Accounts — Vouchers, Tax & Registers",
    "version": "19.0.1.0.0",
    "category": "Accounting",
    "summary": "Mukti Cox's Bazar — voucher workflow, VAT/TDS & challans, bank reconciliation "
               "statement, cheque register, top sheet, money receipts (SRS v3 Part C core)",
    "description": """
MCB Accounts core (SRS v3 §11–§21)
==================================
- 4-level voucher approval (Prepared/Checked/Reviewed/Approved) on journal entries (VOU-002)
- Voucher numbers per journal per July–June fiscal year, e.g. JV-2526-001 (VOU-001, PER-005)
- Voucher PDFs on MCB letterhead matching Annexures 03–06 + XLSX export (VOU-006)
- Amount-in-words on vouchers and payments (VOU-004)
- Cost Category analytic plan = "Class" dimension (VOU-005)
- Money Receipt (Annexure-01/31) on inbound payments (DFR-007)
- Cheque Issue Register (Annexure-02) report (BNK-003)
- Bank Reconciliation Statement (Annexure-17) PDF + XLSX (BNK-002/005)
- Expenses Top Sheet (Annexure-24) from vendor bills (VOU-008, TAX-002)
- Payment Voucher Checklist (Annexure-28) (VOU-007, TAX-003)
- TDS withholding taxes + VAT/TDS challan register (Mushak / Treasury) + monthly summary
  with deductible/deducted/deposited/dues (TAX-001..006 incl. client feedback)
- Partner BIN & TIN (TAX-006)
- Audit view-only role (T38 feedback)
- July–June fiscal year defaults (PER-005); analytic P&L by donor/project wizard (DFR-001)
""",
    "author": "MCB ERP Team",
    "license": "OEEL-1",
    "depends": [
        "account_accountant",
        "account_reports",
        "account_check_printing",
        "account_3way_match",
        "account_bank_statement_import_csv",
        "l10n_account_withholding_tax",
        "l10n_bd",
        "mcb_hr_employee",
    ],
    "data": [
        "security/mcb_account_security.xml",
        "security/ir.model.access.csv",
        "data/ir_sequence_data.xml",
        "data/ir_cron_data.xml",
        "data/analytic_plan_data.xml",
        "data/checklist_template_data.xml",
        "reports/voucher_report.xml",
        "reports/money_receipt_report.xml",
        "reports/cheque_register_report.xml",
        "reports/bank_recon_report.xml",
        "reports/top_sheet_report.xml",
        "reports/vat_tds_report.xml",
        "reports/payment_checklist_report.xml",
        "reports/analytic_report.xml",
        "views/account_journal_views.xml",
        "views/account_move_views.xml",
        "views/account_payment_views.xml",
        "views/res_partner_views.xml",
        "views/mcb_tax_challan_views.xml",
        "views/mcb_payment_checklist_views.xml",
        "views/wizard_views.xml",
        "views/menus.xml",
    ],
    "demo": [
        "demo/mcb_account_demo.xml",
    ],
    "post_init_hook": "post_init_hook",
    "installable": True,
    "application": True,
}
