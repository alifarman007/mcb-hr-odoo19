from odoo import api, fields, models, _
from odoo.exceptions import UserError


class McbWorkingBudget(models.Model):
    """Annexure-26 — activity-level operational (working) budget (BUD-002, PRJ-006)."""
    _name = "mcb.working.budget"
    _description = "MCB Working Budget (Annexure-26)"
    _inherit = ["mail.thread", "mcb.fy.mixin"]

    name = fields.Char(default="New", copy=False, readonly=True)
    budget_id = fields.Many2one("budget.analytic", string="Parent Project Budget",
                                required=True, tracking=True)
    analytic_account_id = fields.Many2one(
        "account.analytic.account", string="Project / Donor Analytic", required=True,
        help="Consumption is measured on this analytic account within the activity dates.")
    activity_name = fields.Char(string="Name of Activity", required=True)
    account_id = fields.Many2one("account.account", string="Accounts Head")
    date_from = fields.Date(required=True, default=fields.Date.context_today)
    date_to = fields.Date(required=True, default=fields.Date.context_today)
    line_ids = fields.One2many("mcb.working.budget.line", "working_budget_id")
    amount_total = fields.Monetary(compute="_compute_amounts", store=True,
                                   currency_field="currency_id")
    amount_consumed = fields.Monetary(compute="_compute_consumed",
                                      currency_field="currency_id")
    amount_in_words = fields.Char(compute="_compute_words")
    currency_id = fields.Many2one("res.currency", default=lambda s: s.env.company.currency_id)
    company_id = fields.Many2one("res.company", default=lambda s: s.env.company)
    state = fields.Selection([
        ("draft", "Draft"), ("checked", "Checked"),
        ("reviewed", "Reviewed"), ("approved", "Approved"),
    ], default="draft", tracking=True)

    @api.depends("line_ids.amount")
    def _compute_amounts(self):
        for rec in self:
            rec.amount_total = sum(rec.line_ids.mapped("amount"))

    def _compute_consumed(self):
        for rec in self:
            grouped = self.env["account.analytic.line"]._read_group(
                [("account_id", "=", rec.analytic_account_id.id),
                 ("date", ">=", rec.date_from), ("date", "<=", rec.date_to),
                 ("amount", "<", 0)],
                [], ["amount:sum"])
            rec.amount_consumed = -(grouped[0][0] or 0.0)

    @api.depends("amount_total")
    def _compute_words(self):
        for rec in self:
            rec.amount_in_words = (rec.currency_id.amount_to_text(rec.amount_total)
                                   if rec.amount_total else "")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self._mcb_fy_sequence_next("mcb.working.budget", "WB")
        return super().create(vals_list)

    def action_check(self):
        self.write({"state": "checked"})

    def action_review(self):
        self.write({"state": "reviewed"})

    def action_approve(self):
        self.write({"state": "approved"})


class McbWorkingBudgetLine(models.Model):
    _name = "mcb.working.budget.line"
    _description = "Working Budget Line (Annexure-26)"

    working_budget_id = fields.Many2one("mcb.working.budget", required=True,
                                        ondelete="cascade")
    name = fields.Char(string="Particulars", required=True)
    unit_desc = fields.Char(string="Unit Description")
    unit = fields.Float(default=1)
    times = fields.Float(string="Days/Events/Months/Times", default=1)
    unit_cost = fields.Monetary(currency_field="currency_id")
    amount = fields.Monetary(compute="_compute_amount", store=True, readonly=False,
                             currency_field="currency_id")
    remarks = fields.Char()
    currency_id = fields.Many2one(related="working_budget_id.currency_id")

    @api.depends("unit", "times", "unit_cost")
    def _compute_amount(self):
        for l in self:
            if l.unit_cost:
                l.amount = (l.unit or 1) * (l.times or 1) * l.unit_cost
