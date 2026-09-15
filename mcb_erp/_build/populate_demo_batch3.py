"""Batch 3: Project + Volunteer + Vehicle + Store demo data, driven via real
action methods. Anchored to July 2026 (current month) so wizard defaults and
explicit month_date args line up with the attendance/timesheet data created here."""
import traceback
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta

env = env  # noqa: F821
today = date.today()
month_start = date(2026, 7, 1)


def run(name, fn):
    try:
        out = fn()
        print(f"OK   {name}")
        return out
    except Exception as e:
        print(f"FAIL {name}: {e}")
        traceback.print_exc()
        return None


proj = env.ref("mcb_project.demo_project_gbvie")
analytic = proj.account_id
emp_consultant1 = env["hr.employee"].browse(6)   # Abigail Peterson
emp_consultant2 = env["hr.employee"].browse(7)   # Audrey Peterson
emp_driver = env["hr.employee"].browse(23)       # Aminul Haque
emp_dev = env["hr.employee"].browse(14)          # Anita Oliver

# ---------------------------------------------------------------- PROJECT --

def _assignments():
    rows = [
        (emp_consultant1, 60.0), (emp_consultant2, 40.0),
        (emp_driver, 100.0), (emp_dev, 50.0),
    ]
    out = env["mcb.project.assignment"]
    for emp, pct in rows:
        out |= env["mcb.project.assignment"].create({
            "employee_id": emp.id, "project_id": proj.id,
            "date_from": date(2025, 7, 1), "date_to": date(2026, 12, 31),
            "percent": pct,
        })
    return out


run("Project: staff % assignments (PRJ-005)", _assignments)

run("Beneficiary entry: indirect / host community", lambda: env["mcb.beneficiary.entry"].create({
    "project_id": proj.id, "beneficiary_type": "indirect",
    "male": 300, "female": 350, "children": 200, "adults": 400, "elderly": 50,
    "location_type": "host", "camp_no": "Ukhiya Host Community",
    "date": month_start,
}))
run("Beneficiary entry: direct, Camp 19", lambda: env["mcb.beneficiary.entry"].create({
    "project_id": proj.id, "beneficiary_type": "direct",
    "male": 25, "female": 95, "children": 40, "adults": 70, "elderly": 10,
    "location_type": "camp", "camp_no": "Camp 19", "date": month_start,
}))

run("MEAL indicator: GBV case management", lambda: env["mcb.meal.indicator"].create({
    "name": "# of GBV survivors receiving case management", "project_id": proj.id,
    "unit": "count", "target": 200, "achieved": 145, "period": "Q1 FY25-26",
}))
run("MEAL indicator: awareness sessions", lambda: env["mcb.meal.indicator"].create({
    "name": "# of community awareness sessions conducted", "project_id": proj.id,
    "unit": "count", "target": 50, "achieved": 38, "period": "Q1 FY25-26",
}))

ta = run("Travel Authorization (Annex-30): create", lambda: env["mcb.travel.authorization"].create({
    "employee_id": emp_consultant1.id, "project_id": proj.id, "funded_by": "CARE",
    "departure_date": month_start + timedelta(days=10),
    "return_date": month_start + timedelta(days=12),
    "destination": "Dhaka (Head Office coordination meeting)",
    "purpose": "Quarterly donor coordination meeting with CARE Bangladesh",
    "transport_mode": "Air + road", "travel_cost": 12000, "lodging_cost": 9000,
    "food_cost": 3000, "registration_cost": 0, "other_cost": 500,
}))
if ta:
    for step in ("action_submit", "action_finance", "action_recommend", "action_approve"):
        if ta.state not in ("approved", "cancelled"):
            run(f"Travel Authorization: {step}", getattr(ta, step))

run("Quarterly Report wizard (MON-004): create", lambda: env["mcb.quarterly.report.wizard"].create({
    "project_id": proj.id, "date_from": date(2025, 7, 1), "date_to": date(2025, 9, 30),
    "challenges": "Heavy monsoon rains delayed learning-centre construction in Camp 12 "
                  "by roughly two weeks; host-community sensitisation sessions took "
                  "longer than planned due to Eid holidays.",
    "next_plan": "Complete Camp 12 and Camp 19 learning-centre handovers; scale up "
                 "GBV case-management caseload; conduct Q2 donor field visit.",
}))

# Timesheets + extra attendance for Anita Oliver so the timesheet/attendance
# wizards have real data to render for July 2026.
run("Extra attendance: Anita Oliver (more July days)", lambda: [
    env["hr.attendance"].create({
        "employee_id": emp_dev.id,
        "check_in": f"2026-07-{d:02d} 09:00:00",
        "check_out": f"2026-07-{d:02d} 17:00:00",
    }) for d in (2, 3, 6)
])
run("Timesheets: Anita Oliver on GBViE (TMS-002)", lambda: [
    env["account.analytic.line"].create({
        "employee_id": emp_dev.id, "project_id": proj.id,
        "date": f"2026-07-{d:02d}", "name": "GBV case management field support",
        "unit_amount": hrs,
    }) for d, hrs in ((2, 8.0), (3, 8.0), (6, 4.0), (7, 8.0), (8, 5.0))
])

