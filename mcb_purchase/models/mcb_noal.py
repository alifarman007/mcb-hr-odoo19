from odoo import api, fields, models, _
from odoo.exceptions import UserError


class McbNoal(models.Model):
    """Step 9 — Notification of Award Letter (NOAL-001/002/006)."""
    _name = "mcb.noal"
    _description = "MCB Notification of Award Letter (NOAL)"
    _inherit = ["mail.thread", "mcb.fy.mixin"]

    name = fields.Char(string="Reference No", default="New", copy=False, readonly=True)
    date = fields.Date(default=fields.Date.context_today, required=True)
    order_id = fields.Many2one("purchase.order", required=True, string="Purchase Order")
    vendor_id = fields.Many2one("res.partner", required=True, string="Vendor")
    vendor_address = fields.Char(compute="_compute_vendor_address", store=True)
    contract_price = fields.Monetary(currency_field="currency_id", required=True)
    contract_price_words = fields.Char(compute="_compute_words")
    performance_security_pct = fields.Float(string="Performance Security %", default=10.0)
    performance_security_amount = fields.Monetary(
        compute="_compute_security", store=True, currency_field="currency_id")
    currency_id = fields.Many2one("res.currency", default=lambda s: s.env.company.currency_id)
    company_id = fields.Many2one("res.company", default=lambda s: s.env.company)
    state = fields.Selection([
        ("draft", "Draft"),
        ("issued", "Issued"),
        ("acknowledged", "Acknowledged by Vendor"),
    ], default="draft", tracking=True)

    @api.depends("vendor_id")
    def _compute_vendor_address(self):
        for rec in self:
            rec.vendor_address = rec.vendor_id.contact_address or ""

    @api.depends("contract_price", "currency_id")
    def _compute_words(self):
        for rec in self:
            rec.contract_price_words = (
                rec.currency_id.amount_to_text(rec.contract_price)
                if rec.contract_price else "")

    @api.depends("contract_price", "performance_security_pct")
    def _compute_security(self):
        for rec in self:
            rec.performance_security_amount = (
                rec.contract_price * rec.performance_security_pct / 100.0)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self._mcb_fy_sequence_next("mcb.noal", "NOAL")
        return super().create(vals_list)

    def action_issue(self):
        for rec in self:
            if not rec.contract_price:
                raise UserError(_("Set the contract price (NOAL-002)."))
        self.write({"state": "issued"})

    def action_acknowledge(self):
        self.write({"state": "acknowledged"})
