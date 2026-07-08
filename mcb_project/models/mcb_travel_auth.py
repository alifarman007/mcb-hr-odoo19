from odoo import api, fields, models


class McbTravelAuthorization(models.Model):
    """Annexure-30 / MON-006 — Employee Travel Authorization workflow."""
    _name = "mcb.travel.authorization"
    _description = "MCB Travel Authorization (Annexure-30)"
    _inherit = ["mail.thread", "mcb.fy.mixin"]
    _order = "departure_date desc"

    name = fields.Char(default="New", copy=False, readonly=True)
    employee_id = fields.Many2one("hr.employee", required=True,
                                  default=lambda s: s.env.user.employee_id)
    designation = fields.Char(related="employee_id.job_title", string="Designation")
    project_id = fields.Many2one("project.project", string="Project")
    funded_by = fields.Char()
    departure_date = fields.Date(required=True)
    return_date = fields.Date(required=True)
    destination = fields.Char(required=True)
    purpose = fields.Char(required=True)
    transport_mode = fields.Char(string="Mode of Transportation")

    travel_cost = fields.Monetary(currency_field="currency_id")
    lodging_cost = fields.Monetary(currency_field="currency_id")
    food_cost = fields.Monetary(currency_field="currency_id")
    registration_cost = fields.Monetary(currency_field="currency_id")
    other_cost = fields.Monetary(currency_field="currency_id")
    total_cost = fields.Monetary(compute="_compute_total", store=True,
                                 currency_field="currency_id")
    currency_id = fields.Many2one("res.currency", default=lambda s: s.env.company.currency_id)
    company_id = fields.Many2one("res.company", default=lambda s: s.env.company)

    finance_comment = fields.Char(string="Finance Comments")
    recommended_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    approved_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    expense_ids = fields.One2many("hr.expense", "mcb_travel_auth_id",
                                  string="Linked Expense Claims")
    state = fields.Selection([
        ("draft", "Draft"),
        ("submitted", "Submitted"),
        ("finance", "Finance Reviewed"),
        ("recommended", "Recommended"),
        ("approved", "Approved"),
        ("cancelled", "Cancelled"),
    ], default="draft", tracking=True)

    @api.depends("travel_cost", "lodging_cost", "food_cost",
                 "registration_cost", "other_cost")
    def _compute_total(self):
        for rec in self:
            rec.total_cost = (rec.travel_cost + rec.lodging_cost + rec.food_cost
                              + rec.registration_cost + rec.other_cost)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self._mcb_fy_sequence_next("mcb.travel.auth", "TAF")
        return super().create(vals_list)

    def action_submit(self):
        self.write({"state": "submitted"})

    def action_finance(self):
        self.write({"state": "finance"})

    def action_recommend(self):
        self.write({"state": "recommended", "recommended_by_id": self.env.user.id})

    def action_approve(self):
        self.write({"state": "approved", "approved_by_id": self.env.user.id})

    def action_cancel(self):
        self.write({"state": "cancelled"})


class HrExpense(models.Model):
    _inherit = "hr.expense"

    mcb_travel_auth_id = fields.Many2one(
        "mcb.travel.authorization", string="Travel Authorization (Annex-30)",
        help="MOV-004 compliance link — expense claims tie back to the approved travel.")