run("Timesheet Report wizard (Annex-23): create", lambda: env["mcb.timesheet.report.wizard"].create({
    "employee_id": emp_dev.id, "month_date": month_start,
}))
run("Attendance Report wizard (Annex-20): create", lambda: env["mcb.attendance.report.wizard"].create({
    "month_date": month_start, "project_name": "GBViE Project", "funded_by": "CARE",
}))

journal_slr = env["account.journal"].search([("company_id", "=", 1), ("name", "=", "Salaries")], limit=1)
acc_expense = env["account.account"].search(
    [("code", "=", "600000"), ("company_ids", "in", [1])], limit=1)
payroll_wiz = run("Payroll Allocation wizard (TMS-004): create", lambda: env["mcb.payroll.allocation.wizard"].create({
    "month_date": month_start, "journal_id": journal_slr.id if journal_slr else False,
    "salary_account_id": acc_expense.id if acc_expense else False,
}))
if payroll_wiz:
    run("Payroll Allocation: post JE", payroll_wiz.action_post_allocation)

# -------------------------------------------------------------- VOLUNTEER --

vol1 = env.ref("mcb_volunteer.demo_vol_1")
vol2 = env.ref("mcb_volunteer.demo_vol_2")


def _vol_attendance():
    lines = env["mcb.volunteer.attendance"]
    for d in range(1, 9):
        lines |= env["mcb.volunteer.attendance"].create({
            "volunteer_id": vol1.id, "date": f"2026-07-{d:02d}", "present": True})
    for d in (1, 2, 3, 4, 7, 8):
        lines |= env["mcb.volunteer.attendance"].create({
            "volunteer_id": vol2.id, "date": f"2026-07-{d:02d}", "present": True})
    return lines


run("Volunteer attendance: July 2026", _vol_attendance)

journal_petty = env["account.journal"].search(
    [("company_id", "=", 1), ("name", "=", "Petty Cash")], limit=1)
batch = run("Volunteer Incentive Batch (VOL-002..004): create", lambda: env["mcb.volunteer.incentive.batch"].create({
    "month_date": month_start, "project_id": proj.id,
    "journal_id": journal_petty.id if journal_petty else False,
    "expense_account_id": acc_expense.id if acc_expense else False,
}))
if batch:
    run("Incentive Batch: compute", batch.action_compute)
    if batch.state == "computed":
        run("Incentive Batch: approve", batch.action_approve)
    if batch.state == "approved":
        run("Incentive Batch: pay (JE)", batch.action_pay)

# --------------------------------------------------------------- VEHICLE ---

vehicle = env["fleet.vehicle"].browse(5)  # Toyota Corolla
run("Vehicle: assign to GBViE + expiry dates", lambda: vehicle.write({
    "mcb_project_id": proj.id, "mcb_vehicle_kind": "project",
    "mcb_insurance_expiry": today + timedelta(days=25),
    "mcb_fitness_expiry": today + timedelta(days=200),
}))


def _log_lines():
    out = env["mcb.vehicle.log"]
    rows = [
        (2, "Camp 12 site visit", "Program Office", "Camp 12", 8.5, 12.5, 15230, 15295, 10, 900),
        (6, "Materials delivery", "Program Office", "Camp 19", 9.0, 16.0, 15295, 15410, 25, 2100),
        (8, "Donor field visit escort", "Program Office", "Ukhiya UNO Office", 8.0, 13.0, 15410, 15455, 8, 750),
    ]
    for d, purpose, loc_from, loc_to, ts, te, ms, me, fuel, cost in rows:
        out |= env["mcb.vehicle.log"].create({
            "vehicle_id": vehicle.id, "date": f"2026-07-{d:02d}",
            "employee_id": emp_driver.id, "driver_name": emp_driver.name,
            "purpose": purpose, "location_from": loc_from, "location_to": loc_to,
            "time_start": ts, "time_end": te, "meter_start": ms, "meter_end": me,
            "fuel_litre": fuel, "fuel_cost": cost, "project_id": proj.id,
        })
    return out


run("Vehicle Log Book (Annex-10): create lines", _log_lines)

