"""Story data for the MCB Purchase / Procurement click-path tutorials.

Gives the recorder something to point at in EVERY state of the 11-step process:
  * one PR sitting in each approval state, so Confirm / Accounts Check /
    CE Approve / Send to PC / Create RFQs are each visible somewhere;
  * one live procurement (PR-E) with 3 RFQs out and draft Opening Sheet,
    Technical Analysis, Comparative Statement and Evaluation;
  * PR 4 (CARE / GBViE civil works, IFT) stays the finished end-to-end example.

Every step is wrapped in a savepoint - an IntegrityError otherwise poisons the
whole transaction and the final commit silently rolls everything back.
"""
from datetime import date, timedelta

env = env  # noqa: F821

GBVIE_ANALYTIC = 36        # GBViE - Gender Based Violence in Emergency
BUDGET = 3                 # budget.analytic - GBViE-CARE FY 25-26
BL_NFI = 12                # budget.line BL-04 NFI Distribution (780,000)
BL_RENT = 11               # budget.line BL-03 Office Rent & Utilities (180,000)
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


def vendor(name):
    return env["res.partner"].search([("name", "=", name)], limit=1)


PR = env["mcb.purchase.request"]

# ------------------------------------------------- 1. tidy the old PR 1 ----
def _dedupe_pr1():
    """PR 1 was loaded four times, so it carries four copies of every line.
    Keep one of each and raise the quantities so the total (and therefore the
    IFT method + the NOAL that hangs off it) does not move."""
    pr = PR.browse(1)
    if not pr.exists():
        return "PR 1 missing"
    keep = {}
    for line in pr.line_ids:
        keep.setdefault(line.name, []).append(line)
    dropped = 0
    for name, lines in keep.items():
        n = len(lines)
        first = lines[0]
        first.quantity = first.quantity * n
        for extra in lines[1:]:
            extra.unlink()
            dropped += 1
    return f"{dropped} duplicate lines removed, total now {pr.amount_total:,.0f}"


print("  ", run("dedupe PR: 0001/26-27 item lines", _dedupe_pr1))

# ------------------------------- 2. one PR sitting in each approval state --
STAGES = [
    ("draft", "Hygiene kits for the Camp 19 distribution", BL_NFI, [
        ("Hygiene kit (family, 1 month)", "Soap, detergent, sanitary napkins, bucket, mug",
         300, 500.0),
    ]),
    ("confirmed", "Learning centre furniture, Camp 12", BL_NFI, [
        ("Student bench-desk (wooden, 2 seat)", "Seasoned mango wood, varnished", 60, 2200.0),
        ("Teacher table and chair set", "Steel frame, laminate top", 6, 8500.0),
    ]),
    ("accounts", "Generator servicing and fuel, Ukhiya field office", BL_RENT, [
        ("Generator servicing (15 KVA)", "Oil, filter, load test - quarterly contract",
         4, 9000.0),
        ("Diesel", "Litres, delivered to the field office", 1200, 108.0),
    ]),
    ("approved", "Solar lights for the women-friendly spaces", BL_NFI, [
        ("Solar street light, 40W", "Pole, panel, battery, 2-year warranty", 24, 9800.0),
    ]),
    ("sent_pc", "Tube-well installation, host community, Ukhiya", BL_NFI, [
        ("Deep tube-well with platform", "6 inch bore, hand pump, concrete apron",
         6, 68000.0),
    ]),
]

made = {}


def _make_stage(stage, purpose, budget_line, lines):
    def _fn():
        existing = PR.search([("delivery_point", "=", purpose)], limit=1)
        if existing:
            return existing
        pr = PR.create({
            "project_analytic_id": GBVIE_ANALYTIC,
            "donor": "CARE",
            "budget_id": BUDGET,
            "budget_line_id": budget_line,
            "date_request": TODAY - timedelta(days=12),
            "deadline": TODAY + timedelta(days=18),
            "delivery_point": purpose,
            "contact_person": "Aminul Haque",
            "contact_phone": "01711-000002",
            "line_ids": [(0, 0, {
                "name": n, "specification": spec, "quantity": qty,
                "price_unit": price, "uom_id": 1,
            }) for n, spec, qty, price in lines],
        })
        # walk it forward to the state this record is here to demonstrate
        order = ["draft", "confirmed", "accounts", "approved", "sent_pc"]
        for step in order[1:order.index(stage) + 1]:
            {"confirmed": pr.action_confirm,
             "accounts": pr.action_accounts_check,
             "approved": pr.action_ce_approve,
             "sent_pc": pr.action_send_pc}[step]()
        return pr
    return _fn


