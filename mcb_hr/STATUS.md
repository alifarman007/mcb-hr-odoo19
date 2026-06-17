# MCB HR — Build Status (v2.1)

**Build date:** 2026-06-07 (v2.1 client-feedback round)
**Source SRS:** `/Data/odoo19_enterprise/mukticox/Mukti_MCB_Odoo_SRS_v2.docx`
**Client feedback:** `/Data/odoo19_enterprise/mukticox/version2.docx` (yellow-highlighted modifications)
**Templates folder:** `/Data/odoo19_enterprise/mukticox/format-hr-erp/` (33 files read; relevant ones inlined as QWeb reports)
**Platform:** Odoo 19 Enterprise · DB `dev1` · 127.0.0.1:8069

## v2.1 client-feedback changes (yellow highlights applied)

| Area | Change |
|---|---|
| REC-010 | Marks rebalanced **Written 70→50, Computer 30→20**, Oral 30 |
| REC-011 | Oral marking sheet → **Skills (15) + Knowledge (15)**; Education/Experience sub-scores removed |
| REC-009 | Attendance / Admit Card Top Sheet now lists **Mother's name** column |
| REC-007 | Admit Card signed by **"CE / Director-HR & Admin"** |
| PAY-004 | Project festival bonus **100% → 50% gross** (×2); Baishakhi confirmed permanent-only |
| PAY-006 | Gratuity now **yearly deposit** (full year posted in `mcb_gratuity_deposit_month`, default June) |
| Grade 6–8 | Travel entitlement → **"Standard Transport (CE approval for AC Chair & air)"** |
| Compensatory Leave | Approval chain extended to **Manager + HR + CE** (new 3rd-level CE gate) |
| ONB-002 | Mandatory orientations expanded to **10 sessions** (Org History, Code of Conduct, Safeguarding & PSEAH, AMLTF/Fraud, Finance, IT, Procurement, Logistics, M&E, JD) |

All 9 verified by an adversarial review workflow (10 agents): 9/9 implemented, completeness critic found **no missed HR change and no mis-categorisation**.

**Out-of-scope highlights (Finance/Procurement/Accounts/Audit ERP modules — never built):** budget Monthly_report, donor one-click reports, voucher numbering (VOU-001/006), bank-rec excel (BNK-005), ADV-008 IOU form, VAT/TDS report & vendor BIN (TAX-004/006), donor financial reports (DFR-002/006), Audit-department view-only role.

## Coverage

| Status | Count | % of total |
|---|---|---|
| ✅ Done (full end-to-end) | **63** | **100.0%** |
| ⚠ Partial | 0 | 0.0% |
| ❌ Deferred | 0 | 0.0% |
| **Total SRS requirements** | **63** | |

## v2.0 changelog — 7 items moved Partial → Done

| Req ID | What was added | Driving template |
|---|---|---|
| REC-004 | QWeb `report_mcb_job_circular` — Job Circular / Invitation Letter | File 15 *JOINING CIRCULAR.docx* + file 14 *Joining Letter Bangla-English* |
| REC-006 | QWeb `report_mcb_shortlist` — Shortlist Report (all stages shortlist..hired) | derived from candidate fields |
| REC-008 | QWeb `report_mcb_admit_card_topsheet` — Invigilator attendance sheet | derived from individual admit-card |
| PAY-002 | `mcb.hr.salary.revision.wizard` (5 modes) + 4 letter QWebs | Files 25 (Salary Revision), 30 (Transfer), 20 (Re-appointment), 28 (Service Extension) |
| PAY-009 | `mcb.hr.bank.transfer.wizard` — CSV bank disbursement | Designed from scratch (donor-neutral) |
| EXP-002 | `mcb_requires_ce_approval` + `action_mcb_ce_approve` + constrains rule | HR Policy §9.5 |
| LVE-005 | `hr.leave.type.mcb_block_during_probation` + `hr.leave._check_mcb_probation_block` | HR Policy §3.3 |

## Clean upgrade

```
./stop.sh && ./start.sh -u mcb_hr_recruitment,mcb_hr_payroll,mcb_hr_expense,mcb_hr_holidays
```

Last clean restart: 2026-05-29 — exit 0, no traceback, HTTP 200 on `/web/login`.

## Deliverable

| | |
|---|---|
| Final document | `/Data/odoo19_enterprise/custom-addons/mcb_hr/MCB_HR_Module_Guide.docx` |
| File size | **3.6 MB** |
| Pages | **68** |
| Embedded screenshots | **36** |
| Tables (incl. master traceability) | **33** / 320 rows |
| Master traceability matrix rows | **63 / 63** (all SRS IDs) |
| Version | 2.0 (29 May 2026) |

## Future enhancements (out of SRS v2.0 scope)

| Topic | Why deferred |
|---|---|
| Bengali UI translations | SRS §13.1 open item — MCB needs to specify which forms need Bangla |
| Donor-specific bank XML | PAY-009 CSV works for any bank; per-donor SWIFT / NACH templates are environment-specific |
| Annual tax-slab calibration | Now an editable `hr.rule.parameter` — HR rolls forward each fiscal year |
| FDMN / volunteer staff workflow | Belongs to v3 SRS (full ERP) — see `MCB_Odoo_ERP_Full_SRS_v3.docx` |
| Donor analytic chart of accounts | One demo analytic plan provided; depends on MCB's actual donors |

## Module install state

| Module | v2.0 changes |
|---|---|
| mcb_hr_employee | (unchanged from v1.0) |
| mcb_hr_recruitment | +3 QWeb reports (Job Circular, Shortlist, Admit Card Top Sheet) + Print buttons on requisition form |
| mcb_hr_payroll | +Salary Revision Wizard (5 modes) +4 letter QWebs +Bank Disbursement Wizard +security/ir.model.access.csv |
| mcb_hr_holidays | +`mcb_block_during_probation` field on leave-type +constraint on `hr.leave` |
| mcb_hr_onboarding | (unchanged) |
| mcb_hr_expense | +`mcb_requires_ce_approval` field +CE auto-route logic +CE-Approve button + constraint |
| mcb_hr_separation | (unchanged) |
| mcb_hr | (unchanged — umbrella) |

## How to log in and see the module

```
cd /Data/odoo19_enterprise && ./start.sh
# then open http://127.0.0.1:8069
# user: admin   password: admin   DB: dev1
```
