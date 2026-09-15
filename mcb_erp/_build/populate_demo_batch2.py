"""Batch 2: Budget (mcb_budget) + Asset (mcb_asset) demo data, driven via real
action methods so screenshots show meaningful, workflow-correct content."""
import traceback
from datetime import date, timedelta

env = env  # noqa: F821
today = date.today()


def run(name, fn):
    try:
        out = fn()
        print(f"OK   {name}")
        return out
    except Exception as e:
        print(f"FAIL {name}: {e}")
        traceback.print_exc()
        return None


company = env["res.company"].browse(1)
gbvie = env.ref("mcb_budget.demo_budget_gbvie", raise_if_not_found=False)
analytic_gbvie = env["account.analytic.account"].search([("name", "ilike", "GBViE")], limit=1)
employee = env["hr.employee"].search([("company_id", "=", 1)], limit=1)
acc151000 = env["account.account"].search([("code", "=", "151000"), ("company_ids", "in", [1])], limit=1)
acc600000 = env["account.account"].search([("code", "=", "600000"), ("company_ids", "in", [1])], limit=1)
journal_misc = env["account.journal"].search([("company_id", "=", 1), ("type", "=", "general"),
                                              ("name", "=", "Miscellaneous Operations")], limit=1)

print("gbvie:", gbvie, "analytic:", analytic_gbvie, "employee:", employee)

# ---------------------------------------------------------------- BUDGET ---

if gbvie and not gbvie.budget_line_ids:
    def _add_lines():
        lines = [
            ("BL-01", "Learning Centre Construction", "direct", 20, 1, 25000),
            ("BL-02", "Staff Salaries (Project Cost Share)", "staff", 12, 1, 40000),
            ("BL-03", "Office Rent & Utilities", "indirect", 12, 1, 15000),
            ("BL-04", "NFI Distribution", "direct", 500, 1, 1200),
        ]
        for code, act, cat, unit, times, cost in lines:
            env["budget.line"].create({
                "budget_analytic_id": gbvie.id,
                "account_id": analytic_gbvie.id,
                "mcb_activity_code": code,
                "mcb_activity_name": act,
                "mcb_cost_category": cat,
                "mcb_unit": unit, "mcb_times": times, "mcb_unit_cost": cost,
                "budget_amount": unit * times * cost,
            })
        return gbvie.budget_line_ids
    run("GBViE budget: add Annex-27 lines", _add_lines)

if gbvie and gbvie.state == "draft":
    run("GBViE budget: confirm", gbvie.action_budget_confirm)

wb = run("Working Budget (Annex-26): create", lambda: env["mcb.working.budget"].create({
    "budget_id": gbvie.id, "analytic_account_id": analytic_gbvie.id,
    "activity_name": "Q1 FY25-26 Learning Centre Construction Activities",
    "account_id": acc600000.id if acc600000 else False,
    "date_from": date(2025, 7, 1), "date_to": date(2025, 9, 30),
}))
if wb and not wb.line_ids:
    def _wb_lines():
        for name, unit_desc, unit, times, cost in [
            ("Cement & construction materials", "bag", 500, 1, 12),
            ("Skilled labour", "person-day", 60, 1, 800),
            ("Unskilled labour", "person-day", 120, 1, 500),
            ("Transport of materials", "trip", 15, 1, 3500),
        ]:
            env["mcb.working.budget.line"].create({
                "working_budget_id": wb.id, "name": name, "unit_desc": unit_desc,
                "unit": unit, "times": times, "unit_cost": cost,
            })
        return wb.line_ids
    run("Working Budget: add lines", _wb_lines)
if wb and wb.state == "draft":
    run("Working Budget: check", wb.action_check)
if wb and wb.state == "checked":
    run("Working Budget: review", wb.action_review)
if wb and wb.state == "reviewed":
    run("Working Budget: approve", wb.action_approve)

