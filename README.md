# Mukti Cox's Bazar — HR Module suite (Odoo 19 Enterprise)

Custom HR modules built for **Mukti Cox's Bazar (MCB)**, a Cox's Bazar–based NGO,
on **Odoo 19 Enterprise**, implementing the SRS v2.0 + the client's v2.1
yellow-highlight feedback round.

## Modules

| Module | Extends | Purpose |
|---|---|---|
| `mcb_hr_employee` | `hr`, `hr_skills` | Grade model (G1–G10), MCB profile fields (NID, parents, PF nominee, service dates), CE/PM/RC security groups |
| `mcb_hr_recruitment` | `hr_recruitment` | Staff Requisition, Admit Card, marking sheets (Written 50 / Computer 20 / Oral 30), merit ranking, expenditure top sheet, Job Circular & Shortlist QWeb reports |
| `mcb_hr_payroll` | `hr_payroll` | MCB salary structures (Permanent/Project/Support), PF 10+10, gratuity (30/45 days, yearly deposit), festival bonus (2×100% basic / 2×50% gross), Baishakhi, BD income-tax slabs, salary-revision wizard, bank-disbursement CSV |
| `mcb_hr_holidays` | `hr_holidays` | 8 MCB leave types, 2-level approval (+ CE 3rd-level for Compensatory), probation block, Bangladesh public holidays |
| `mcb_hr_onboarding` | `hr` | Onboarding plan (10 mandatory orientations), T-15 probation reminder cron, progress bar |
| `mcb_hr_expense` | `hr_expense` | Per-diem table, grade auto-fill, Economy-only air constraint, CE auto-route for air / Grade 1–2 |
| `mcb_hr_separation` | `hr` | Resignation flow, exit interview, final settlement, experience certificate |
| `mcb_hr` | (umbrella) | Pulls in all of the above |

## Install / upgrade

From the Odoo project root (`/Data/odoo19_enterprise`):

```bash
./start.sh -i mcb_hr          # fresh install of the whole suite
./start.sh -u mcb_hr          # upgrade everything
./start.sh -u mcb_hr_payroll  # upgrade one sub-module
```

DB `dev1` · Odoo 19 Enterprise · BDT currency · Bangladesh localisation.

## Deliverables

- **`mcb_hr/MCB_HR_Module_Guide.docx`** — full implementation & SRS-traceability guide (v2.1, 71 pages, embedded screenshots).
- **`mcb_hr/PLAN.md`** — architecture, build order, decisions log.
- **`mcb_hr/STATUS.md`** — coverage (63/63 requirements ✅) + v2.1 changelog.
- **`mcb_hr/_build/`** — screenshots + the scripts that capture them and generate the guide.

## SRS coverage

All 63 HR requirements (EMP / REC / PAY / LVE / ONB / EXP / SEP) implemented and
adversarially verified. See `mcb_hr/STATUS.md`.
