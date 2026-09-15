from odoo import api, fields, models, _
from odoo.exceptions import UserError


class McbStockDisposal(models.Model):
    """LOG-007 — Disposal of expired or damaged stock.

    SOP, monthly activities: 'When an approved Disposal Request is received from the
    head office the expired or damaged inventory items can be disposed of environmentally
    friendly and in line with local regulations. The Mukti Cox's Bazar head office will
    adjust the inventory records... and the warehouse will adjust the quantities on the
    stock and stack/bin cards. The approved disposal list needs to be printed and filed.'

    So the approval must come first, and the bin cards are adjusted only after it.
    """
    _name = "mcb.stock.disposal"
    _description = "MCB Stock Disposal Request"
    _inherit = ["mail.thread", "mail.activity.mixin", "mcb.fy.mixin"]
    _order = "date desc, id desc"

    name = fields.Char(default="New", copy=False, readonly=True, index=True)
    date = fields.Date(required=True, default=fields.Date.context_today, tracking=True)
    warehouse_id = fields.Many2one("stock.warehouse", required=True, tracking=True)
    project_id = fields.Many2one("project.project", string="Project / Office")
    reason = fields.Selection([
        ("expired", "Expired"),
        ("damaged", "Damaged"),
        ("obsolete", "Obsolete / Unserviceable"),
        ("lost", "Lost in verification"),
    ], required=True, default="expired", tracking=True)
    verification_id = fields.Many2one("mcb.stock.verification",
                                      string="From Physical Verification")
    disposal_method = fields.Char(
        string="Method of Disposal",
        help="SOP: disposed of environmentally friendly and in line with local regulations.")
    line_ids = fields.One2many("mcb.stock.disposal.line", "disposal_id", string="Items")
    total_value = fields.Monetary(compute="_compute_total", store=True,
                                  currency_field="currency_id")
    currency_id = fields.Many2one("res.currency",
                                  default=lambda s: s.env.company.currency_id)
    company_id = fields.Many2one("res.company", default=lambda s: s.env.company)

    requested_by_id = fields.Many2one("res.users", string="Requested By",
                                      default=lambda s: s.env.user)
    approved_by_id = fields.Many2one("res.users", string="Approved By (Head Office)",
                                     readonly=True, copy=False)
    approval_date = fields.Date(readonly=True, copy=False)
    remarks = fields.Text()

    state = fields.Selection([
        ("draft", "Draft"),
        ("requested", "Requested"),
        ("approved", "Approved"),
        ("disposed", "Disposed"),
        ("rejected", "Rejected"),
    ], default="draft", tracking=True)

    @api.depends("line_ids.value")
    def _compute_total(self):
        for rec in self:
            rec.total_value = sum(rec.line_ids.mapped("value"))

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self._mcb_fy_sequence_next("mcb.stock.disposal",
                                                          "DSP", padding=3)
        return super().create(vals_list)

    def action_request(self):
        for rec in self:
            if not rec.line_ids:
                raise UserError(_("LOG-007 — list the items to be disposed of."))
        self.write({"state": "requested"})

    def action_approve(self):
        """Head office approval. Only after this may the warehouse touch the stock."""
        for rec in self:
            if rec.state != "requested":
                raise UserError(_("Only a submitted request can be approved."))
        self.write({
            "state": "approved",
            "approved_by_id": self.env.user.id,
            "approval_date": fields.Date.context_today(self),
        })

    def action_reject(self):
        self.write({"state": "rejected"})

    def action_dispose(self):
        """Scrap the goods and write the movement onto the bin/stack cards."""
        for rec in self:
            if rec.state != "approved":
                raise UserError(_(
                    "LOG-007 — stock may only be disposed of once the head office has "
                    "approved the request. Get the approval first."))
            for line in rec.line_ids:
                rec._scrap_line(line)
                if line.bin_card_id:
                    line.bin_card_id._mcb_post_movement(
                        date=rec.date,
                        party=_("Disposal — %s", dict(
                            rec._fields["reason"].selection).get(rec.reason, rec.reason)),
                        doc_ref=rec.name,
                        qty_out=line.quantity,
                        remarks=line.remarks or rec.disposal_method,
                    )
            rec.state = "disposed"

    def _scrap_line(self, line):
        self.ensure_one()
        Location = self.env["stock.location"]
        scrap_loc = Location.search([
            ("usage", "=", "inventory"), ("name", "ilike", "scrap"),
            ("company_id", "in", (self.company_id.id, False))], limit=1)
        if not scrap_loc:
            scrap_loc = Location.search([
                ("usage", "=", "inventory"),
                ("company_id", "in", (self.company_id.id, False))], limit=1)
        if not scrap_loc:
            raise UserError(_(
                "No scrap or inventory-adjustment location exists for this company, so "
                "the disposal cannot be written off. Ask the administrator to create one."))
        self.env["stock.scrap"].create({
            "product_id": line.product_id.id,
            "scrap_qty": line.quantity,
            "product_uom_id": line.uom_id.id or line.product_id.uom_id.id,
            "location_id": (line.location_id.id
                            or self.warehouse_id.lot_stock_id.id),
            "scrap_location_id": scrap_loc.id,
            "origin": self.name,
        }).do_scrap()


class McbStockDisposalLine(models.Model):
    _name = "mcb.stock.disposal.line"
    _description = "MCB Stock Disposal Line"
    _order = "id"

    disposal_id = fields.Many2one("mcb.stock.disposal", required=True, ondelete="cascade")
    product_id = fields.Many2one("product.product", required=True, string="Item")
    location_id = fields.Many2one("stock.location", string="Location")
    lot_id = fields.Many2one("stock.lot", string="Batch No")
    bin_card_id = fields.Many2one("mcb.bin.card", string="Bin / Stack Card")
    uom_id = fields.Many2one("uom.uom", string="Unit")
    quantity = fields.Float(required=True, digits="Product Unit of Measure")
    unit_value = fields.Monetary(currency_field="currency_id")
    value = fields.Monetary(compute="_compute_value", store=True,
                            currency_field="currency_id")
    currency_id = fields.Many2one(related="disposal_id.currency_id")
    expiry_date = fields.Date(string="Expiry Date")
    remarks = fields.Char()

    @api.depends("quantity", "unit_value")
    def _compute_value(self):
        for line in self:
            line.value = (line.quantity or 0.0) * (line.unit_value or 0.0)

    @api.onchange("product_id")
    def _onchange_product(self):
        for line in self:
            if line.product_id:
                line.uom_id = line.product_id.uom_id
