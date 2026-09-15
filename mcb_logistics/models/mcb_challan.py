from odoo import api, fields, models, _
from odoo.exceptions import UserError


class McbChallan(models.Model):
    """LOG-003 — Materials Supply Note / Challan (Waybill).

    SOP: 'A Waybill/Challan is used as the warehouse issuing document, certifying the
    transfer/release of goods... It is the responsibility of the Logistic Officer to
    ensure that the Challan/Waybill is properly filled in, signed and filed. The
    Challan/Waybill can be also referred to as the carrier document, listing the load,
    weight, size, final destination, etc. of the goods carried.'

    Nothing leaves an MCB store without one. It is normally raised from an approved SRF
    (a store requisition), because the SOP is explicit that the store cannot issue
    against no requisition.
    """
    _name = "mcb.challan"
    _description = "MCB Materials Supply Note / Challan"
    _inherit = ["mail.thread", "mail.activity.mixin", "mcb.fy.mixin"]
    _order = "date desc, id desc"

    name = fields.Char(default="New", copy=False, readonly=True, index=True)
    pad_serial = fields.Char(
        string="Printed Pad Serial (Challan No.)",
        help="The number pre-printed on the paper challan pad, e.g. 17701.")
    date = fields.Date(string="Challan Date", required=True,
                       default=fields.Date.context_today, tracking=True)
    srf_id = fields.Many2one("mcb.srf", string="Against Requisition (SRF)", tracking=True)
    warehouse_id = fields.Many2one("stock.warehouse", string="Issuing Warehouse",
                                   required=True, tracking=True)
    source_location_id = fields.Many2one("stock.location", string="From (Store)",
                                         domain="[('usage', '=', 'internal')]")
    dest_location_id = fields.Many2one("stock.location", string="To (Location)",
                                       domain="[('usage', 'in', ('internal', 'customer'))]")

    # --- who is receiving (top block of the printed form) ---
    recipient_name = fields.Char(string="Name of Recipient", tracking=True)
    recipient_designation = fields.Char(string="Designation")
    organisation_name = fields.Char(string="Organization / Camp / LC Name")
    purpose = fields.Char(string="Purpose")
    project_id = fields.Many2one("project.project", string="Project")
    analytic_account_id = fields.Many2one("account.analytic.account",
                                          string="Project / Donor Analytic")

    # --- carrier details (the SOP's 'carrier document') ---
    vehicle_id = fields.Many2one("fleet.vehicle", string="Vehicle")
    vehicle_no = fields.Char(string="Vehicle No")
    driver_name = fields.Char(string="Driver")
    driver_phone = fields.Char(string="Driver Phone")
    transporter = fields.Char(string="Transporter / Forwarder")
    total_packages = fields.Integer(string="Total Packages")
    total_weight = fields.Float(string="Total Weight (kg)")
    destination = fields.Char(string="Final Destination")

    line_ids = fields.One2many("mcb.challan.line", "challan_id", string="Materials")
    total_quantity = fields.Float(compute="_compute_total", store=True,
                                  digits="Product Unit of Measure")
    remarks = fields.Text()

    # --- the three printed signatures ---
    delivered_by_id = fields.Many2one("res.users", string="Delivered By",
                                      default=lambda s: s.env.user)
    approved_by_id = fields.Many2one("res.users", string="Approved By", readonly=True,
                                     copy=False)
    received_by_name = fields.Char(string="Received By")
    received_date = fields.Date(string="Received On")

    picking_id = fields.Many2one("stock.picking", readonly=True, copy=False)
    company_id = fields.Many2one("res.company", default=lambda s: s.env.company)

    state = fields.Selection([
        ("draft", "Draft"),
        ("approved", "Approved"),
        ("issued", "Issued / In Transit"),
        ("delivered", "Delivered"),
        ("cancelled", "Cancelled"),
    ], default="draft", tracking=True)

    @api.depends("line_ids.qty_issued")
    def _compute_total(self):
        for rec in self:
            rec.total_quantity = sum(rec.line_ids.mapped("qty_issued"))

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self._mcb_fy_sequence_next("mcb.challan", "CHL", padding=4)
        return super().create(vals_list)

    @api.onchange("srf_id")
    def _onchange_srf(self):
        """Copy the approved requisition onto the challan, so the store issues exactly
        what was approved and nothing else."""
        for rec in self:
            srf = rec.srf_id
            if not srf:
                continue
            rec.source_location_id = srf.source_location_id
            rec.dest_location_id = srf.dest_location_id
            rec.recipient_name = srf.recipient_name
            rec.project_id = srf.project_id
            rec.analytic_account_id = srf.analytic_account_id
            rec.line_ids = [(5, 0, 0)] + [(0, 0, {
                "product_id": l.product_id.id,
                "uom_id": l.product_id.uom_id.id,
                "qty_issued": l.quantity,
            }) for l in srf.line_ids]

    # ------------------------------------------------------------- workflow --
    def action_approve(self):
        for rec in self:
            if not rec.line_ids:
                raise UserError(_("LOG-003 — add at least one material line."))
            if rec.srf_id and rec.srf_id.state not in ("approved", "issued"):
                raise UserError(_(
                    "LOG-003 — requisition %(srf)s is still '%(state)s'. The SOP does not "
                    "allow the store to issue against an unapproved requisition.",
                    srf=rec.srf_id.name, state=rec.srf_id.state))
        self.write({"state": "approved", "approved_by_id": self.env.user.id})

    def action_issue(self):
        """Release the goods: move the stock and write the bin/stack cards."""
        for rec in self:
            if rec.state != "approved":
                raise UserError(_("LOG-003 — approve the challan before issuing the goods."))
            rec._create_issue_picking()
            rec._update_bin_cards()
            rec.state = "issued"

    def _create_issue_picking(self):
        self.ensure_one()
        if self.srf_id and self.srf_id.picking_id:
            # the requisition already created the internal transfer; do not duplicate it
            self.picking_id = self.srf_id.picking_id.id
            return self.picking_id
        picking_type = self.env["stock.picking.type"].search([
            ("code", "in", ("outgoing", "internal")),
            ("warehouse_id", "=", self.warehouse_id.id)], limit=1)
        if not picking_type:
            raise UserError(_(
                "No outgoing or internal operation type is configured for warehouse '%s'.",
                self.warehouse_id.display_name))
        src = self.source_location_id or picking_type.default_location_src_id
        dest = self.dest_location_id or picking_type.default_location_dest_id
        picking = self.env["stock.picking"].create({
            "picking_type_id": picking_type.id,
            "origin": self.name,
            "location_id": src.id,
            "location_dest_id": dest.id,
            "move_ids": [(0, 0, {
                "product_id": l.product_id.id,
                "product_uom_qty": l.qty_issued,
                "product_uom": l.uom_id.id or l.product_id.uom_id.id,
                "location_id": src.id,
                "location_dest_id": dest.id,
            }) for l in self.line_ids],
        })
        picking.action_confirm()
        self._mcb_validate_picking(picking)
        self.picking_id = picking.id
        return picking

    def _mcb_validate_picking(self, picking):
        """Issue the goods for real — a confirmed-but-unvalidated transfer leaves the
        stock sitting in the store while the challan says it has gone."""
        if not picking or picking.state in ("done", "cancel"):
            return picking
        picking.action_assign()
        for move in picking.move_ids:
            move.quantity = move.product_uom_qty
            move.picked = True
        picking.button_validate()
        return picking

    def _update_bin_cards(self):
        self.ensure_one()
        Card = self.env["mcb.bin.card"]
        for line in self.line_ids:
            card = Card.search([
                ("product_id", "=", line.product_id.id),
                ("warehouse_id", "=", self.warehouse_id.id),
                ("balance", ">", 0),
            ], order="expiry_date asc, id asc", limit=1)
            if not card:
                # nothing on a card yet — open one so the issue is still recorded
                card = Card._mcb_get_or_create(
                    product=line.product_id, warehouse=self.warehouse_id,
                    location=self.source_location_id)
            line.bin_card_id = card.id
            card._mcb_post_movement(
                date=self.date,
                party=self.recipient_name or self.organisation_name or "",
                doc_ref=self.name,
                qty_out=line.qty_issued,
                remarks=line.remarks,
            )

    def action_deliver(self):
        for rec in self:
            if rec.state != "issued":
                raise UserError(_("Only an issued challan can be marked delivered."))
            if not rec.received_by_name:
                raise UserError(_(
                    "LOG-003 — record who received the goods before closing the challan. "
                    "The receiving signature is what proves delivery."))
        self.write({"state": "delivered",
                    "received_date": fields.Date.context_today(self)})

    def action_cancel(self):
        for rec in self:
            if rec.state in ("issued", "delivered"):
                raise UserError(_(
                    "LOG-003 — the goods have already left the store. Raise a return "
                    "GSRN instead of cancelling the challan."))
        self.write({"state": "cancelled"})


class McbChallanLine(models.Model):
    _name = "mcb.challan.line"
    _description = "MCB Challan Material Line"
    _order = "sequence, id"

    challan_id = fields.Many2one("mcb.challan", required=True, ondelete="cascade")
    sequence = fields.Integer(default=10)
    product_id = fields.Many2one("product.product", required=True,
                                 string="Name of Materials")
    uom_id = fields.Many2one("uom.uom", string="Unit")
    qty_issued = fields.Float(string="Issued Quantity", digits="Product Unit of Measure")
    bin_card_id = fields.Many2one("mcb.bin.card", string="Stock Register Folio",
                                  readonly=True,
                                  help="The bin/stack card this issue was written on — "
                                       "the printed form's 'Stock Register Folio'.")
    remarks = fields.Char()

    @api.onchange("product_id")
    def _onchange_product(self):
        for line in self:
            if line.product_id:
                line.uom_id = line.product_id.uom_id
