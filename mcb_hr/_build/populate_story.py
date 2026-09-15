"""Story demo data for the HR video tutorial series.

One continuous cast so every video follows the same person:
  REQ/2026/0001 "MEAL Officer" -> 7 applicants sit exams -> Rashedul Karim ranks #1
  -> hired as MEAL-001 -> applies for leave -> claims TA/DA -> appears on payroll.
Plus a separate short-notice resignation (Farzana Akter) to demo the exit flow.

Every step runs inside a SAVEPOINT so one failure cannot poison the transaction
(an IntegrityError otherwise aborts the whole batch at commit time).
"""
import traceback
from datetime import date, timedelta

env = env  # noqa: F821
today = date.today()


def run(name, fn):
    try:
        with env.cr.savepoint():
            out = fn()
        print(f"OK   {name}")
        return out
    except Exception as e:
        print(f"FAIL {name}: {str(e)[:160]}")
        return None


req = env["mcb.hr.staff.requisition"].browse(1)
print("Requisition:", req.name, "|", req.position_title, "| state:", req.state)

# ---------------------------------------------------------- JOB POSITION ---
if not req.job_id:
    def _mk_job():
        job = env["hr.job"].create({
            "name": "MEAL Officer (Cox's Bazar)",
            "department_id": req.department_id.id if req.department_id else False,
            "no_of_recruitment": req.number_of_vacancies or 1,
        })
        req.job_id = job.id
        return job
    run("link requisition -> job position", _mk_job)

job = req.job_id
print("job:", job.name if job else None)

# ------------------------------------------------------------ APPLICANTS ---
# Rashedul is given the top score so he ranks #1 and the story is unambiguous.
CAST = [
    ("Rashedul Karim", "Abdul Karim", "Rahima Begum", "1990123456789",
     "MSS in Development Studies, University of Chittagong (2014)",
     "3 years MEAL Assistant, BRAC; 2 years Data Officer, Save the Children",
     46, 18, 14, 14),
    ("Nusrat Jahan", "Md. Shahjahan", "Kulsum Ara", "1992223456789",
     "MSc in Statistics, University of Dhaka (2016)",
     "4 years M&E Officer, Oxfam Bangladesh",
     40, 16, 12, 12),
    ("Mahmudul Hasan", "Nurul Hasan", "Salma Khatun", "1991323456789",
     "MBA, Premier University Chittagong (2015)",
     "3 years Programme Officer, Caritas",
     38, 15, 11, 11),
    ("Sadia Islam", "Rafiqul Islam", "Nasima Akter", "1993423456789",
     "BSS in Economics, National University (2017)",
     "2 years Field Monitor, World Vision",
     35, 14, 10, 10),
    ("Tanvir Ahmed", "Jashim Uddin", "Rokeya Begum", "1994523456789",
     "BBA in Management, IIUC (2018)",
     "1 year Intern, local NGO",
     30, 12, 9, 8),
]

exam_day = today - timedelta(days=20)
EXAM = {
    "mcb_exam_date": exam_day,
    "mcb_exam_time": "10:00 AM",
    "mcb_exam_venue": "MCB Head Office, Goldighirpar, Cox's Bazar",
    "mcb_attended_written": True,
    "mcb_attended_oral": True,
}


def _mk_applicants():
    made = env["hr.applicant"]
    for i, (nm, fa, mo, nid, edu, exp, w, c, sk, kn) in enumerate(CAST, start=1):
        a = env["hr.applicant"].search(
            [("partner_name", "=", nm), ("mcb_requisition_id", "=", req.id)], limit=1)
        if not a:
            a = env["hr.applicant"].create({
                "partner_name": nm,
                "job_id": job.id if job else False,
                "mcb_requisition_id": req.id,
                "email_from": f"{nm.split()[0].lower()}.mcb@example.com",
                "mcb_father_name": fa,
                "mcb_mother_name": mo,
                "mcb_nid": nid,
                "mcb_present_address": "Cox's Bazar Sadar, Cox's Bazar",
                "mcb_permanent_address": "Ukhiya, Cox's Bazar",
                "mcb_education_summary": edu,
                "mcb_experience_summary": exp,
            })
        vals = dict(EXAM)
        vals.update({"mcb_written_score": w, "mcb_computer_score": c,
                     "mcb_oral_score_skills": sk, "mcb_oral_score_knowledge": kn})
        a.write(vals)
        made |= a
    return made


apps = run("create/refresh 5 MEAL Officer applicants with marks", _mk_applicants)

# fold in any pre-existing applicants on this requisition so the merit list is coherent
others = env["hr.applicant"].search([("mcb_requisition_id", "=", req.id)])
if others:
    def _fix_others():
        for a in others:
            if a.mcb_written_score or a.mcb_total_score:
                a.write(EXAM)
        return others
    run("stamp exam details on pre-existing applicants", _fix_others)

all_apps = env["hr.applicant"].search([("mcb_requisition_id", "=", req.id)])


def _issue_cards():
    n = 0
    for a in all_apps:
        if not a.mcb_admit_card_issued:
            a.action_issue_admit_card()
            n += 1
    return n


run("issue admit cards", _issue_cards)

