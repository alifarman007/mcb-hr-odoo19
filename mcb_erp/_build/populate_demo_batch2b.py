"""Addendum: real account.payment records (Money Receipt + Cheque Register
reports are bound to account.payment, not account.move; Batch 1's vouchers
were posted as plain journal entries so these two reports had nothing to show)."""
env = env  # noqa: F821


def run(name, fn):
    try:
        out = fn()
        print(f"OK   {name}")
        return out
    except Exception as e:
        print(f"FAIL {name}: {e}")
        return None


bank = env["account.journal"].browse(6)
vendor = env["res.partner"].search([("name", "=", "Gemini Furniture")], limit=1)
care = run("Partner: CARE Bangladesh (donor)", lambda: env["res.partner"].create({
    "name": "CARE Bangladesh", "is_company": True, "supplier_rank": 0, "customer_rank": 1,
}))

receipt = run("Money Receipt: inbound payment from CARE", lambda: env["account.payment"].create({
    "payment_type": "inbound", "partner_type": "customer", "partner_id": care.id,
    "journal_id": bank.id, "amount": 500000,
    "memo": "Donor contribution — CARE tranche 3 (Annex-01/31)",
}))
if receipt:
    run("Money Receipt: post", receipt.action_post)

cheque = run("Cheque payment: outbound to Gemini Furniture", lambda: env["account.payment"].create({
    "payment_type": "outbound", "partner_type": "supplier", "partner_id": vendor.id,
    "journal_id": bank.id, "amount": 90000,
    "payment_method_line_id": env.ref("account_check_printing.account_payment_method_check").id,
    "memo": "Payment — Gemini Furniture invoice GF-2201 (Annex-02)",
}))
if cheque:
    cheque.check_number = "1002345"
    run("Cheque payment: post", cheque.action_post)

env.cr.commit()
print("=== BATCH2B (payments) DONE ===")
