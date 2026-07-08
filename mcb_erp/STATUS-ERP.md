# MCB Full-ERP Build Status (SRS v3 Parts B/C/D)

**Build date:** 2026-07-09 (local build; deployment to the client server deferred by request)
**Source:** `MCB_Odoo_ERP_Full_SRS_v3.docx` + client yellow-highlight feedback (`version2.docx`)
+ Financial Management Manual 5th ed (OCR), Procurement Guidelines 2018 (OCR), Warehouse SOP,
Vehicle Policy, Annexures 01–31 (all read in full).

## What was built — 10 new modules

| Module | SRS home | Highlights |
|---|---|---|
| `mcb_account` | Part C §13–14, 19–21 | 4-level voucher workflow + per-FY voucher numbers (JV-2526-001…), Annex-01/02/03/04/05/06/24/28/31 PDFs + XLSX, TDS **withholding-on-payment** taxes + Mushak/Treasury challan register + monthly VAT/TDS summary (deductible/deducted/deposited/dues), Annex-17 bank reconciliation PDF/XLSX, partner BIN+TIN, Cost-Category analytic plan (Class), July–June FY, restrictive audit trail, **Audit view-only role**, year-end fund-balance closing wizard, hard GRN payment gate |
| `mcb_cash_advance` | Part C §15–16 | Advance lifecycle (Annex-18/19) with real JEs, ADV-003 outstanding block, 5-working-day reminder cron (Fri/Sat weekend), **IOU (Annex-13, feedback ADV-008)**, petty cash count (Annex-14) / book (Annex-15) / statement (Annex-16), top-up workflow, low-balance alert |
| `mcb_budget` | Part C §17 | Annex-27 columns on `budget.line`, Working Budget (Annex-26) with live consumption, Variance Statement (Annex-11), revision workflow (>10% ⇒ CE only), CE budget lock, overage warn/block on bills **and** POs, Donor Budget-vs-Actual report (monthly/bimonthly/quarterly/half-yearly/annual + donor-currency display) PDF/XLSX |
| `mcb_asset` | Part C §18 | Asset ID sequence, custodian/location/condition/donor, Annex-07 register (opening/charge/adjustment/closing/WDV) PDF/XLSX, Annex-22 physical inventory, transfer history, CE-gated disposal, barcode labels |
| `mcb_purchase` | Part B | PR `PR: NNNN/YY-YY` with budget-balance check + CE override, Table-9 auto method (Direct/RFQ/RFP/IFT), Note Sheets 1/2/3, RFQ fan-out per vendor, Opening Sheet, TA-1/TA-2, **Comparative Statement** (auto totals, lowest positions, TA-passed gate, PC narrative) PDF, Vendor Evaluation → winning PO, **NOAL** (auto ≥ 5,00,000; PO confirm hard-blocked without it), PO/CO/WO sequences, 4-level PO authorization gating confirm ≥ 10k, Annex-29 checklist, 6 procurement reports |
| `mcb_store` | Part D §29 | SRF workflow → internal transfer, Store Register (Annex-08) running balance PDF/XLSX, Monthly Stock Report, NFI muster roll with beneficiary signatures |
| `mcb_project` | Part D §22–27 | Project profile (donor/contract/budget/area/close-out gate), staff % assignments (≤100% enforced), **payroll cost allocation JE** by assignment % (TMS-004), Annex-23 timesheet w/ At-a-Glance policy-vs-actual, Annex-20 monthly attendance PDF/XLSX, beneficiary entries (gender/age/camp-host), Travel Authorization (Annex-30) workflow+PDF, quarterly report (MON-004), milestone-delay cron, TMS-003 attendance→timesheet cron, camp attendance CSV import, MEAL scaffold |
| `mcb_volunteer` | Part D §26 | HTV/RTV/Community DB (camp/block/FCN), attendance, incentive batches (days × per-type rate; cash/bKash/bank), signature sheet PDF, analytic JE posting |
| `mcb_vehicle` | Part D §28 | Vehicle register ext (project, insurance/fitness expiry + 30-day alert cron), Log Book (Annex-10) lines + odometer sync + monthly PDF/XLSX, Movement Register (Annex-09) + PDF, Travel Bill (Annex-25) over expenses with movement refs |
| `mcb_erp` | umbrella | one-shot install of the whole ERP (HR + B/C/D) |
| *(+ `mcb_hr_payroll`)* | | Annex-21 Staff Payroll Sheet on payslip batches |