if all_apps:
    run("compute merit ranking", all_apps.action_compute_merit_rank)
    winner = all_apps.filtered(lambda a: a.partner_name == "Rashedul Karim")
    if winner and not winner.mcb_selected:
        run("mark Rashedul Karim selected", winner.action_mark_selected)
    print("   --- MERIT LIST ---")
    for a in all_apps.sorted(key=lambda x: x.mcb_merit_rank or 99):
        print(f"   rank {a.mcb_merit_rank}: {a.partner_name:22s} "
              f"W{a.mcb_written_score:.0f} C{a.mcb_computer_score:.0f} "
              f"O{a.mcb_oral_score:.0f} = {a.mcb_total_score:.0f}"
              f"{'  <-- SELECTED' if a.mcb_selected else ''}  [{a.mcb_admit_card_id or '-'}]")

# ------------------------------------------------------------ THE HERO -----
rashedul = env["hr.employee"].search([("mcb_employee_code", "=", "MEAL-001")], limit=1)
print("hero employee:", rashedul.name, "| grade:",
      rashedul.version_id.mcb_grade_id.name if rashedul.version_id else None)

# ---------------------------------------------------------------- LEAVE ----
def _leave_type(pattern):
    return env["hr.leave.type"].search(
        [("name", "ilike", pattern),
         ("company_id", "in", [rashedul.company_id.id, False])], limit=1)


annual = _leave_type("Annual")
casual = _leave_type("Casual")
print("leave types:", annual.name if annual else None, "|", casual.name if casual else None)


def _allocate(ltype, days, label):
    al = env["hr.leave.allocation"].search(
        [("employee_id", "=", rashedul.id), ("holiday_status_id", "=", ltype.id)], limit=1)
    if not al:
        al = env["hr.leave.allocation"].create({
            "employee_id": rashedul.id,
            "holiday_status_id": ltype.id,
            "number_of_days": days,
            "name": label,
        })
    if al.state == "confirm":
        al.action_approve()
    return al


def _mk_leave(ltype, d_from, d_to, reason, target_state):
    lv = env["hr.leave"].create({
        "employee_id": rashedul.id,
        "holiday_status_id": ltype.id,
        "request_date_from": d_from,
        "request_date_to": d_to,
        "name": reason,
    })
    if lv.state == "draft":
        lv.action_confirm()
    if target_state in ("validate1", "validate"):
        lv.action_approve()
    if target_state == "validate":
        lv.action_validate()
    return lv


if annual:
    run("annual leave allocation (20 days)", lambda: _allocate(annual, 20, "Annual entitlement FY 26-27"))
    lv_pending = run("leave AWAITING APPROVAL (approve-button scene)",
                     lambda: _mk_leave(annual, today + timedelta(days=7), today + timedelta(days=9),
                                       "Family wedding in Chittagong", "confirm"))
    if lv_pending:
        print("   pending leave:", lv_pending.state, lv_pending.number_of_days, "days")

if casual:
    run("casual leave allocation (10 days)", lambda: _allocate(casual, 10, "Casual entitlement FY 26-27"))
    lv_done = run("leave FULLY APPROVED (after-approval scene)",
                  lambda: _mk_leave(casual, today - timedelta(days=10), today - timedelta(days=10),
                                    "Personal work", "validate"))
    if lv_done:
        print("   approved leave:", lv_done.state, lv_done.number_of_days, "days")

# -------------------------------------------------------------- EXPENSE ----
cat_perdiem = env["product.product"].search([("name", "ilike", "Per Diem")], limit=1) or \
    env["product.product"].search([("can_be_expensed", "=", True)], limit=1)


def _mk_expense():
    exp = env["hr.expense"].search(
        [("employee_id", "=", rashedul.id), ("name", "ilike", "Camp 12 monitoring")], limit=1)
    if not exp:
        exp = env["hr.expense"].create({
            "name": "Camp 12 monitoring field visit — TA/DA",
            "employee_id": rashedul.id,
            "product_id": cat_perdiem.id if cat_perdiem else False,
            "date": today - timedelta(days=5),
            "mcb_is_taDa": True,
            "mcb_distance_km": 62,
            "mcb_overnight_stay": True,
            "mcb_field_visit_hours": 8,
            "mcb_project_code": "FDMN",
            "mcb_donor": "UNFPA",
            "total_amount_currency": 1500,
        })
    exp.action_apply_per_diem()
    return exp


expense = run("TA/DA expense for Rashedul (62 km + overnight)", _mk_expense)
if expense:
    print("   expense:", expense.total_amount_currency, "| grade:",
          expense.mcb_grade_id.name if expense.mcb_grade_id else None,
          "| needs CE:", expense.mcb_requires_ce_approval)

# ---------------------------------------------------------- RESIGNATION ----
farzana = env["hr.employee"].search([("mcb_employee_code", "=", "CORE-003")], limit=1)


def _mk_resignation():
    r = env["mcb.hr.resignation"].search(
        [("employee_id", "=", farzana.id), ("state", "!=", "closed")], limit=1)
    if not r:
        r = env["mcb.hr.resignation"].create({
            "employee_id": farzana.id,
            "submission_date": today,
            # deliberately SHORT notice: permanent staff need 60 days, giving ~20
            "intended_last_day": today + timedelta(days=20),
            "reason": "resign_voluntary",
            "notes": "<p>Resigning to join another organisation closer to family.</p>",
            "leave_encashment_days": 8,
        })
    if r.state == "draft":
        r.action_submit()
    return r


resign = run("short-notice resignation for Farzana Akter (submitted)", _mk_resignation)
if resign:
    print("   resignation:", resign.name, "| state:", resign.state,
          "| notice req:", resign.required_notice_days,
          "| actual:", resign.actual_notice_days,
          "| short by:", resign.notice_short_by_days,
          "| settlement:", resign.final_settlement_total)

env.cr.commit()
print("=== STORY DATA DONE ===")
