from odoo import api, models, _
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = "account.move"

    def _post(self, soft=True):
        """BUD-004 (block/warn on overage) + BUD-008 (budget lock) enforced at posting
        of vendor bills / expenditure entries carrying a budgeted analytic account."""
        self._mcb_check_budget()
        return super()._post(soft=soft)

    def _mcb_check_budget(self):
        BudgetLine = self.env["budget.line"].sudo()
        for move in self:
            if move.move_type not in ("in_invoice", "entry"):
                continue
            for line in move.line_ids:
                if line.display_type not in ("product", False) or not line.debit:
                    continue
                if line.account_id.account_type not in (
                        "expense", "expense_direct_cost", "expense_depreciation"):
                    continue
                candidates = BudgetLine.search([
                    ("budget_analytic_state", "=", "confirmed"),
                    ("date_from", "<=", move.date),
                    ("date_to", ">=", move.date),
                    ("company_id", "=", move.company_id.id),
                ])
                for aid_str, pct in (line.analytic_distribution or {}).items():
                    for aid in str(aid_str).split(","):
                        blines = candidates.filtered(
                            lambda b: self._mcb_line_matches_analytic(b, int(aid)))
                        for bl in blines:
                            budget = bl.budget_analytic_id
                            if budget.mcb_locked:
                                raise UserError(_(
                                    "BUD-008 — budget '%s' is locked by the CE; no further "
                                    "expenditure may be posted against it.", budget.name))
                            amount = line.debit * (pct / 100.0)
                            new_total = bl.achieved_amount + amount
                            if new_total > bl.budget_amount and bl.budget_amount > 0:
                                msg = _(
                                    "BUD-004 — posting %(amt).2f against budget line '%(line)s' "
                                    "exceeds the approved budget (%(ach).2f + %(amt).2f > %(bud).2f).",
                                    amt=amount, line=bl.display_name,
                                    ach=bl.achieved_amount, bud=bl.budget_amount)
                                if budget.mcb_overage_policy == "block":
                                    raise UserError(msg)
                                move.message_post(body=msg)

    @api.model
    def _mcb_line_matches_analytic(self, budget_line, analytic_id):
        """A budget.line references analytic accounts through plan-mixin columns."""
        for fname, field in budget_line._fields.items():
            if field.type == "many2one" and field.comodel_name == "account.analytic.account":
                if budget_line[fname].id == analytic_id:
                    return True
        return False
