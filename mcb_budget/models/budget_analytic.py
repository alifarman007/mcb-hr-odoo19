from odoo import api, fields, models, _
from odoo.exceptions import UserError


class BudgetAnalytic(models.Model):
    _inherit = "budget.analytic"

    # BUD-001 (Annexure-27) header data
    mcb_donor = fields.Char(string="Funded By (Donor)")
    mcb_project_code = fields.Char(string="Project Code")
    mcb_implementing_org = fields.Char(default="Mukti Cox's Bazar")
    mcb_locked = fields.Boolean(
        string="Budget Locked (BUD-008)", tracking=True, copy=False,
        help="CE lock at project close-out — no further expenditure allowed.")
    mcb_overage_policy = fields.Selection([
        ("warn", "Warn only"),
        ("block", "Block (BUD-004)"),
    ], default="block", required=True, string="On Budget Overage")
    mcb_revision_ids = fields.One2many("mcb.budget.revision", "budget_id")

    def action_mcb_lock(self):
        if not self.env.user.has_group("mcb_hr_employee.group_mcb_ce"):
            raise UserError(_("BUD-008 — only the Chief Executive group can lock/unlock budgets."))
        for rec in self:
            rec.mcb_locked = not rec.mcb_locked


class BudgetLine(models.Model):
    _inherit = "budget.line"

    # Annexure-27 columns
    mcb_activity_code = fields.Char(string="Activity Code")
    mcb_activity_serial = fields.Char(string="Activity Serial")
    mcb_cost_category = fields.Selection([
        ("direct", "Direct Cost"),
        ("indirect", "Indirect / Admin Cost"),
        ("staff", "Staff Cost"),
    ], string="Cost Category")
    mcb_activity_name = fields.Char(string="Activities")
    mcb_unit_desc = fields.Char(string="Unit Description")
    mcb_unit = fields.Float(string="Unit", default=1)
    mcb_times = fields.Float(string="Month/Day/Time", default=1)
    mcb_unit_cost = fields.Monetary(string="Unit Cost", currency_field="currency_id")
    mcb_variance_reason = fields.Char(string="Reason for Variance (Annex-11)")

    @api.onchange("mcb_unit", "mcb_times", "mcb_unit_cost")
    def _onchange_mcb_amounts(self):
        for line in self:
            if line.mcb_unit_cost:
                line.budget_amount = (line.mcb_unit or 1) * (line.mcb_times or 1) * line.mcb_unit_cost
