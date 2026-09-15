from odoo import api, fields, models, _
from odoo.exceptions import UserError


class McbGsrn(models.Model):
    """LOG-002 — Goods and Service Received Note (GSRN).

    SOP: 'The Goods Receiving Note (GRN) is a standard Mukti Cox's Bazar document to
    confirm receipt of goods. It is the base document for financial transactions, such
    as the payment of the supplier/forwarder and the recording of the accounting
    entries.' The printed form is a three-part set — Accounts, Store and Purchaser.

    It also covers goods that arrive with no purchase order at all: the SOP's scope
    explicitly includes 'items provided in-kind by Donor/UN agency/GoB'.
    """
    _name = "mcb.gsrn"
    _description = "MCB Goods & Service Received Note (GSRN)"
    _inherit = ["mail.thread", "mail.activity.mixin", "mcb.fy.mixin"]
    _order = "date desc, id desc"

    name = fields.Char(default="New", copy=False, readonly=True, index=True)
    pad_serial = fields.Char(
        string="Printed Pad Serial (GRN # MC-)",
        help="The number pre-printed on the paper GSRN pad, e.g. 573. Kept alongside the "
             "system number so ERP records can be tied to the pads during the changeover.")
    date = fields.Date(string="Receiving Date", required=True,
                       default=fields.Date.context_today, tracking=True)
    source_type = fields.Selection([
        ("purchase", "Against Purchase Order / PR / WR"),
        ("in_kind", "In-kind — Donor / UN Agency / GoB"),
        ("transfer", "Transfer from another MCB warehouse"),
        ("return", "Return from field"),
    ], default="purchase", required=True, tracking=True, string="Source of Goods")

    # --- supplier block (left side of the printed form) ---
    partner_id = fields.Many2one("res.partner", string="Name of Vendor", tracking=True)
    supplier_challan_no = fields.Char(string="Supplier Challan #")
    supplier_challan_date = fields.Date(string="Supplier Challan Date")

    # --- MCB block (right side of the printed form) ---
    warehouse_id = fields.Many2one("stock.warehouse", string="Name of Office / Warehouse",
                                   required=True, tracking=True)
    location_id = fields.Many2one("stock.location", string="Store Location",
                                  domain="[('usage', '=', 'internal')]")
    purchase_order_id = fields.Many2one("purchase.order", string="PO / PR / WR #",
                                        tracking=True)
    reference_no = fields.Char(
        string="Reference (in-kind / transfer)",
        help="Donation reference, gift certificate or transfer note when there is no PO.")
    donor = fields.Char(string="Donor / Funder")
    project_id = fields.Many2one("project.project", string="Project")
    analytic_account_id = fields.Many2one("account.analytic.account",
                                          string="Project / Donor Analytic")

    line_ids = fields.One2many("mcb.gsrn.line", "gsrn_id", string="Items")
    remarks = fields.Text()

    # --- quality inspection (SOP: quality inspection reports go to head office daily) ---
    inspection_result = fields.Selection([
        ("accepted", "Accepted in full"),
        ("partial", "Partially accepted"),
        ("rejected", "Rejected"),
    ], string="Quality Inspection", default="accepted", tracking=True)
    inspection_remarks = fields.Char(string="Inspection Remarks")

    # --- signatures printed on the form ---
    delivered_by_name = fields.Char(string="Delivered By (vendor side)")
    delivered_by_date = fields.Date(string="Delivery Date")
    recipient_id = fields.Many2one("res.users", string="Recipient",
                                   default=lambda s: s.env.user, tracking=True)
    recipient_designation = fields.Char(string="Recipient Designation")

    picking_id = fields.Many2one("stock.picking", readonly=True, copy=False,
                                 string="Stock Receipt")
    amount_total = fields.Monetary(compute="_compute_amount", store=True,
                                   currency_field="currency_id")
    currency_id = fields.Many2one("res.currency",
                                  default=lambda s: s.env.company.currency_id)
    company_id = fields.Many2one("res.company", default=lambda s: s.env.company)

    state = fields.Selection([
        ("draft", "Draft"),
        ("received", "Received"),
        ("posted", "Posted to Stock"),
        ("cancelled", "Cancelled"),
    ], default="draft", tracking=True)

    @api.depends("line_ids.amount")
    def _compute_amount(self):
        for rec in self:
            rec.amount_total = sum(rec.line_ids.mapped("amount"))

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self._mcb_fy_sequence_next("mcb.gsrn", "GSRN", padding=4)
        return super().create(vals_list)

    @api.onchange("purchase_order_id")
    def _onchange_purchase_order(self):
        """Pull the ordered quantities off the PO so the storekeeper only types what
        actually turned up."""
        for rec in self:
            po = rec.purchase_order_id
            if not po:
                continue
            rec.partner_id = po.partner_id
            lines = []
            for pol in po.order_line:
                lines.append((0, 0, {
                    "product_id": pol.product_id.id,
                    "description": pol.name,
                    "uom_id": pol.product_uom_id.id if hasattr(pol, "product_uom_id")
                    else pol.product_id.uom_id.id,
                    "qty_ordered": pol.product_qty,
                    "qty_received": pol.product_qty,
                    "unit_cost": pol.price_unit,
                }))
            rec.line_ids = [(5, 0, 0)] + lines

    # ------------------------------------------------------------- workflow --
    def action_receive(self):
        for rec in self:
            if not rec.line_ids:
                raise UserError(_("LOG-002 — add at least one item line before receiving."))
            if rec.source_type == "purchase" and not rec.purchase_order_id:
                raise UserError(_(
                    "LOG-002 — a GSRN against a purchase must name the PO / PR / WR. "
                    "For goods with no purchase order, set the source to 'In-kind'."))
            if rec.source_type == "in_kind" and not (rec.donor or rec.reference_no):
                raise UserError(_(
                    "LOG-002 — in-kind goods must record the donor or a reference, so the "
                    "items can be traced back to whoever gave them."))
        self.write({"state": "received"})

    def action_post(self):
        """Put the goods into stock and write the bin/stack cards."""
        for rec in self:
            if rec.state != "received":
                raise UserError(_("Receive the GSRN before posting it to stock."))
            accepted = rec.line_ids.filtered(lambda l: l.qty_accepted > 0)
            if not accepted:
                raise UserError(_(
                    "LOG-002 — every line was rejected, so there is nothing to take into "
                    "stock. Cancel the GSRN instead."))
            # The printed form is a Goods AND SERVICE Received Note: a work order or a
            # service is certified here but never enters stock, so only storable lines
            # produce a stock move and a bin card entry.
            storable = accepted.filtered(lambda l: l.product_id.is_storable)
            if storable:
                rec._create_receipt_picking(storable)
                rec._update_bin_cards(storable)
            rec.state = "posted"

    def _create_receipt_picking(self, lines):
        self.ensure_one()
        picking_type = self.env["stock.picking.type"].search([
            ("code", "=", "incoming"),
            ("warehouse_id", "=", self.warehouse_id.id)], limit=1)
        if not picking_type:
            raise UserError(_(
                "No incoming operation type is configured for warehouse '%s'.",
                self.warehouse_id.display_name))
        dest = self.location_id or picking_type.default_location_dest_id
        src = self.env.ref("stock.stock_location_suppliers", raise_if_not_found=False)
        vals = {
            "picking_type_id": picking_type.id,
            "partner_id": self.partner_id.id or False,
            "origin": self.name,
            "location_id": src.id if src else picking_type.default_location_src_id.id,
            "location_dest_id": dest.id,
            "move_ids": [(0, 0, {
                "product_id": l.product_id.id,
                "product_uom_qty": l.qty_accepted,
                "product_uom": l.uom_id.id,
                "location_id": src.id if src else picking_type.default_location_src_id.id,
                "location_dest_id": dest.id,
            }) for l in lines],
        }
        picking = self.env["stock.picking"].create(vals)
        picking.action_confirm()
        self._mcb_validate_picking(picking)
        self.picking_id = picking.id
        return picking

    def _mcb_validate_picking(self, picking):
        """Confirming a transfer only reserves it — the goods are not in (or out of)
        stock until it is validated. A receiving note whose goods never reach stock
        would leave the bin cards and Odoo permanently out of step, which is exactly
        what the SOP's monthly reconciliation exists to catch."""
        if not picking or picking.state in ("done", "cancel"):
            return picking
        picking.action_assign()
        for move in picking.move_ids:
            move.quantity = move.product_uom_qty
            move.picked = True
        picking.button_validate()
        return picking


    def _update_bin_cards(self, lines):
        self.ensure_one()
        Card = self.env["mcb.bin.card"]
        for line in lines:
            card = Card._mcb_get_or_create(
                product=line.product_id,
                warehouse=self.warehouse_id,
                location=self.location_id,
                purchase_order=self.purchase_order_id,
                po_reference=self.reference_no or self.donor,
                lot=line.lot_id,
            )
            card._mcb_post_movement(
                date=self.date,
                party=self.partner_id.name or self.donor or "",
                doc_ref=self.name,
                qty_in=line.qty_accepted,
                remarks=line.remarks,
            )

    def action_cancel(self):
        for rec in self:
            if rec.state == "posted":
                raise UserError(_(
                    "LOG-002 — this GSRN is already in stock. Reverse the stock receipt "
                    "first; a posted receiving note cannot simply be cancelled."))
        self.write({"state": "cancelled"})

    def action_draft(self):
        self.filtered(lambda r: r.state == "cancelled").write({"state": "draft"})

    def action_view_picking(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "res_model": "stock.picking",
            "res_id": self.picking_id.id,
            "view_mode": "form",
        }


