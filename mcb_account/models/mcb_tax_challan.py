from odoo import api, fields, models


class McbTaxChallan(models.Model):
    """TAX-004/005 (client feedback) — VAT (Mushak) & TDS (Treasury) challan register.

    Tracks amounts deposited to the Govt. Treasury so the monthly summary can show
    Deductible / Deducted / Deposited / Dues with challan no, date, bank & branch.
    """
    _name = "mcb.tax.challan"
    _description = "MCB VAT/TDS Challan"
    _inherit = ["mail.thread"]
    _order = "date desc"

    name = fields.Char(string="Reference", default="New", copy=False, readonly=True)
    challan_type = fields.Selection([
        ("mushak_vat", "Mushak Challan (VAT)"),
        ("treasury_tds", "Treasury Challan (TDS)"),
    ], required=True, default="treasury_tds", tracking=True)
    challan_no = fields.Char(required=True, tracking=True)
    date = fields.Date(required=True, default=fields.Date.context_today, tracking=True)
    bank_name = fields.Char(string="Name of Bank", required=True)
    branch_name = fields.Char(string="Branch")
    amount = fields.Monetary(required=True, currency_field="currency_id", tracking=True)
    currency_id = fields.Many2one("res.currency", default=lambda s: s.env.company.currency_id)
    company_id = fields.Many2one("res.company", default=lambda s: s.env.company, required=True)
    period_date_from = fields.Date(string="Period From")
    period_date_to = fields.Date(string="Period To")
    move_ids = fields.Many2many(
        "account.move", string="Related Vouchers / Bills",
        help="Bills or entries whose VAT/TDS this challan deposits.",
    )
    state = fields.Selection([
        ("draft", "Draft"),
        ("deposited", "Deposited to Treasury"),
    ], default="draft", tracking=True)
    note = fields.Text()

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code("mcb.tax.challan") or "CHL/000"
        return super().create(vals_list)

    def action_deposit(self):
        self.write({"state": "deposited"})

    def action_reset(self):
        self.write({"state": "draft"})
