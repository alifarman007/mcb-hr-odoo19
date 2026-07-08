from odoo import api, fields, models


class McbAssetInventory(models.Model):
    """Annexure-22 — Fixed Assets Physical Inventory Report (AST-004)."""
    _name = "mcb.asset.inventory"
    _description = "MCB Asset Physical Inventory (Annexure-22)"
    _inherit = ["mail.thread", "mcb.fy.mixin"]

    name = fields.Char(default="New", copy=False, readonly=True)
    date = fields.Date(default=fields.Date.context_today, required=True)
    project_name = fields.Char(string="Name of Project / Office")
    funded_by = fields.Char()
    company_id = fields.Many2one("res.company", default=lambda s: s.env.company)
    line_ids = fields.One2many("mcb.asset.inventory.line", "inventory_id")
    state = fields.Selection([
        ("draft", "Draft"), ("done", "Verified"),
    ], default="draft", tracking=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self._mcb_fy_sequence_next("mcb.asset.inventory", "API")
        return super().create(vals_list)

    def action_fill_from_register(self):
        """Load all running assets as inventory lines (register qty = 1 each)."""
        for rec in self:
            existing = rec.line_ids.mapped("asset_id")
            assets = self.env["account.asset"].search([
                ("state", "=", "open"),
                ("company_id", "=", rec.company_id.id),
                ("id", "not in", existing.ids),
            ])
            rec.line_ids = [(0, 0, {
                "asset_id": a.id,
                "qty_register": 1,
                "qty_found": 1,
            }) for a in assets]

    def action_done(self):
        for rec in self:
            for line in rec.line_ids:
                if line.recommendation == "repairable":
                    line.asset_id.mcb_condition = "repairable"
        self.write({"state": "done"})


class McbAssetInventoryLine(models.Model):
    _name = "mcb.asset.inventory.line"
    _description = "Asset Physical Inventory Line"

    inventory_id = fields.Many2one("mcb.asset.inventory", required=True, ondelete="cascade")
    asset_id = fields.Many2one("account.asset", required=True)
    cost = fields.Monetary(related="asset_id.original_value", currency_field="currency_id")
    wdv = fields.Monetary(related="asset_id.book_value", string="Written Down Value",
                          currency_field="currency_id")
    currency_id = fields.Many2one(related="asset_id.currency_id")
    qty_register = fields.Integer(string="Qty per Register", default=1)
    qty_found = fields.Integer(string="Qty Physically Found", default=1)
    diff = fields.Integer(compute="_compute_diff", store=True, string="Short/Excess")
    recommendation = fields.Selection([
        ("keep", "Keep in Service"),
        ("sales", "Sales"),
        ("disposal", "Disposal"),
        ("repairable", "Repairable"),
    ], default="keep")
    remarks = fields.Char()

    @api.depends("qty_register", "qty_found")
    def _compute_diff(self):
        for l in self:
            l.diff = l.qty_found - l.qty_register