for stage, purpose, bl, lines in STAGES:
    pr = run(f"PR in state '{stage}' - {purpose[:40]}", _make_stage(stage, purpose, bl, lines))
    if pr:
        made[stage] = pr
        print(f"     {pr.name}  {pr.state:10s} {pr.amount_total:>12,.0f}  "
              f"{pr.procurement_method}  min quotes={pr.min_quotations}")

# --------------------------- 3. take the last one out to three vendors -----
live = made.get("sent_pc")
VENDORS = ["Coxs Bazar Construction Co", "Ukhiya Engineering Works", "BD Builders Ltd"]


def _rfqs():
    if not live:
        return "no live PR"
    if live.order_ids:
        return f"already has {len(live.order_ids)} RFQs"
    partners = env["res.partner"]
    for nm in VENDORS:
        partners |= vendor(nm)
    wiz = env["mcb.pr.rfq.wizard"].create({
        "request_id": live.id, "vendor_ids": [(6, 0, partners.ids)]})
    wiz.action_generate()
    return ", ".join(live.order_ids.mapped("name"))


print("  ", run("generate 3 RFQs from the live PR", _rfqs))

# ------------------- 4. draft opening sheet / TA / CS / evaluation on it ----
def _opening():
    if not live:
        return "no live PR"
    sheet = env["mcb.opening.sheet"].search([("request_id", "=", live.id)], limit=1)
    if sheet:
        return sheet.name
    sheet = env["mcb.opening.sheet"].create({
        "request_id": live.id,
        "member_ids": [(6, 0, env["res.users"].search([("login", "in",
                        ("admin", "rashedul"))]).ids)],
    })
    sheet.action_fill_bidders()
    for i, ln in enumerate(sheet.line_ids):
        ln.security_submitted = True
        ln.remarks = ["Sealed, signed by both members", "Sealed", "Sealed"][i % 3]
    return f"{sheet.name} with {len(sheet.line_ids)} bidders"


print("  ", run("draft Opening Sheet (Step 4)", _opening))


def _tech():
    if not live:
        return "no live PR"
    ta = env["mcb.technical.analysis"].search([("request_id", "=", live.id)], limit=1)
    if ta:
        return ta.name
    ta = env["mcb.technical.analysis"].create({"request_id": live.id, "ta_type": "ta1"})
    ta.action_fill_vendors()
    for i, ln in enumerate(ta.line_ids):
        ln.spec_compliance = i != 2
        ln.delivery_compliance = True
        ln.result = "fail" if i == 2 else "pass"
        ln.remarks = ("Bore depth below specification" if i == 2
                      else "Meets the 6 inch bore and apron specification")
    return f"{ta.name} - {len(ta.passed_vendors())} of {len(ta.line_ids)} vendors passed"


print("  ", run("draft Technical Analysis (Step 5)", _tech))


def _cs():
    if not live:
        return "no live PR"
    cs = env["mcb.comparative.statement"].search([("request_id", "=", live.id)], limit=1)
    if cs:
        return cs.name
    ta = env["mcb.technical.analysis"].search([("request_id", "=", live.id)], limit=1)
    cs = env["mcb.comparative.statement"].create({
        "request_id": live.id,
        "technical_analysis_id": ta.id if ta else False,
        "circular_date": TODAY - timedelta(days=10),
        "opening_date": TODAY - timedelta(days=3),
        "pc_comment": "<p>Three quotations received against an RFP. "
                      "Rates compared per unit, delivery and warranty verified.</p>",
    })
    cs.action_fill_vendors()
    return f"{cs.name} with {len(cs.vendor_line_ids)} vendor columns"


print("  ", run("draft Comparative Statement (Step 6)", _cs))


def _eval():
    if not live:
        return "no live PR"
    ev = env["mcb.vendor.evaluation"].search([("request_id", "=", live.id)], limit=1)
    if ev:
        return ev.name
    cs = env["mcb.comparative.statement"].search([("request_id", "=", live.id)], limit=1)
    ta = env["mcb.technical.analysis"].search([("request_id", "=", live.id)], limit=1)
    passed = ta.passed_vendors() if ta else live.order_ids.mapped("partner_id")
    scores = [(38, 28, 14, 13), (34, 29, 13, 12)]
    ev = env["mcb.vendor.evaluation"].create({
        "request_id": live.id,
        "cs_id": cs.id if cs else False,
        "eval_type": "eval1",
        "line_ids": [(0, 0, {
            "vendor_id": v.id, "price_score": s[0], "quality_score": s[1],
            "delivery_score": s[2], "experience_score": s[3],
        }) for v, s in zip(passed, scores)],
    })
    return f"{ev.name} scoring {len(ev.line_ids)} vendors out of 100"


print("  ", run("draft Vendor Evaluation (Step 7)", _eval))

env.cr.commit()
print("=== PROCUREMENT STORY DATA DONE ===")
