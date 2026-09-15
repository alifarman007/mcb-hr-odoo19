"""Fix2: PR2's winning PO was RFQ-generated before evaluation ran, so it never
got its NOAL. Create the NOAL manually (mirrors action_create_po's own logic),
issue it, then confirm the PO."""
env = env  # noqa: F821


def run(name, fn):
    try:
        out = fn()
        print(f"OK   {name}")
        return out
    except Exception as e:
        print(f"FAIL {name}: {e}")
        return None


pr2 = env["mcb.purchase.request"].search([("delivery_point", "=", "GBViE Camp 12 Learning Centre")], limit=1)
vendor4 = env["res.partner"].search([("name", "=", "BD Builders Ltd")], limit=1)
po2 = env["purchase.order"].search(
    [("mcb_pr_id", "=", pr2.id), ("partner_id", "=", vendor4.id)], limit=1)
eval2 = env["mcb.vendor.evaluation"].search([("request_id", "=", pr2.id)], limit=1)
print("po2:", po2, po2.state, po2.mcb_noal_id, po2.amount_total)

if po2 and not po2.mcb_noal_id:
    def _make_noal():
        po2.mcb_evaluation_id = eval2.id
        noal = env["mcb.noal"].create({
            "order_id": po2.id, "vendor_id": po2.partner_id.id,
            "contract_price": po2.amount_total,
        })
        po2.mcb_noal_id = noal.id
        noal.action_issue()
        noal.action_acknowledge()
        return noal
    noal2 = run("PR2: create + issue + ack NOAL", _make_noal)

if po2 and po2.state == "draft":
    def _confirm():
        if not po2.mcb_checked_by_id:
            po2.action_mcb_check()
        if not po2.mcb_reviewed_by_id:
            po2.action_mcb_review()
        if not po2.mcb_approved_by_id:
            po2.action_mcb_approve()
        po2.button_confirm()
        return po2.state
    run("PR2 PO: confirm (NOAL now satisfied)", _confirm)

# procurement checklist for PR2/PO2
checklist2 = run("PR2 procurement checklist", lambda: env["mcb.procurement.checklist"].create({
    "request_id": pr2.id, "order_id": po2.id if po2 else False,
}))
if checklist2:
    for l in checklist2.line_ids:
        l.status = "yes"

env.cr.commit()
print("=== FIX2 DONE ===", po2.state if po2 else None)
