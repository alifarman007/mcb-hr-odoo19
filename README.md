# Mukti Cox's Bazar — ERP suite for Odoo 19 Enterprise

Custom modules built for **Mukti Cox's Bazar (MCB)**, a Cox's Bazar–based NGO, on
**Odoo 19 Enterprise**. What began as the HR suite (SRS v2.0 + the client's v2.1
feedback round) now covers HR, Accounts, Budgets, Assets, Procurement, Store &
Logistics, Projects, Volunteers and Vehicles — SRS v3 Parts B/C/D.

Everything is shaped around MCB's own paperwork: the numbered **Annexures**
(Annex-07 Assets Register, Annex-08 Store Register, Annex-18/19 Advances …), the
**July–June financial year**, BDT, and donor-funded project accounting.

## Modules

Install the umbrella `mcb_erp` for everything, or `mcb_hr` for the HR suite alone.

### HR

| Module | Extends | Purpose |
|---|---|---|
| `mcb_hr_employee` | `hr`, `hr_skills` | Grade ladder G1–G10, MCB profile (NID, parents, PF nominee, service dates), CE/PM/RC security groups |
| `mcb_hr_recruitment` | `hr_recruitment` | Staff Requisition, admit card, marking sheets, merit ranking, expenditure top sheet, Job Circular report |
| `mcb_hr_payroll` | `hr_payroll` | Permanent / Project / Support structures, PF 10+10, gratuity, festival & Baishakhi bonus, BD tax slabs, bank-disbursement CSV |
| `mcb_hr_holidays` | `hr_holidays` | 8 MCB leave types, 2-level approval (+ CE third level), probation block, Bangladesh public holidays |
| `mcb_hr_onboarding` | `hr` | Onboarding plan, probation reminder cron, progress tracker |
| `mcb_hr_expense` | `hr_expense` | TA/DA per-diem by grade, economy-only air rule, CE routing |
| `mcb_hr_separation` | `hr` | Resignation, notice-period shortfall, exit interview, final settlement, certificate |
| `mcb_hr` | umbrella | Installs the seven above |

### Finance

| Module | Extends | Purpose |
|---|---|---|
| `mcb_account` | `account_accountant`, `account_reports` | 4-level voucher workflow (Prepared → Checked → Reviewed → Approved), per-FY voucher numbering, VAT/TDS challans, bank reconciliation (Annex-17), cheque register (Annex-02), money receipts |
| `mcb_budget` | `account_budget` | Project Budget (Annex-27), Working Budget (Annex-26), variance (Annex-11), revision >10% needs CE, budget lock, donor reports |
| `mcb_cash_advance` | `mcb_account`, `hr` | Advance lifecycle (Annex-18/19), IOU (Annex-13), petty cash count/book/statement (Annex-14/15/16) |
| `mcb_asset` | `account_asset` | Fixed Assets Register (Annex-07), physical inventory (Annex-22), asset codes, transfers, CE-gated disposal |

### Operations

| Module | Extends | Purpose |
|---|---|---|
| `mcb_purchase` | `purchase`, `purchase_requisition` | The 11-step procurement process: PR with budget check, Table-9 thresholds (Direct/RFQ/RFP/IFT), opening sheet, technical analysis, comparative statement, evaluation, NOAL ≥ 5 lakh, 4-level PO authorisation |
| `mcb_store` | `stock`, `purchase_stock` | SRF issue workflow, Store Register (Annex-08), monthly stock report, NFI distribution muster roll |
| `mcb_logistics` | `stock`, `mcb_store` | GSRN goods receipt (incl. in-kind donations), Materials Supply Note / Challan (waybill), Bin/Stack Cards, physical stock verification, stock disposal, warehouse information sheet |
| `mcb_project` | `project_enterprise`, `hr_timesheet` | Project profile & donor contract, staff % assignments → payroll cost allocation, timesheets (Annex-23), monthly attendance (Annex-20), beneficiaries & MEAL indicators, Travel Authorization (Annex-30) |
| `mcb_vehicle` | `fleet` | Vehicle/MC Log Book (Annex-10), movement register (Annex-09), travel bill (Annex-25), insurance & fitness expiry alerts |
| `mcb_volunteer` | `mcb_project` | Volunteer database, attendance, incentive batches (days × rate, cash/bKash), camp-wise reports |
| `mcb_erp` | umbrella | Installs everything |

## Install / upgrade

From the Odoo project root (`/Data/odoo19_enterprise`). On this box Odoo runs as
the `mcb-odoo` systemd service on port 8069, so install/upgrade on a spare port
with `--stop-after-init` rather than `./start.sh` — otherwise the port clashes:

```bash
./venv/bin/python ./odoo/odoo-bin -c ./odoo.conf -d mcb_demo \
    -i mcb_erp --stop-after-init --http-port=8099      # fresh install, whole ERP
./venv/bin/python ./odoo/odoo-bin -c ./odoo.conf -d mcb_demo \
    -u mcb_logistics --stop-after-init --http-port=8099   # upgrade one module
sudo systemctl restart mcb-odoo                        # pick the change up live
```

`./start.sh -i mcb_erp` also works, but only with the service stopped.

DB `mcb_demo` · Odoo 19 Enterprise · BDT · Bangladesh localisation · FY July–June.

## Documentation & training material

| Where | What |
|---|---|
| `mcb_hr/PLAN.md`, `mcb_erp/PLAN-ERP.md` | Architecture, build order, decisions log |
| `mcb_hr/STATUS.md`, `mcb_erp/STATUS-ERP.md` | Requirement coverage and changelog |
| `mcb_hr/MCB_HR_Module_Guide.docx` | HR implementation & SRS-traceability guide |

Trainer's guides (Bangla narration, English UI labels, one annotated screenshot
per step) and the click-path video series are **generated artefacts** and are not
kept in this repo — they are produced into `mukticox/` by the build scripts below:
HR, Payslip, Purchase, Project, Open Tender (IFT), Logistics and Accounts guides,
plus 45 video clips across HR, Accounts, Project and Purchase.

## Build tooling (`_build/`)

`mcb_hr/_build/` and `mcb_erp/_build/` hold the pipeline that produces the guides
and videos straight from a running Odoo — so the screenshots can never drift from
the real screens:

- `populate_*.py` — story/demo data, run through `odoo-bin shell`
- `flow_recorder.py` — drives a real journey in Playwright, screenshots each step
  and rings the exact element to click (red ring + cursor + numbered badge + role chip)
- `flow_*.py` — the click-path definitions per module
- `make_flow_video.py`, `make_*_video.py` — render the steps to MP4 (static frames only)
- `*_bn.py` — the Bangla narration for each module's trainer guide
- `build_*_docx.py`, `build_module_docx.py` — assemble the .docx guides

Generated frames, video segments and screenshot folders are gitignored; rerun the
capture and build scripts to recreate them.

Re-capture after any data or branding change, otherwise guides will show stale
screens:

```bash
cd custom-addons/mcb_erp/_build
../../../venv/bin/python flow_logistics.py      # capture
../../../venv/bin/python build_logistics_guide.py   # build the .docx
```
