"""Story data for the MCB Project module click-path tutorials.

The person is the same one the HR videos follow: Rashedul Karim (MEAL-001),
MEAL Officer on the GBViE project in Cox's Bazar, CARE-funded. Here he does the
project side of the job - work breakdown, timesheets, beneficiary data, MEAL
indicators and a field trip that needs a Travel Authorization.

Every step runs inside a savepoint so one failure cannot roll the rest back.
"""
from datetime import date, timedelta

env = env  # noqa: F821

PROJECT = 10               # GBViE - Gender Based Violence in Emergency
BUDGET = 3                 # budget.analytic - GBViE-CARE FY 25-26
RASHEDUL = 22              # hr.employee MEAL-001
AMINUL = 23                # CORE-002
RAHMAT = 26                # MCB-005
TAREK = 27                 # MCB-006
TODAY = date.today()


def run(name, fn):
    try:
        with env.cr.savepoint():
            out = fn()
        print(f"OK   {name}")
        return out
    except Exception as e:
        print(f"FAIL {name}: {str(e)[:200]}")
        return None


project = env["project.project"].browse(PROJECT)
Task = env["project.task"]

# ------------------------------------------- 1. finish the project profile --
def _profile():
    project.write({
        "mcb_budget_id": BUDGET,
        "mcb_donor_currency_id": env["res.currency"].search(
            [("name", "=", "USD")], limit=1).id,
        "mcb_donor_budget": 150000.0,
        "allow_timesheets": True,
    })
    return f"{project.name} -> budget {project.mcb_budget_id.display_name}"


print("  ", run("link the project to its Annexure-27 budget", _profile))

# -------------------------------- 2. work breakdown: output > activity > task
WBS = [
    ("Output 1 - GBV survivors have access to quality case management", "output", 55, [
        ("Activity 1.1 - Run case management at the 3 women-friendly spaces", "activity", 65, [
            ("Recruit and train 6 case workers", "task", 100),
            ("Open the Camp 12 women-friendly space", "task", 100),
            ("Monthly case review with the protection sector", "task", 40),
        ]),
        ("Activity 1.2 - Referral pathway with health and legal partners", "activity", 45, [
            ("Sign referral MoUs with 4 partners", "task", 75),
            ("Print and distribute the referral directory", "task", 20),
        ]),
    ]),
    ("Output 2 - Communities are aware of GBV risks and services", "output", 40, [
        ("Activity 2.1 - Community awareness sessions in camps 4, 12 and 19",
         "activity", 50, [
             ("Train 20 community volunteers", "task", 80),
             ("Hold 60 awareness sessions", "task", 35),
         ]),
        ("Activity 2.2 - Distribute dignity and hygiene kits", "activity", 30, [
            ("Procure 300 hygiene kits", "task", 25),
            ("Distribution in Camp 19", "task", 0),
        ]),
    ]),
    ("Output 3 - MEAL system produces evidence for CARE and the sector",
     "output", 35, [
         ("Activity 3.1 - Beneficiary tracking and quarterly reporting",
          "activity", 35, [
              ("Set up the beneficiary database", "task", 100),
              ("Q1 quarterly report to CARE", "task", 60),
          ]),
     ]),
]


def _wbs():
    created = 0

    def make(name, level, progress, parent=None):
        nonlocal created
        found = Task.search([("project_id", "=", PROJECT), ("name", "=", name)], limit=1)
        if found:
            found.write({"mcb_task_level": level, "mcb_progress": progress})
            return found
        t = Task.create({
            "project_id": PROJECT, "name": name, "mcb_task_level": level,
            "mcb_progress": progress, "parent_id": parent.id if parent else False,
            "user_ids": [(6, 0, [9])],   # rashedul
        })
        created += 1
        return t

    for out_name, out_lvl, out_pct, activities in WBS:
        out = make(out_name, out_lvl, out_pct)
        for act_name, act_lvl, act_pct, tasks in activities:
            act = make(act_name, act_lvl, act_pct, out)
            for tk_name, tk_lvl, tk_pct in tasks:
                make(tk_name, tk_lvl, tk_pct, act)
    return f"{created} new tasks, {Task.search_count([('project_id', '=', PROJECT)])} total"


