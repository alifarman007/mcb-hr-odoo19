"""Fix3: PR1's confirmed PO doesn't match the Vendor Evaluation's recommended
vendor. eval1.recommended_vendor_id = Gemini Furniture (highest score, 87 —
also what the Comparative Statement narrative says), but the original demo
script's `search(mcb_pr_id=pr1, state='draft', limit=1)` had no partner filter
and no explicit order, so it grabbed PO 20 (Modern Furnishing BD, highest id)
instead of PO 18 (Gemini Furniture) and confirmed the wrong one. Revert PO 20
to draft (a normal losing RFQ, like PR2's pattern) and confirm PO 18 instead."""
env = env  # noqa: F821


def run(name, fn):
    try:
        out = fn()
        print(f"OK   {name}")
        return out
    except Exception as e:
        print(f"FAIL {name}: {e}")
        return None


po20 = env["purchase.order"].browse(20)  # Modern Furnishing BD — wrongly confirmed
po18 = env["purchase.order"].browse(18)  # Gemini Furniture — the actual recommended winner
print("before:", po20.name, po20.state, "|", po18.name, po18.state)

if po20.state != "draft":
    run("PO20 (Modern Furnishing BD): revert to draft", lambda: po20.write({
        "state": "draft", "mcb_checked_by_id": False,
        "mcb_reviewed_by_id": False, "mcb_approved_by_id": False,
    }))

if po18.state == "draft":
    def _confirm_po18():
        po18.action_mcb_check()
        po18.action_mcb_review()
        po18.action_mcb_approve()
        po18.button_confirm()
        return po18.state
    run("PO18 (Gemini Furniture): 4-level approve + confirm", _confirm_po18)

checklist1 = env["mcb.procurement.checklist"].search([("request_id", "=", 1)], limit=1)
if checklist1 and checklist1.order_id.id != po18.id:
    run("Procurement Checklist 1: re-link to PO18", lambda: checklist1.write({"order_id": po18.id}))

env.cr.commit()
print("after:", po20.name, po20.state, "|", po18.name, po18.state)
print("=== FIX3 DONE ===")
