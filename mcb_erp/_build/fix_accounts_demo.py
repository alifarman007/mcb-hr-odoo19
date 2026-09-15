"""Two fixes the Accounts tutorials need:

1. Relabel the remaining USD amounts to BDT (company currency is now BDT, but
   entries posted earlier still carry their old currency).
   NOTE: this relabels, it does not convert — demo figures only.
2. Create a DRAFT journal voucher so the Check / Review / Approve buttons are
   actually visible; on a posted voucher they are gone, which is why the
   approval screenshot had nothing to point at.
"""
from datetime import date

env = env  # noqa: F821

usd = env["res.currency"].search([("name", "=", "USD")], limit=1)
bdt = env["res.currency"].search([("name", "=", "BDT")], limit=1)

# ------------------------------------------------------------ 1. currency --
for table, model in [("account_move", "account.move"),
                     ("account_move_line", "account.move.line"),
                     ("account_payment", "account.payment"),
                     ("account_bank_statement_line", "account.bank.statement.line")]:
    try:
        env.cr.execute(
            f"UPDATE {table} SET currency_id=%s WHERE currency_id=%s AND company_id=1",
            (bdt.id, usd.id))
        print(f"  {model:32s} {env.cr.rowcount:4d} rows -> BDT")
    except Exception as e:
        env.cr.execute("ROLLBACK TO SAVEPOINT x") if False else None
        print(f"  {model:32s} skipped ({str(e)[:60]})")
env.invalidate_all()

# --------------------------------------------------- 2. draft voucher ------
misc = env["account.journal"].search(
    [("company_id", "=", 1), ("type", "=", "general"),
     ("name", "=", "Miscellaneous Operations")], limit=1)
exp = env["account.account"].search([("code", "=", "600000"), ("company_ids", "in", [1])], limit=1)
lia = env["account.account"].search([("code", "=", "201000"), ("company_ids", "in", [1])], limit=1)
analytic = env["account.analytic.account"].search([("name", "ilike", "GBViE")], limit=1)

existing = env["account.move"].search(
    [("company_id", "=", 1), ("move_type", "=", "entry"), ("state", "=", "draft"),
     ("ref", "like", "Fuel and transport")], limit=1)
if existing:
    jv = existing
    print("  draft voucher already present:", jv.id)
else:
    jv = env["account.move"].create({
        "move_type": "entry",
        "journal_id": misc.id,
        "date": date.today(),
        "ref": "Fuel and transport — Camp 12 field visits",
        "line_ids": [
            (0, 0, {"account_id": exp.id, "name": "Fuel and transport",
                    "debit": 8500, "credit": 0,
                    "analytic_distribution": {str(analytic.id): 100} if analytic else False}),
            (0, 0, {"account_id": lia.id, "name": "Payable — transport vendor",
                    "debit": 0, "credit": 8500}),
        ],
    })
    print("  created draft voucher:", jv.id, jv.ref)

print("  state:", jv.state, "| currency:", jv.currency_id.name,
      "| total:", jv.amount_total)
for f in ("mcb_checked_by_id", "mcb_reviewed_by_id", "mcb_approved_by_id"):
    if f in jv._fields:
        print(f"   {f}:", jv[f].name if jv[f] else "(empty — button will show)")

env.cr.commit()
print("DRAFT_JV_ID =", jv.id)
print("=== ACCOUNTS FIXES DONE ===")