print("  ", run("build the Output / Activity / Task breakdown (PRJ-002)", _wbs))

# ------------------------------------------------------------ 3. milestones --
MILESTONES = [
    ("3 women-friendly spaces open and staffed", -120, True),
    ("300 survivors reached with case management", -20, False),   # overdue on purpose
    ("Mid-term review submitted to CARE", 35, False),
    ("Project close-out and asset handover", 180, False),
]


def _milestones():
    M = env["project.milestone"]
    n = 0
    for name, offset, reached in MILESTONES:
        if M.search_count([("project_id", "=", PROJECT), ("name", "=", name)]):
            continue
        M.create({"project_id": PROJECT, "name": name,
                  "deadline": TODAY + timedelta(days=offset),
                  "is_reached": reached})
        n += 1
    return f"{n} milestones added (one deliberately overdue, for the MON-003 alert)"


print("  ", run("project milestones incl. one overdue (MON-003)", _milestones))

# --------------------------------------------- 4. staff assignments (% time) --
ASSIGN = [(RASHEDUL, 100.0), (AMINUL, 100.0), (RAHMAT, 60.0), (TAREK, 40.0)]


def _assignments():
    A = env["mcb.project.assignment"]
    A.search([("project_id", "=", PROJECT)]).unlink()
    for emp, pct in ASSIGN:
        A.create({"employee_id": emp, "project_id": PROJECT, "percent": pct,
                  "date_from": date(TODAY.year if TODAY.month >= 7 else TODAY.year - 1, 7, 1),
                  "date_to": date(TODAY.year if TODAY.month < 7 else TODAY.year + 1, 6, 30)})
    return ", ".join(f"{env['hr.employee'].browse(e).name} {p:g}%" for e, p in ASSIGN)


print("  ", run("staff assignments on GBViE (PRJ-005)", _assignments))

# ------------------------------------------------------ 5. timesheet history --
def _timesheets():
    AAL = env["account.analytic.line"]
    tasks = Task.search([("project_id", "=", PROJECT), ("mcb_task_level", "=", "task")])
    if not tasks:
        return "no tasks"
    emp_ids = [RASHEDUL, AMINUL, RAHMAT]
    made = 0
    for back in range(1, 31):
        d = TODAY - timedelta(days=back)
        if d.weekday() == 4:          # Friday - weekend in Bangladesh
            continue
        for i, emp in enumerate(emp_ids):
            task = tasks[(back + i) % len(tasks)]
            if AAL.search_count([("employee_id", "=", emp), ("date", "=", d),
                                 ("task_id", "=", task.id)]):
                continue
            AAL.create({
                "employee_id": emp, "project_id": PROJECT, "task_id": task.id,
                "date": d, "unit_amount": [8.0, 6.0, 4.0][i],
                "name": task.name[:60],
            })
            made += 1
    return f"{made} timesheet lines over the last 30 days"


print("  ", run("timesheet history for the assigned staff (TMS)", _timesheets))

# ---------------------------------------------- 6. beneficiary data (MON-005)
BENEF = [
    (-75, "direct", "camp", "Camp 12", 42, 168, 0, 61, 132, 17,
     "Case management intake, October"),
    (-45, "direct", "camp", "Camp 19", 31, 149, 2, 48, 118, 16,
     "Case management intake, November"),
    (-45, "indirect", "host", "Ratnapalong Union", 210, 265, 0, 150, 290, 35,
     "Awareness sessions, host community"),
    (-15, "direct", "camp", "Camp 4", 26, 121, 1, 39, 96, 13,
     "Dignity kit distribution"),
    (-15, "indirect", "camp", "Camp 12", 180, 240, 0, 130, 260, 30,
     "Household members reached indirectly"),
]


