from odoo import api, fields, models


class McbHrRecruitmentExpenditure(models.Model):
    """REC-014 Recruitment Expenditure Top Sheet."""
    _name = "mcb.hr.recruitment.expenditure"
    _description = "MCB Recruitment Expenditure Top Sheet"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "create_date desc"

    name = fields.Char(string="Reference", required=True, default="New", copy=False, readonly=True)
    requisition_id = fields.Many2one("mcb.hr.staff.requisition", required=True, ondelete="cascade", tracking=True)
    date = fields.Date(default=fields.Date.context_today)
    purpose = fields.Char(default="Recruitment Expenditure")
    state = fields.Selection([
        ("draft", "Draft"),
        ("submitted", "Submitted"),
        ("approved", "Approved"),
    ], default="draft", tracking=True)
    currency_id = fields.Many2one("res.currency", default=lambda s: s.env.company.currency_id)
    line_ids = fields.One2many("mcb.hr.recruitment.expenditure.line", "expenditure_id", string="Lines")
    total_amount = fields.Monetary(compute="_compute_total", store=True, currency_field="currency_id")
    budget_amount = fields.Monetary(currency_field="currency_id", help="Budgeted recruitment cost from approved budget.")
    variance = fields.Monetary(compute="_compute_total", store=True, currency_field="currency_id")

    @api.depends("line_ids.net_paid", "budget_amount")
    def _compute_total(self):
        for rec in self:
            rec.total_amount = sum(l.net_paid for l in rec.line_ids)
            rec.variance = (rec.budget_amount or 0) - rec.total_amount

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code("mcb.hr.recruitment.expenditure") or "EXP/0000"
        return super().create(vals_list)

    def action_submit(self):
        self.write({"state": "submitted"})

    def action_approve(self):
        self.write({"state": "approved"})


class McbHrRecruitmentExpenditureLine(models.Model):
    _name = "mcb.hr.recruitment.expenditure.line"
    _description = "Recruitment Expenditure Line"

    expenditure_id = fields.Many2one("mcb.hr.recruitment.expenditure", required=True, ondelete="cascade")
    sequence = fields.Integer(default=10)
    voucher_no = fields.Char()
    receiver = fields.Char(string="Receiver / Vendor")
    description = fields.Char(string="Purpose / Description", required=True)
    bill_amount = fields.Monetary(currency_field="currency_id")
    vat_amount = fields.Monetary(string="VAT/TDS", currency_field="currency_id")
    net_paid = fields.Monetary(currency_field="currency_id", compute="_compute_net", store=True, readonly=False)
    analytic_code = fields.Char(string="Analytic Code")
    currency_id = fields.Many2one("res.currency", related="expenditure_id.currency_id", store=True)

    @api.depends("bill_amount", "vat_amount")
    def _compute_net(self):
        for rec in self:
            rec.net_paid = (rec.bill_amount or 0) - (rec.vat_amount or 0)