if gbvie and gbvie.budget_line_ids:
    line0 = gbvie.budget_line_ids.filtered(lambda l: l.mcb_activity_code == "BL-04")
    if line0:
        rev = run("Budget Revision (>10%%, CE gate)", lambda: env["mcb.budget.revision"].create({
            "budget_id": gbvie.id, "line_id": line0[0].id,
            "new_amount": line0[0].budget_amount * 1.30,
            "reason": "NFI unit price increase per updated market survey; CARE no-cost extension approved.",
        }))
        if rev and rev.state == "draft":
            run("Budget Revision: submit", rev.action_submit)
        if rev and rev.state == "submitted":
            run("Budget Revision: CE approve", rev.action_approve)

donor_wiz = run("Donor Budget Report wizard: create", lambda: env["mcb.donor.report.wizard"].create({
    "budget_id": gbvie.id, "granularity": "quarterly",
}))

# ----------------------------------------------------------------- ASSET ---

def _mk_asset(name, value, location, condition, funded_by, custodian, acquired_days_ago):
    a = env["account.asset"].create({
        "name": name, "company_id": 1,
        "original_value": value,
        "account_asset_id": acc151000.id, "account_depreciation_id": acc151000.id,
        "account_depreciation_expense_id": acc600000.id, "journal_id": journal_misc.id,
        "method": "linear", "method_number": 5, "method_period": "12",
        "acquisition_date": today - timedelta(days=acquired_days_ago),
        "mcb_location": location, "mcb_condition": condition,
        "mcb_custodian_id": custodian.id if custodian else False,
        "mcb_project_analytic_id": analytic_gbvie.id if analytic_gbvie else False,
        "mcb_funded_by": funded_by,
    })
    a.validate()
    return a


asset1 = run("Asset: Generator Set (Camp 12)", lambda: _mk_asset(
    "Generator Set 15 KVA — Camp 12 Learning Centre", 250000, "GBViE Camp 12 Learning Centre",
    "good", "CARE", employee, 200))
asset2 = run("Asset: Office Laptop", lambda: _mk_asset(
    "Dell Latitop Laptop — Program Office", 85000, "Cox's Bazar Program Office",
    "good", "CARE", employee, 150))
asset3 = run("Asset: Old Photocopier (for disposal demo)", lambda: _mk_asset(
    "Photocopier — Canon iR2006N (old)", 60000, "Cox's Bazar Program Office",
    "damaged", "Core Funds", employee, 1800))

if asset1:
    run("Asset Transfer: Camp 12 -> Camp 8", lambda: env["mcb.asset.transfer"].create({
        "asset_id": asset1.id, "from_project_id": analytic_gbvie.id if analytic_gbvie else False,
        "to_project_id": analytic_gbvie.id if analytic_gbvie else False,
        "from_location": "GBViE Camp 12 Learning Centre", "to_location": "GBViE Camp 8 Learning Centre",
        "from_custodian_id": employee.id if employee else False,
        "to_custodian_id": employee.id if employee else False,
        "note": "Learning centre relocation per donor field visit recommendation.",
    }))

inv = run("Asset Physical Inventory (Annex-22): create", lambda: env["mcb.asset.inventory"].create({
    "project_name": "GBViE Project", "funded_by": "CARE",
}))
if inv:
    run("Asset Inventory: fill from register", inv.action_fill_from_register)
    if inv.line_ids:
        line_dmg = inv.line_ids.filtered(lambda l: l.asset_id == asset3) if asset3 else inv.line_ids[:1]
        if line_dmg:
            line_dmg[0].write({"qty_found": 1, "recommendation": "disposal",
                                "remarks": "Beyond economical repair; recommend write-off."})
    run("Asset Inventory: mark verified", inv.action_done)

if asset3:
    run("Asset: CE-approve disposal (AST-005 gate)", asset3.action_mcb_ce_approve_disposal)

env.cr.commit()
print("=== BATCH2 (Budget + Asset) DONE ===")