def _beneficiaries():
    B = env["mcb.beneficiary.entry"]
    n = 0
    for off, btype, loc, camp, male, female, other, ch, ad, el, note in BENEF:
        d = TODAY + timedelta(days=off)
        if B.search_count([("project_id", "=", PROJECT), ("date", "=", d),
                           ("note", "=", note)]):
            continue
        B.create({"project_id": PROJECT, "date": d, "beneficiary_type": btype,
                  "location_type": loc, "camp_no": camp, "male": male,
                  "female": female, "other": other, "children": ch, "adults": ad,
                  "elderly": el, "note": note})
        n += 1
    total = sum(B.search([("project_id", "=", PROJECT)]).mapped("total"))
    return f"{n} new entries, {total:,} people recorded in total"


print("  ", run("beneficiary reach, disaggregated (MON-005)", _beneficiaries))

# ------------------------------------------------ 7. MEAL indicators (MON-007)
MEAL = [
    ("# of GBV survivors receiving case management", "survivors", 600, 391, "Q2 26-27"),
    ("# of community awareness sessions conducted", "sessions", 60, 21, "Q2 26-27"),
    ("# of dignity kits distributed", "kits", 300, 148, "Q2 26-27"),
    ("% of survivors referred within 48 hours", "percent", 90, 84, "Q2 26-27"),
    ("# of community volunteers trained", "volunteers", 20, 16, "Q2 26-27"),
]


def _meal():
    M = env["mcb.meal.indicator"]
    n = 0
    for name, unit, target, achieved, period in MEAL:
        rec = M.search([("project_id", "=", PROJECT), ("name", "=", name)], limit=1)
        vals = {"unit": unit, "target": target, "achieved": achieved, "period": period}
        if rec:
            rec.write(vals)
        else:
            M.create(dict(vals, name=name, project_id=PROJECT))
            n += 1
    return f"{n} added, {M.search_count([('project_id', '=', PROJECT)])} indicators live"


print("  ", run("MEAL indicators with target vs achieved (MON-007)", _meal))

# ------------------------------------- 8. travel authorizations, every state --
TRIPS = [
    ("draft", RASHEDUL, "Camp 19, Ukhiya", "Monthly beneficiary verification visit",
     3, 1800, 0, 900, 0, 0),
    ("submitted", RASHEDUL, "Camp 4 and Camp 12", "Awareness session monitoring",
     2, 1200, 0, 600, 0, 0),
    ("finance", AMINUL, "Dhaka - CARE country office", "Quarterly review meeting",
     4, 9500, 7200, 3200, 0, 1500),
    ("recommended", RAHMAT, "Teknaf field office", "Volunteer training rollout",
     5, 3500, 4500, 2500, 2000, 0),
]


def _travel():
    T = env["mcb.travel.authorization"]
    out = []
    for stage, emp, dest, purpose, days, travel, lodging, food, reg, other in TRIPS:
        if T.search_count([("destination", "=", dest), ("purpose", "=", purpose)]):
            continue
        rec = T.create({
            "employee_id": emp, "project_id": PROJECT, "funded_by": "CARE",
            "departure_date": TODAY + timedelta(days=7),
            "return_date": TODAY + timedelta(days=7 + days),
            "destination": dest, "purpose": purpose,
            "transport_mode": "MCB vehicle / bus",
            "travel_cost": travel, "lodging_cost": lodging, "food_cost": food,
            "registration_cost": reg, "other_cost": other,
        })
        order = ["draft", "submitted", "finance", "recommended", "approved"]
        for step in order[1:order.index(stage) + 1]:
            {"submitted": rec.action_submit, "finance": rec.action_finance,
             "recommended": rec.action_recommend, "approved": rec.action_approve}[step]()
        if stage == "finance":
            rec.finance_comment = "Budget line BL-02 has cover. Advance to be adjusted on return."
        out.append(f"{rec.name} {rec.state} {rec.total_cost:,.0f}")
    return "; ".join(out) or "already present"


print("  ", run("travel authorizations at each approval stage (Annex-30)", _travel))

env.cr.commit()
print("=== PROJECT STORY DATA DONE ===")
