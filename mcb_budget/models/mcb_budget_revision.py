from odoo import api, fields, models, _
from odoo.exceptions import UserError


class McbBudgetRevision(models.Model):
    """BUD-005 — budget reallocation; CE approval mandatory when > 10% of the line."""
    _name = "mcb.budget.revision"
    _description = "MCB Budget Revision"
    _inherit = ["mail.thread"]

    name = fields.Char(default="New", copy=False, readonly=True)
    budget_id = fields.Many2one("budget.analytic", required=True)
    line_id = fields.Many2one("budget.line", required=True,
                              domain="[('budget_analytic_id', '=', budget_id)]")
    old_amount = fields.Monetary(related="line_id.budget_amount", string="Current Amount",
                                 currency_field="currency_id")
    new_amount = fields.Monetary(required=True, currency_field="currency_id")
    delta_pct = fields.Float(compute="_compute_delta", store=True, string="Change %")
    requires_ce = fields.Boolean(compute="_compute_delta", store=True,
                                 string="CE Approval Required (>10%)")
    reason = fields.Text(required=True)
    currency_id = fields.Many2one("res.currency", default=lambda s: s.env.company.currency_id)
    state = fields.Selection([
        ("draft", "Draft"), ("submitted", "Submitted"), ("approved", "Approved"),
        ("rejected", "Rejected"),
    ], default="draft", tracking=True)

    @api.depends("old_amount", "new_amount")
    def _compute_delta(self):
        for rec in self:
            base = rec.old_amount or 1.0
            rec.delta_pct = abs(rec.new_amount - rec.old_amount) / abs(base) * 100.0
            rec.requires_ce = rec.delta_pct > 10.0

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].sudo().next_by_code(
                    "mcb.budget.revision") or "REV/000"
        return super().create(vals_list)

    def action_submit(self):
        self.write({"state": "submitted"})

    def action_approve(self):
        for rec in self:
            if rec.requires_ce and not self.env.user.has_group(
                    "mcb_hr_employee.group_mcb_ce"):
                raise UserError(_(
                    "BUD-005 — this reallocation changes the line by %.1f%% (>10%%); "
                    "only the Chief Executive group can approve it.", rec.delta_pct))
            rec.line_id.budget_amount = rec.new_amount
            rec.state = "approved"
            rec.budget_id.message_post(body=_(
                "Budget line '%s' revised %s → %s (%s). Reason: %s",
                rec.line_id.display_name, rec.old_amount, rec.new_amount,
                rec.name, rec.reason))

    def action_reject(self):
        self.write({"state": "rejected"})
