# MCB HR Module — Implementation Plan

**Client:** Mukti Cox's Bazar (MCB)
**Platform:** Odoo 19 Enterprise
**Source SRS:** `Mukti_MCB_Odoo_SRS_v2.docx` (v2.0, April 2026)
**Date:** 2026-05-28
**Version:** 1.0

---

## 1. Requirement inventory (63 IDs)

Extracted from SRS tables 7–9, 10, 12, 13, 15, 16:

| Area | IDs | Count |
|------|-----|-------|
| Employee | EMP-001 … EMP-008 | 8 |
| Recruitment | REC-001 … REC-015 | 15 |
| Payroll | PAY-001 … PAY-010 | 10 |
| Leave | LVE-001 … LVE-008 | 8 |
| Onboarding | ONB-001 … ONB-007 | 7 |
| Expense | EXP-001 … EXP-007 | 7 |
| Separation | SEP-001 … SEP-008 | 8 |
| **Total** | | **63** |

## 2. Module structure

One umbrella module that depends on seven area-specific extensions. Each extension is an Odoo addon that depends on the corresponding upstream HR app, never re-implementing it.

```
mcb_hr/                           # umbrella (Phase 0 manifest, branding, dashboard)
├── mcb_hr_employee/              # extends `hr` + `hr.version`
├── mcb_hr_recruitment/           # extends `hr_recruitment`
├── mcb_hr_payroll/               # extends `hr_payroll` (Enterprise)
├── mcb_hr_holidays/              # extends `hr_holidays`
├── mcb_hr_onboarding/            # extends `hr` + `mail.activity.plan`
├── mcb_hr_expense/               # extends `hr_expense`
└── mcb_hr_separation/            # extends `hr` (departure flow)
```

## 3. Build order & dependency graph

```
hr_employee ─┬─> hr_holidays ─┐
             ├─> hr_recruitment │
             ├─> hr_payroll ────┼─> hr_separation
             ├─> hr_onboarding   │
             └─> hr_expense ─────┘
                       │
                       └─> mcb_hr (umbrella)
```

Build sequence: **employee → recruitment → payroll → leave → onboarding → expense → separation → umbrella**.

## 4. File-tree (skeleton common to every addon)

```
mcb_hr_<area>/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   └── *.py                  # extensions / new models
├── views/
│   └── *.xml                 # view inheritance + new menus
├── security/
│   ├── ir.model.access.csv   # ACLs
│   └── security.xml          # groups + record rules (where needed)
├── data/
│   └── *.xml                 # demo / config data
└── reports/                  # only where SRS demands a printable doc
    └── *.xml
```

## 5. User-role / security mapping (SRS §2.2)

| SRS Role | Odoo group used / created |
|---|---|
| Chief Executive (CE) | `mcb_hr.group_mcb_ce` (new) |
| HR Manager | `hr.group_hr_manager` (built-in) |
| Project Manager / HoD | `mcb_hr.group_mcb_pm` (new, inherits `hr.group_hr_user`) |
| Finance Officer | `account.group_account_user` + `hr_payroll.group_hr_payroll_user` |
| Recruitment Committee | `mcb_hr.group_mcb_rc` (new) |
| Employee Self-Service | `base.group_user` (default internal user) |
| System Administrator | `base.group_system` |

## 6. Decisions log

> Every decision below is captured because the SRS leaves the call to the implementer. Use this section to back-trace why something was chosen.

