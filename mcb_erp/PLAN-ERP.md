# MCB Full-ERP Build Plan — SRS v3 Parts B, C, D (+E)

**Date:** 2026-06-27 · **Source:** `MCB_Odoo_ERP_Full_SRS_v3.docx` + client yellow-highlight feedback
(`version2.docx`) + Financial Management Manual (5th ed, OCR'd), Procurement Guidelines 2018 (OCR'd),
Warehouse SOP, Vehicle Policy, and Annexures 01–31.
**Scope:** everything after PART A (HR — already delivered as `mcb_hr*`).

## 0. Requirement inventory (new IDs)

| Part | Groups | Count |
|---|---|---|
| B Purchase | PR-001..008, CS-001..006+008, NOAL-001/002/006, PO-001/002/007/008/010/011, 6 report types | 24 + 6 reports |
| C Accounts | COA×8, VOU×10, BNK×6, PCH×6, ADV×8 (incl. feedback ADV-008), BUD×8, AST×7, TAX×7, DFR×7, PER×5 | 72 |
| D Projects | PRJ×7, TMS×6, ATT×6, VOL×7, MON×8, VEH×5, MOV×4, STO×7 | 50 |
| E Cross | Integration map, NFR, roles (T38 + **Audit view-only**), annexure register | — |

Client-feedback amendments folded in: VOU-001 (per-company journals), VOU-006 (+XLSX),
BNK-005 (+XLSX), **ADV-008 IOU (new)**, TAX-004 (Mushak/Treasury challan detail), TAX-006 (+TIN),
DFR-002 (monthly/bimonthly/quarterly/half-yearly), DFR-006 (+XLSX), T38 Audit role.

## 1. Doctrine: Odoo Enterprise first

Verified available on disk and used as foundations (no OCA/external addons):

| Need | Native app used | Covers natively |
|---|---|---|
| Accounting core, lock dates, multi-currency, TB/GL/Aged reports + XLSX | `account_accountant`, `account_reports` | COA-002/005/006/007, DFR-006, PER-001/002/005 |
| BD CoA + VAT taxes + tax report | `l10n_bd` | COA-001/002 base, TAX-001 (VAT side) |
| Bank statement import + reconciliation | `account_bank_statement_import_csv/ofx` | BNK-001, BNK-004 |
| Cheque numbers | `account_check_printing` | BNK-003 base |
| GRN-gated vendor-bill payment | `account_3way_match` (`release_to_pay`) | PO-007 |
| Budgets by analytic (+PO committed) | `account_budget`, `account_budget_purchase` | BUD-004 base |
| Fixed assets + depreciation | `account_asset` | AST-001/002 base |
| RFQ/PO, call-for-tender & alternatives | `purchase`, `purchase_requisition(_stock)`, `purchase_stock` | Steps 3, 10 |
| Warehouse, GRN, reorder rules, counts | `stock` | STO-003/005/006 base |
| Projects, subtasks, milestones, Gantt | `project`, `project_enterprise` | PRJ-002/004, MON-001/002/003 base |
| Timesheets + validation grid | `hr_timesheet`, `timesheet_grid` | TMS-001/003/005 base |
| Attendance | `hr_attendance` | ATT base |
| Vehicles, odometer, contract expiry | `fleet` | VEH-002/004 base |

Custom = MCB workflows, Annexure-format PDFs/XLSX, and the models Odoo has no equivalent for
(PR, CS, NOAL, advances, IOU, petty-cash count, volunteers, movement register, log book…).

## 2. Module architecture (9 new + umbrella)

