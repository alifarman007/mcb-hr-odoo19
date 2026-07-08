from odoo import fields, models, _
from odoo.exceptions import UserError


class McbYearEndWizard(models.TransientModel):
    """PER-002 — year-end fund-balance closing journal (plan-review finding 9).

    Posts one journal entry that transfers the fiscal year's net surplus/deficit
    per project/donor analytic account into the Fund Balance (NGO) equity account.
    """
    _name = "mcb.year.end.wizard"
    _inherit = ["mcb.fy.mixin"]
    _description = "Year-End Fund Balance Closing (PER-002)"

    fiscal_date = fields.Date(
        string="Any date inside the FY to close", required=True,
        default=fields.Date.context_today,
    )
    journal_id = fields.Many2one(
        "account.journal", domain="[('type', '=', 'general')]", required=True,
        default=lambda s: s.env["account.journal"].search([("type", "=", "general")], limit=1),
    )

    def action_close(self):
        self.ensure_one()
        date_from, date_to = self._mcb_fy_bounds(self.fiscal_date)
        company = self.env.company
        fund_acc = self.env["account.account"].search(
            [("code", "=", "300190"), ("company_ids", "in", company.id)], limit=1)
        if not fund_acc:
            raise UserError(_("Fund Balance account 300190 not found — reinstall mcb_account."))
        lines = self.env["account.move.line"].search([
            ("company_id", "=", company.id),
            ("parent_state", "=", "posted"),
            ("date", ">=", date_from), ("date", "<=", date_to),
            ("account_id.account_type", "in",
             ("income", "income_other", "expense", "expense_depreciation",
              "expense_direct_cost")),
        ])
        per_analytic = {}
        for l in lines:
            keys = list((l.analytic_distribution or {}).keys()) or ["none"]
            for k in keys:
                per_analytic.setdefault(k, 0.0)
                per_analytic[k] += l.balance / len(keys)
        move_lines = []
        total = 0.0
        for key, bal in per_analytic.items():
            if abs(bal) < 0.005:
                continue
            dist = {key: 100} if key != "none" else False
            # income accounts carry credit balances (negative balance) → surplus
            move_lines.append((0, 0, {
                "account_id": fund_acc.id,
                "name": _("FY %s fund balance", self._mcb_fy_label(self.fiscal_date)),
                "debit": -bal if bal < 0 else 0.0,
                "credit": bal if bal > 0 else 0.0,
                "analytic_distribution": dist,
            }))
            total += bal
        if not move_lines:
            raise UserError(_("Nothing to close for this fiscal year."))
        counter_acc = self.env["account.account"].search(
            [("account_type", "=", "equity_unaffected"),
             ("company_ids", "in", company.id)], limit=1) or fund_acc
        move_lines.append((0, 0, {
            "account_id": counter_acc.id,
            "name": _("FY %s closing counterpart", self._mcb_fy_label(self.fiscal_date)),
            "debit": total if total > 0 else 0.0,
            "credit": -total if total < 0 else 0.0,
        }))
        move = self.env["account.move"].create({
            "move_type": "entry",
            "journal_id": self.journal_id.id,
            "date": date_to,
            "ref": _("Year-end fund balance closing %s", self._mcb_fy_label(self.fiscal_date)),
            "line_ids": move_lines,
        })
        return {
            "type": "ir.actions.act_window",
            "res_model": "account.move",
            "res_id": move.id,
            "view_mode": "form",
        }