| # | Topic | Decision | Reason |
|---|---|---|---|
| D1 | Module split | 7 area children + 1 umbrella | Matches SRS chapters 1:1; each area can be upgraded independently and shows in Apps list with its own icon |
| D2 | Use `hr.version` (Odoo 19) instead of legacy `hr.contract` | Yes — Odoo 19 collapsed contracts into version-based history on `hr.employee` | Future-proof; aligns with Enterprise 19 upgrade docs |
| D3 | Grade representation | New model `mcb.hr.grade` (records 1–10) referenced from `hr.version.mcb_grade_id` rather than a `Selection` field | Editable by HR; lets us attach per-diem, OT eligibility, leave entitlement to the grade record |
| D4 | Employment-type vocabulary | Extend `hr.version.employee_type` selection with MCB values (`probationary`, `project`, `support`) on top of the Odoo defaults | Keeps reporting compatibility with Odoo's own selections |
| D5 | PF + Gratuity | Modeled as salary rules in the `MCB Permanent` salary structure, plus an accrual journal entry monthly | Aligns with Odoo payroll patterns; auditable |
| D6 | Festival bonus & Baishakhi | Encoded as one-shot salary rules driven by company config (festival month / year) on `res.config.settings` | HR can switch months without code change |
| D7 | BD tax slabs | Implemented as `hr.rule.parameter` records (2024-25 individual slabs) used by an income-tax salary rule | Odoo's official way to keep tax tables editable |
| D8 | Currency | All companies created with `BDT` as primary | NFR explicitly states BDT primary |
| D9 | Per-diem table | New model `mcb.hr.per.diem` (one row per grade) drives auto-fill on expense lines | Matches SRS table 14 verbatim |
| D10 | Recruitment scoring | Three new fields on `hr.applicant`: `mcb_written_score`, `mcb_oral_score`, `mcb_total_score` (computed). Five MCB stages added | Single record keeps all marks together (SRS §4.2 mockup) |
| D11 | Admit card | QWeb report on `hr.applicant`, ID format `MCB-MEAL-O-#NN` via `ir.sequence` | Matches SRS REC-007 exemplar |
| D12 | Onboarding | Use Odoo's `mail.activity.plan` (built-in) with MCB-specific template seeded as data | Native onboarding mechanism in Odoo 19 |
| D13 | Probation reminder | `ir.cron` daily check: 15 days before `probation_end_date` schedules an activity on the line manager | Matches ONB-004 |
| D14 | Leave types | Seeded via XML data with proper `requires_allocation` / `leave_validation_type='both'` for 2-level approval | LVE-002 |
| D15 | Work-from-home approval | New leave type with `responsible_user_ids` constrained to the CE group | LVE-008 |
| D16 | Separation / exit interview | New model `mcb.hr.exit.interview` linked One2one to `hr.employee` | Keeps interview answers in a single, exportable record |
| D17 | Final settlement | Server action on `hr.employee.departure.wizard` extension that builds a draft payslip with leave-encash + PF + gratuity inputs | Re-uses Odoo payslip engine |
| D18 | Bengali language | Not delivered v1.0 — marked ⚠ Partial. English UI is in scope; Bangla translations deferred (NFR open item §13.1) | SRS allows |
| D19 | Multi-currency | `res.currency` for USD, GBP, AUD activated; no separate code | NFR row 2 |
| D20 | Audit trail | Rely on Odoo built-in `mail.thread` + `tracking=True` on critical fields | NFR row 5 |
| D21 | Document templates | QWeb reports — Payslip, Admit Card, Recruitment Top Sheet, Appointment Letter, Experience Certificate | Required by SRS |
| D22 | Demo data | One sample employee per grade band, one open requisition, one payslip run, one expense claim, one resignation | Lets a brand-new reviewer see every workflow without manual data entry |
| D23 | OT rule (Grade 9-10 only) | Implemented via salary-rule guard `version.mcb_grade_id.overtime_eligible` | PAY-003 |
| D24 | Bank-transfer file | Marked ⚠ Partial — produces CSV via report; real bank-format is donor-specific | PAY-009 (Should Have) |
| D25 | Bangladesh public-holiday calendar | Seeded into `resource.calendar.leaves` for the default company calendar (CY 2026 + 2027) | LVE-007 |

## 7. Reusable building blocks created in `mcb_hr_employee`

These appear in multiple later modules:

- `mcb.hr.grade` (model + form/list views)
- `mcb.hr.per.diem` (model — populated by `mcb_hr_expense` data, but the model lives here)
- `mcb_hr.group_mcb_ce`, `_pm`, `_rc` (security groups)
- Company-level fields on `res.company` (e.g. `mcb_pf_employer_pct`, festival month settings)

## 8. Out-of-scope explicit calls

| Item | Why deferred |
|---|---|
| Live bank integration (PAY-009) | Donor-dependent format; SRS marks Should-Have. Provide CSV export only |
| Bengali UI translations | SRS §13.1 lists "Bengali language scope" as an open item to be clarified with MCB |
| Real Bangladesh income-tax slab calibration | We seed 2024-25 individual slabs; HR will fine-tune in production via `hr.rule.parameter` |
| FDMN / volunteer staff workflow | Belongs to v3 SRS (full ERP), not the HR v2 deliverable |
| Donor analytic chart of accounts | One demo analytic plan; full structure depends on MCB's actual donors |

## 9. Verification plan

After every sub-module:

1. `./start.sh -u <module>` — log must end with module loaded, zero traceback
2. Headless Playwright login → open module menu → create one record → save
3. Take screenshots into `_build/screenshots/<sub-module>/`

Final pass:

1. `./stop.sh && ./start.sh -u mcb_hr` — full chain upgrade
2. Re-screenshot anything that changed
3. Rebuild `MCB_HR_Module_Guide.docx`
4. Write `STATUS.md` with coverage %.

## 10. Schedule (this session)

Sequential, one sub-module at a time. No parallelism on writes — Odoo upgrades are serial.

```
[plan]    -> [employee] -> [recruitment] -> [payroll] -> [leave]
       -> [onboarding] -> [expense] -> [separation] -> [umbrella]
       -> [screenshots] -> [docx] -> [verify+status]
```
