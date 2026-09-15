"""Fix-up pass: admin groups (correct field name) + PR2 with 3 vendors."""
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


def _grant_groups():
    admin = env.ref("base.user_admin")
    for xmlid in [
        "mcb_hr_employee.group_mcb_ce",
        "mcb_hr_employee.group_mcb_pm",
        "mcb_hr_employee.group_mcb_rc",
        "mcb_account.group_mcb_finance_manager",
        "mcb_purchase.group_mcb_proc_manager",
    ]:
        grp = env.ref(xmlid, raise_if_not_found=False)
        if grp:
            admin.write({"group_ids": [(4, grp.id)]})
    return "granted"


run("grant admin groups (fixed)", _grant_groups)

pr2 = env["mcb.purchase.request"].search([("delivery_point", "=", "GBViE Camp 12 Learning Centre")], limit=1)
vendor4 = env["res.partner"].search([("name", "=", "BD Builders Ltd")], limit=1)
vendor5 = env["res.partner"].search([("name", "=", "Coxs Bazar Construction Co")], limit=1)
vendor6 = run("create vendor6 (civil)", lambda: env["res.partner"].create({
    "name": "Ukhiya Engineering Works", "supplier_rank": 1, "is_company": True}))

print("PR2 state:", pr2.state if pr2 else None, "orders:", pr2.order_ids if pr2 else None)


def _finish_pr2_rfqs():
    if pr2.state == "sent_pc" and not pr2.order_ids:
        wiz = env["mcb.pr.rfq.wizard"].create({
            "request_id": pr2.id,
            "vendor_ids": [(6, 0, [vendor4.id, vendor5.id, vendor6.id])],
        })
        wiz.action_generate()
    return pr2.state, pr2.order_ids.mapped("name")


run("PR2: create 3-vendor RFQs", _finish_pr2_rfqs)

ta2 = env["mcb.technical.analysis"].search([("request_id", "=", pr2.id)], limit=1)
if not ta2:
    ta2 = run("PR2 technical analysis", lambda: env["mcb.technical.analysis"].create({
        "request_id": pr2.id, "ta_type": "ta2"}))
if ta2 and not ta2.line_ids:
    run("PR2 TA: fill vendors", ta2.action_fill_vendors)
if ta2:
    ta2.line_ids.write({"spec_compliance": True, "delivery_compliance": True, "result": "pass"})
    if ta2.state != "done":
        run("PR2 TA: done", ta2.action_done)

cs2 = env["mcb.comparative.statement"].search([("request_id", "=", pr2.id)], limit=1)
if not cs2:
    cs2 = run("PR2 comparative statement", lambda: env["mcb.comparative.statement"].create({
        "request_id": pr2.id, "technical_analysis_id": ta2.id if ta2 else False,
        "circular_date": today - timedelta(days=25),
        "opening_date": today - timedelta(days=12),
        "pc_comment": "<p>BD Builders Ltd quoted the lowest price and has prior "
                      "satisfactory experience with MCB. Recommended for NOAL.</p>",
    }))
if cs2 and not cs2.vendor_line_ids:
    run("PR2 CS: fill vendors", cs2.action_fill_vendors)
if cs2 and cs2.state != "done":
    run("PR2 CS: done", cs2.action_done)

eval2 = env["mcb.vendor.evaluation"].search([("request_id", "=", pr2.id)], limit=1)
if not eval2:
    eval2 = run("PR2 evaluation", lambda: env["mcb.vendor.evaluation"].create({
        "request_id": pr2.id, "cs_id": cs2.id if cs2 else False, "eval_type": "eval2"}))
if eval2 and not eval2.line_ids:
    for v in cs2.vendor_line_ids.mapped("vendor_id"):
        env["mcb.vendor.evaluation.line"].create({
            "evaluation_id": eval2.id, "vendor_id": v.id,
            "price_score": 38 if v == vendor4 else 30,
            "quality_score": 28, "delivery_score": 14, "experience_score": 14,
        })
    eval2.recommended_vendor_id = vendor4.id
if eval2 and eval2.state != "done":
    run("PR2 evaluation: done", eval2.action_done)
if eval2 and eval2.state == "done":
    po2_final = env["purchase.order"].search(
        [("mcb_pr_id", "=", pr2.id), ("partner_id", "=", vendor4.id), ("state", "=", "draft")], limit=1)
    if not po2_final:
        run("PR2 evaluation: create PO (+draft NOAL)", eval2.action_create_po)
        po2_final = env["purchase.order"].search(
            [("mcb_pr_id", "=", pr2.id), ("partner_id", "=", vendor4.id), ("state", "=", "draft")], limit=1)
    print("po2_final:", po2_final, po2_final.amount_total if po2_final else None)

    noal2 = po2_final.mcb_noal_id if po2_final else False
    if noal2 and noal2.state == "draft":
        def _issue_noal2():
            noal2.contract_price = po2_final.amount_total
            noal2.action_issue()
            return noal2.state
        run("PR2 NOAL: issue", _issue_noal2)
    if noal2 and noal2.state == "issued":
        run("PR2 NOAL: acknowledge", noal2.action_acknowledge)

    if po2_final and po2_final.state == "draft":
        def _confirm_po2():
            po2_final.action_mcb_check()
            po2_final.action_mcb_review()
            po2_final.action_mcb_approve()
            po2_final.button_confirm()
            return po2_final.state
        run("PR2 PO: 4-level approve + confirm (NOAL satisfied)", _confirm_po2)

env.cr.commit()
print("=== FIX1 DONE ===")
