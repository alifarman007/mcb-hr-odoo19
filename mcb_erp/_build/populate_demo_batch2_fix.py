"""Fix: CE-gated actions check self.env.user.has_group(); the odoo-bin shell
env is bound to the superuser (uid=1), not the 'admin' login (uid=2) that
actually holds the CE group. Re-run the two CE-gated steps with_user(admin)."""
env = env  # noqa: F821


def run(name, fn):
    try:
        out = fn()
        print(f"OK   {name}")
        return out
    except Exception as e:
        print(f"FAIL {name}: {e}")
        return None


admin = env.ref("base.user_admin")
gbvie = env.ref("mcb_budget.demo_budget_gbvie")
rev = env["mcb.budget.revision"].search(
    [("budget_id", "=", gbvie.id), ("state", "=", "submitted")], limit=1)
print("rev:", rev, rev.state if rev else None)
if rev:
    run("Budget Revision: CE approve (as admin)", lambda: rev.with_user(admin).action_approve())

asset3 = env["account.asset"].search([("name", "ilike", "Photocopier")], limit=1)
print("asset3:", asset3, asset3.mcb_ce_disposal_approved if asset3 else None)
if asset3 and not asset3.mcb_ce_disposal_approved:
    run("Asset: CE-approve disposal (as admin)", lambda: asset3.with_user(admin).action_mcb_ce_approve_disposal())

env.cr.commit()
print("=== BATCH2 FIX DONE ===")