class McbGsrnLine(models.Model):
    _name = "mcb.gsrn.line"
    _description = "MCB GSRN Item Line"
    _order = "sequence, id"

    gsrn_id = fields.Many2one("mcb.gsrn", required=True, ondelete="cascade")
    sequence = fields.Integer(default=10)
    product_id = fields.Many2one("product.product", required=True, string="Item")
    description = fields.Char(string="Description")
    uom_id = fields.Many2one("uom.uom", string="Unit")
    lot_id = fields.Many2one("stock.lot", string="Batch No")
    qty_ordered = fields.Float(string="Quantity Ordered", digits="Product Unit of Measure")
    qty_received = fields.Float(string="Quantity Received", digits="Product Unit of Measure")
    qty_rejected = fields.Float(string="Quantity Rejected", digits="Product Unit of Measure")
    qty_accepted = fields.Float(string="Quantity Accepted", compute="_compute_accepted",
                                store=True, digits="Product Unit of Measure")
    unit_cost = fields.Monetary(string="Unit Cost (Taka)", currency_field="currency_id")
    amount = fields.Monetary(compute="_compute_amount", store=True,
                             currency_field="currency_id")
    currency_id = fields.Many2one(related="gsrn_id.currency_id")
    remarks = fields.Char()

    @api.depends("qty_received", "qty_rejected")
    def _compute_accepted(self):
        for line in self:
            line.qty_accepted = max((line.qty_received or 0.0) - (line.qty_rejected or 0.0), 0.0)

    @api.depends("qty_accepted", "unit_cost")
    def _compute_amount(self):
        for line in self:
            line.amount = line.qty_accepted * (line.unit_cost or 0.0)

    @api.constrains("qty_received", "qty_rejected")
    def _check_quantities(self):
        for line in self:
            if line.qty_rejected and line.qty_rejected > line.qty_received:
                raise UserError(_(
                    "LOG-002 — you cannot reject %(rej).2f of '%(item)s' when only "
                    "%(rec).2f was received.",
                    rej=line.qty_rejected, item=line.product_id.display_name,
                    rec=line.qty_received))

    @api.onchange("product_id")
    def _onchange_product(self):
        for line in self:
            if line.product_id:
                line.description = line.product_id.display_name
                line.uom_id = line.product_id.uom_id
