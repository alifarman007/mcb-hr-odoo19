from odoo import api, fields, models, _
from odoo.exceptions import UserError


class McbSrf(models.Model):
    """STO-004 — Store Requisition Form: request → approval → internal issue picking.
    The generated stock moves ARE the Store Register entries (Annexure-08)."""
    _name = "mcb.srf"
    _description = "MCB Store Requisition Form (SRF)"
    _inherit = ["mail.thread", "mcb.fy.mixin"]
    _order = "create_date desc"

    name = fields.Char(default="New", copy=False, readonly=True)
    requester_id = fields.Many2one("res.users", default=lambda s: s.env.user, tracking=True)
    project_id = fields.Many2one("project.project", string="Project")
    analytic_account_id = fields.Many2one("account.analytic.account",
                                          string="Project / Donor Analytic")
    date_request = fields.Date(default=fields.Date.context_today)
    source_location_id = fields.Many2one(
        "stock.location", string="Store (Source)", required=True,
        domain="[('usage', '=', 'internal')]",
        default=lambda s: s.env.ref("stock.stock_location_stock",
                                    raise_if_not_found=False))
    dest_location_id = fields.Many2one(
        "stock.location", string="Issue To", required=True,
        domain="[('usage', 'in', ('internal', 'customer', 'production'))]")
    line_ids = fields.One2many("mcb.srf.line", "srf_id", string="Items")
    picking_id = fields.Many2one("stock.picking", readonly=True, copy=False)
    recipient_name = fields.Char(string="Name & Designation of Recipient")
    state = fields.Selection([
        ("draft", "Draft"),
        ("requested", "Requested"),
        ("approved", "Approved"),
        ("issued", "Issued"),
        ("cancelled", "Cancelled"),
    ], default="draft", tracking=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self._mcb_fy_sequence_next("mcb.srf", "SRF")
        return super().create(vals_list)

    def action_request(self):
        for rec in self:
            if not rec.line_ids:
                raise UserError(_("Add at least one item to issue."))
        self.write({"state": "requested"})

    def action_approve(self):
        self.write({"state": "approved"})

    def action_issue(self):
        """Create + confirm the internal transfer; store register updates via stock.move."""
        for rec in self:
            picking_type = self.env["stock.picking.type"].search([
                ("code", "=", "internal"),
                ("company_id", "=", self.env.company.id)], limit=1)
            if not picking_type:
                raise UserError(_("No internal transfer operation type configured."))
            picking = self.env["stock.picking"].create({
                "picking_type_id": picking_type.id,
                "location_id": rec.source_location_id.id,
                "location_dest_id": rec.dest_location_id.id,
                "origin": rec.name,
                "move_ids": [(0, 0, {
                    "product_id": l.product_id.id,
                    "product_uom_qty": l.quantity,
                    "product_uom": l.product_id.uom_id.id,
                    "location_id": rec.source_location_id.id,
                    "location_dest_id": rec.dest_location_id.id,
                }) for l in rec.line_ids],
            })
            picking.action_confirm()
            rec.write({"picking_id": picking.id, "state": "issued"})

    def action_cancel(self):
        self.write({"state": "cancelled"})


class McbSrfLine(models.Model):
    _name = "mcb.srf.line"
    _description = "SRF Item Line"

    srf_id = fields.Many2one("mcb.srf", required=True, ondelete="cascade")
    product_id = fields.Many2one("product.product", required=True,
                                 domain="[('type', 'in', ('consu', 'product'))]")
    quantity = fields.Float(default=1, required=True)
    purpose = fields.Char()