Native Enterprise apps carrying requirements (no custom code needed): `account_accountant`,
`account_reports` (TB/GL/Aged + XLSX), `l10n_bd` (BD CoA + VAT), `account_bank_statement_import_csv/ofx`
(BNK-001), `account_3way_match` (+ hard payment gate), `account_budget(+purchase)`, `account_asset`,
`purchase(_stock/_requisition)`, `stock` (GRN/reorder/counts), `project_enterprise` (Gantt/milestones),
`timesheet_grid` (validation = TMS-005), `hr_attendance`, `hr_payroll_attendance` (ATT-003), `fleet`,
`l10n_account_withholding_tax` (TDS at payment + challan sequence).

## Verification

1. **Every module installed clean on dev1** (with demo data, 2-company DB).
2. **Fresh no-demo DB `mcb_test`: full-chain `-i mcb_erp` → 204 modules, exit 0, zero errors.**
3. **Live smoke tests (Odoo shell, 11 scenarios): all pass** —
   FY labels · TDS-withholding taxes · July–June FY · PR number & Table-9 thresholds ·
   PO ≥ 5 L blocked without NOAL/approval · advance pay JE · ADV-003 outstanding block ·
   adjustment settle + 200 BDT refund cash line · JV voucher number + amount-in-words ·
   incentive 5 d × 500 · assignment >100% blocked · VOU-002 post gate (block → approve → post).
4. Plan was adversarially reviewed **before** building (25 findings — all HIGH/MED folded in:
   withholding engine, hard GRN gate, per-company hook guards, PR-as-analytic design,
   real PO authorization, no-demo verification DB, hr.expense-sheet removal, payroll-split JE…).

## Coverage (146 requirement IDs, Parts B/C/D)

| Status | Count |
|---|---|
| ✅ Done | **141** |
| ⚠ Partial | **5** |
| ❌ Deferred | 0 |

⚠ Partial detail:
- **COA-001** — BD chart + native CSV import preserve MCB codes; the actual `Budget_Chart_of_Accounts.xlsx` file was not supplied → data load pending (SRS §36 open item 3).
- **BUD-007** (Should) — multi-year budgets modelled as one budget per FY; consolidated multi-FY view pending.
- **MON-007** (Should) — MEAL indicators scaffolded (target/achieved/%), full indicator framework awaits MEAL officer's list (SRS §36 open item 9).
- **ATT-006** (Should) — attendance data + pivots available; bespoke absenteeism dashboard not built.
- **VEH-005** (Should) — both registers exist; automatic cross-reference between vehicle log and movement register is manual.

## Where to click (dev1 · https://mcb-odoo.tail4092a2.ts.net · admin/admin)

- **Accounting → MCB Registers** — challans, payment checklists, bank recon, cheque register, top sheet, VAT/TDS summary, donor report, year-end closing, asset register/inventory
- **Accounting → Advances & Petty Cash** — advances, adjustments, IOU, cash counts, top-ups, petty book
- **Accounting → MCB Budgets** — working budgets, revisions, donor budget report
- **Purchase → MCB Procurement / MCB Reports** — PR → Opening → TA → CS → Evaluation → NOAL → checklists; 6 reports
- **Inventory → MCB Store** — SRF, muster rolls, store register
- **Project → MCB** — assignments, beneficiaries, travel authorizations, MEAL, quarterly/timesheet/attendance reports, payroll allocation
- **MCB Volunteers** (top-level app) — database, attendance, incentive batches
- **Fleet → MCB** — vehicle log book, movement register, monthly log PDF

## Not done on purpose

- Deployment to the client server (user will trigger later; `git pull` + `-u mcb_erp` per the runbook).
- Real CoA/budget/volunteer data loads (migration files listed in SRS Table-41 not provided).
