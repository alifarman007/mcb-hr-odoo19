"""Fill the two gaps the Accounts tutorials need:
   1. a vendor bill created FROM a purchase order (so 3-way match has something to show)
   2. BIN / TIN on the vendors that appear in the videos
"""
import traceback
env = env  # noqa: F821


def run(name, fn):
    try:
        with env.cr.savepoint():
            out = fn()
        print(f"OK   {name}")
        return out
    except Exception as e:
        print(f"FAIL {name}: {str(e)[:170]}")
        return None


# ---------------------------------------------------- BIN / TIN on vendors --
BIN_TIN = {
    "Gemini Furniture":       ("001234567-0101", "123456789012"),
    "Ready Mat":              ("002345678-0202", "234567890123"),
    "Modern Furnishing BD":   ("003456789-0303", "345678901234"),
    "BD Builders Ltd":        ("004567890-0404", "456789012345"),
    "CARE Bangladesh":        ("005678901-0505", "567890123456"),
}


def _bin_tin():
    n = 0
    for name, (bin_, tin) in BIN_TIN.items():
        p = env["res.partner"].search([("name", "=", name)], limit=1)
        if p:
            p.write({"mcb_bin_no": bin_, "mcb_tin_no": tin})
            n += 1
    return n


print("vendors updated with BIN/TIN:", run("BIN / TIN on demo vendors", _bin_tin))

# --------------------------------------- vendor bill created from the PO ----
po = env["purchase.order"].browse(18)   # Gemini Furniture, confirmed
print("PO:", po.name, po.partner_id.name, po.state, po.amount_total)


def _receive_goods():
    """Validate the incoming shipment so the 3-way match has a receipt to match."""
    done = []
    for pick in po.picking_ids.filtered(lambda p: p.state not in ("done", "cancel")):
        for mv in pick.move_ids:
            mv.quantity = mv.product_uom_qty
        pick.move_ids.picked = True
        pick.button_validate()
        done.append(pick.name)
    return done or "no pickings to receive"


run("receive the goods (GRN)", _receive_goods)


def _make_bill():
    existing = env["account.move"].search(
        [("invoice_origin", "like", po.name), ("move_type", "=", "in_invoice")], limit=1)
    if existing:
        return existing
    po.action_create_invoice()
    bill = env["account.move"].search(
        [("invoice_origin", "like", po.name), ("move_type", "=", "in_invoice")],
        order="id desc", limit=1)
    if bill:
        bill.invoice_date = bill.invoice_date or env["ir.fields.converter"] and __import__(
            "datetime").date.today()
        bill.ref = f"GF-2201 / {po.name}"
    return bill


bill = run("create vendor bill from the PO", _make_bill)
if bill:
    print("   bill:", bill.name or "(draft)", "| origin:", bill.invoice_origin,
          "| total:", bill.amount_total, "| state:", bill.state)
    for f in ("release_to_pay", "release_to_pay_manual", "invoice_origin"):
        if f in bill._fields:
            print(f"   3-way field {f}:", bill[f])
    if bill.state == "draft":
        run("post the vendor bill", bill.action_post)
        print("   after post:", bill.name, bill.state)

env.cr.commit()
print("=== ACCOUNTS DEMO DATA DONE ===")