```
mcb_account       C-core: voucher workflow (4-level), voucher numbers per FY, voucher PDFs
                  (Annex 01/02/03/04/05/06/24/28/31) + XLSX, amount-in-words, partner BIN/TIN,
                  TDS taxes + challan register (Mushak/Treasury) + monthly VAT/TDS summary,
                  bank-reconciliation statement (Annex-17) PDF/XLSX, analytic plan “Cost Category”
                  (Class), fiscal-year July–June config, Audit view-only group, DFR-001 wizard.
mcb_cash_advance  Advances (Annex-18/19) full lifecycle + IOU (Annex-13, ADV-008) + petty cash:
                  cash count (Annex-14), petty cash book (Annex-15), statement (Annex-16),
                  top-up workflow, limit alert. Crons: 5-day adjustment reminder, low-balance.
mcb_budget        Project Budget (Annex-27) & Working Budget (Annex-26) on budget.analytic/line,
                  Variance Statement (Annex-11), revision workflow (>10% ⇒ CE), budget lock,
                  Donor/Quarterly report wizard (monthly/bimonthly/quarterly/half-yearly/annual;
                  BDT + donor-currency display) → PDF/XLSX. Overage warn/block hooks.
mcb_asset         Asset code sequence, custodian/location/condition/project-donor, Annex-07
                  register (opening/charge/adjust/closing/WDV) PDF+XLSX, Annex-22 physical
                  inventory model+PDF, transfer log, CE-gated disposal, label report.
mcb_purchase      PR model (PR: NNNN/YY-YY) w/ budget balance check + 4-level approvals + Note
                  Sheets 1/2/3 PDFs, threshold auto-method (Direct/RFQ/RFP/IFT per T9), Opening
                  Sheet, Technical Analysis (TA-1/2), Comparative Statement (auto totals +
                  lowest-position + TA-passed gate) PDF/XLSX, Vendor Evaluation, NOAL (auto ≥5 L,
                  blocks PO confirm), PO/CO/WO sequences + 4-signature PO report, procurement
                  checklist (Annex-29), 6 procurement reports.
mcb_store         SRF workflow → internal picking, Store Register (Annex-08) PDF/XLSX, Monthly
                  Stock Report, count-variance report, NFI muster roll (STO-007) PDF.
mcb_project       Project profile (donor/contract/budget/area/status/close-out), assignments w/ %
                  (PRJ-005) + payroll-split allocation report (TMS-004), Annex-23 timesheet PDF
                  (At-a-Glance policy vs actual), Annex-20 monthly attendance PDF/XLSX, task %
                  progress + Gantt, milestone-delay cron, quarterly project report (MON-004),
                  beneficiary entries (MON-005), Travel Authorization (Annex-30) workflow+PDF,
                  Travel Bill (Annex-25) on expense sheet, MEAL indicator scaffold, attendance→
                  timesheet auto-populate cron (TMS-003).
mcb_volunteer     Volunteer DB (camp/block/HTV-RTV-Community/NID), attendance, incentive batch
                  (days × configurable rate; cash/bKash/bank), incentive sheet PDF w/ signature
                  col, camp/month/project summaries, posting to analytic account (VOL-007).
mcb_vehicle       Vehicle ext (project, insurance/fitness expiry + 30-day cron), Log Book lines
                  (Annex-10) + monthly PDF + odometer sync, monthly usage summary, Movement
                  Register (Annex-09) + monthly PDF, links to Travel Auth/Bill (MOV-003/004).
mcb_erp           Umbrella app (depends mcb_hr + the 9 above).
(+ mcb_hr_payroll) add Annex-21 Staff Payroll Sheet QWeb on payslip batch.
```

Dependency order = listing order. Each module: `models/ security/ views/ reports/ data/ demo/`.

## 3. Key design decisions

| # | Decision | Rationale |
|---|---|---|
| E1 | Voucher numbers (`JV-2526-001`) as separate `mcb_voucher_no` field + per-journal/FY ir.sequence — native `name` untouched | Fighting Odoo 19's move-name sequencing is fragile; SRS only requires the number to exist on vouchers/PDFs |
| E2 | 4-level voucher approval as fields+buttons on `account.move`, enforced at post only for journals flagged `mcb_require_approval` | Doesn't break sales/misc flows or demo data |
| E3 | TDS = negative-amount purchase taxes in group “TDS”, created by post_init hook per company (accounts resolved from installed CoA) | Withholding at source per GoB; hook avoids template-XML company issues |
| E4 | “Class / Cost Centre” (VOU-005) = second analytic plan “Cost Category” | Native multi-plan analytic distribution — reportable everywhere |
| E5 | PR is a custom model (not `approvals`) | PR needs budget balance, note sheets, threshold method, PC flow, PR: NNNN/YY-YY — too specific for the generic app |
| E6 | CS is a custom model fed by requisition/alternative RFQs, not just the native compare-lines UI | SRS wants a printable CS with per-vendor totals, positions, PC narrative, letterhead |
| E7 | NOAL gate implemented in `purchase.order.button_confirm` override (≥ BDT 500,000 ⇒ issued NOAL required) | NOAL-006 is a hard Must |
| E8 | Advances/IOU post real journal entries against a per-company Employee-Advance account (auto-created by hook) | Auditable, reconcilable; ADV-007 refund/extra JE auto |
| E9 | Fiscal-year label helper `YY-YY` (July–June) as a mixin used by PR/voucher/advance sequences | PER-005 consistent everywhere |
| E10 | Audit role = `group_mcb_audit` implying `account.group_account_readonly` + read-only ACLs on every mcb_* model | T38 feedback “all modules, only view” honestly scoped |
| E11 | Volunteer incentives post one JE per batch (expense ↔ cash/bank) with analytic distribution | VOL-007 without abusing payroll |
| E12 | Store Register / Monthly Stock / Annex-20 / Annex-23 / registers = wizard-driven QWeb+XLSX over native data | Reports, not new data silos |
| E13 | Timesheet auto-populate (TMS-003) = daily cron drafting lines from yesterday's attendance split by assignment % (opt-in per project) | Native grid stays the editing surface |
| E14 | Beneficiary & MEAL models kept minimal (Should-Have) | Scaffold now, donor-specific config later |
| E15 | Where SRS references source XLSX files we don't have (CoA import, camp sheets), seed structure + document as migration open item | SRS §36 lists them as open items anyway |

## 4. Verification plan
1. `-i <module>` on dev1 after each module; zero ERROR/CRITICAL.
2. Odoo-shell smoke asserts per module (sequences, computes, gates: NOAL block, budget block, advance outstanding check).
3. Final `-u mcb_erp` clean pass + HTTP 200.
4. Adversarial multi-agent verification (Workflow) of Must-Have requirements → fix → STATUS-ERP.md.