run("Movement Register (Annex-09): create", lambda: env["mcb.movement.register"].create({
    "employee_id": emp_consultant1.id if ta else emp_driver.id,
    "office_location": "Cox's Bazar Program Office",
    "destination": "Dhaka (Head Office coordination meeting)",
    "purpose": "Quarterly donor coordination meeting with CARE Bangladesh",
    "departure_date": month_start + timedelta(days=10), "departure_time": 6.0,
    "arrival_date": month_start + timedelta(days=12), "arrival_time": 20.0,
    "travel_auth_id": ta.id if ta else False,
}))

run("Vehicle Log Book wizard: create", lambda: env["mcb.logbook.wizard"].create({
    "vehicle_id": vehicle.id, "month_date": month_start,
}))

# ------------------------------------------------------------------ STORE --

wh_stock = env.ref("stock.stock_location_stock", raise_if_not_found=False) or \
    env["stock.location"].browse(5)
customers_loc = env["stock.location"].browse(2)


def _mk_nfi(name):
    return env["product.product"].create({
        "name": name, "type": "consu", "is_storable": True, "can_be_expensed": False,
    })


tarp = run("NFI product: Tarpaulin Sheet", lambda: _mk_nfi("Tarpaulin Sheet (Heavy Duty)"))
kit = run("NFI product: Hygiene Kit", lambda: _mk_nfi("Hygiene Kit (Family Pack)"))
jerry = run("NFI product: Jerry Can 10L", lambda: _mk_nfi("Jerry Can 10L"))


def _seed_stock():
    Quant = env["stock.quant"]
    for p, qty in ((tarp, 500), (kit, 800), (jerry, 600)):
        if p:
            Quant._update_available_quantity(p, wh_stock, qty)
    return "seeded"


run("Seed NFI opening stock in WH/Stock", _seed_stock)

internal_pt = env["stock.picking.type"].search(
    [("company_id", "=", 1), ("code", "=", "internal")], limit=1)
if not internal_pt:
    internal_pt = run("Store: create Internal Transfers operation type", lambda: env["stock.picking.type"].create({
        "name": "MCB Store Issues", "code": "internal", "sequence_code": "STORE-OUT",
        "warehouse_id": 1, "company_id": 1,
        "default_location_src_id": wh_stock.id, "default_location_dest_id": customers_loc.id,
    }))

srf = run("SRF (Store Requisition Form): create", lambda: env["mcb.srf"].create({
    "project_id": proj.id, "analytic_account_id": analytic.id if analytic else False,
    "source_location_id": wh_stock.id, "dest_location_id": customers_loc.id,
    "recipient_name": "GBViE Distribution Team — Camp 12",
    "line_ids": [
        (0, 0, {"product_id": tarp.id, "quantity": 150, "purpose": "NFI distribution — Camp 12"}),
        (0, 0, {"product_id": kit.id, "quantity": 200, "purpose": "NFI distribution — Camp 12"}),
        (0, 0, {"product_id": jerry.id, "quantity": 200, "purpose": "NFI distribution — Camp 12"}),
    ] if tarp and kit and jerry else [],
}))
if srf and srf.line_ids:
    if srf.state == "draft":
        run("SRF: request", srf.action_request)
    if srf.state == "requested":
        run("SRF: approve", srf.action_approve)
    if srf.state == "approved":
        run("SRF: issue (creates internal transfer)", srf.action_issue)
    if srf.picking_id and srf.picking_id.state not in ("done", "cancel"):
        def _validate_picking():
            for mv in srf.picking_id.move_ids:
                mv.quantity = mv.product_uom_qty
            srf.picking_id.move_ids.picked = True
            return srf.picking_id.button_validate()
        run("SRF: validate transfer (moves -> done)", _validate_picking)

if srf:
    muster = run("Muster Roll (NFI distribution): create", lambda: env["mcb.muster.roll"].create({
        "project_id": proj.id, "product_id": tarp.id if tarp else False,
        "location": "GBViE Camp 12 Learning Centre", "picking_id": srf.picking_id.id if srf.picking_id else False,
        "line_ids": [
            (0, 0, {"beneficiary_name": "Rashida Begum", "beneficiary_id_no": "FCN-991122", "quantity": 1}),
            (0, 0, {"beneficiary_name": "Nurul Amin", "beneficiary_id_no": "FCN-991123", "quantity": 1}),
            (0, 0, {"beneficiary_name": "Fatema Khatun", "beneficiary_id_no": "FCN-991124", "quantity": 1}),
        ],
    }))
    if muster:
        run("Muster Roll: mark distributed", muster.action_done)

run("Store Register wizard (Annex-08): create", lambda: env["mcb.store.register.wizard"].create({
    "location_id": wh_stock.id, "product_id": tarp.id if tarp else False,
    "date_from": today - timedelta(days=30), "date_to": today,
    "project_name": "GBViE Project", "funded_by": "CARE",
}))

env.cr.commit()
print("=== BATCH3 (Project + Volunteer + Vehicle + Store) DONE ===")
