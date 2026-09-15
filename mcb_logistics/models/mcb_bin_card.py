from odoo import api, fields, models, _
from odoo.exceptions import UserError


class McbBinCard(models.Model):
    """LOG-005 — Bin / Stack Card.

    SOP: 'One bin/stack should only comprise one type of item from one unique Purchase
    Order (PO) number.' The card shows the beginning balance, the movements in and out
    and the current balance of an item at any given time, and must be updated as soon as
    an item is moved in or out.
    """
    _name = "mcb.bin.card"
    _description = "MCB Bin / Stack Card"
    _inherit = ["mail.thread"]
    _order = "warehouse_id, product_id, id"

    name = fields.Char(compute="_compute_name", store=True)
    warehouse_id = fields.Many2one("stock.warehouse", required=True, string="Warehouse Name")
    location_id = fields.Many2one("stock.location", string="Bin / Stack Location",
                                  domain="[('usage', '=', 'internal')]")
    product_id = fields.Many2one("product.product", required=True, string="Item Name")
    uom_id = fields.Many2one(related="product_id.uom_id", string="Unit of Measurement")
    purchase_order_id = fields.Many2one("purchase.order", string="PO Number")
    po_reference = fields.Char(
        string="PO / Source Reference",
        help="Free text for goods that arrive without an MCB purchase order — an in-kind "
             "donation from a donor, a UN agency or GoB.")
    lot_id = fields.Many2one("stock.lot", string="Batch No")
    expiry_date = fields.Date(string="Shelf Life Expiry Date")
    page_no = fields.Char(string="Page Number")

    opening_balance = fields.Float(string="Opening Balance", digits="Product Unit of Measure")
    line_ids = fields.One2many("mcb.bin.card.line", "card_id", string="Movements")
    balance = fields.Float(string="Closing Balance", compute="_compute_balance", store=True,
                           digits="Product Unit of Measure")
    total_in = fields.Float(compute="_compute_balance", store=True,
                            digits="Product Unit of Measure")
    total_out = fields.Float(compute="_compute_balance", store=True,
                             digits="Product Unit of Measure")
    active = fields.Boolean(default=True)
    company_id = fields.Many2one("res.company", default=lambda s: s.env.company)

    _unique_card = models.Constraint(
        "unique(warehouse_id, product_id, purchase_order_id, location_id, lot_id)",
        "One bin/stack card already exists for this item, PO, batch and location. "
        "The SOP allows only one card per item per PO per bin.")

    @api.depends("product_id", "purchase_order_id", "po_reference", "location_id")
    def _compute_name(self):
        for rec in self:
            src = rec.purchase_order_id.name or rec.po_reference or _("No PO")
            loc = rec.location_id.name or "-"
            rec.name = f"{rec.product_id.name or ''} · {src} · {loc}"

    @api.depends("opening_balance", "line_ids.qty_in", "line_ids.qty_out")
    def _compute_balance(self):
        for rec in self:
            rec.total_in = sum(rec.line_ids.mapped("qty_in"))
            rec.total_out = sum(rec.line_ids.mapped("qty_out"))
            rec.balance = rec.opening_balance + rec.total_in - rec.total_out

    # ------------------------------------------------------------------ api --
    @api.model
    def _mcb_get_or_create(self, product, warehouse, location=None, purchase_order=None,
                           po_reference=None, lot=None):
        """Find the card this movement belongs to, or open a new one.

        Called by the GSRN when goods come in and by the Challan when they go out, so
        the card is written at the moment of the movement — as the SOP requires.
        """
        domain = [
            ("product_id", "=", product.id),
            ("warehouse_id", "=", warehouse.id),
            ("purchase_order_id", "=", purchase_order.id if purchase_order else False),
            ("location_id", "=", location.id if location else False),
            ("lot_id", "=", lot.id if lot else False),
        ]
        card = self.search(domain, limit=1)
        if card:
            return card
        return self.create({
            "product_id": product.id,
            "warehouse_id": warehouse.id,
            "location_id": location.id if location else False,
            "purchase_order_id": purchase_order.id if purchase_order else False,
            "po_reference": po_reference or False,
            "lot_id": lot.id if lot else False,
            "expiry_date": lot.expiration_date.date()
            if lot and lot.expiration_date else False,
        })

    def _mcb_post_movement(self, date, party, doc_ref, qty_in=0.0, qty_out=0.0,
                           recorded_by=None, remarks=None):
        self.ensure_one()
        if qty_out and qty_out > self.balance:
            raise UserError(_(
                "LOG-005 — bin/stack card '%(card)s' holds only %(bal).2f %(uom)s, but "
                "%(out).2f is being issued. Check the card before issuing.",
                card=self.name, bal=self.balance,
                uom=self.uom_id.name or "", out=qty_out))
        return self.env["mcb.bin.card.line"].create({
            "card_id": self.id,
            "date": date,
            "party_name": party,
            "doc_reference": doc_ref,
            "qty_in": qty_in,
            "qty_out": qty_out,
            "recorded_by_id": (recorded_by or self.env.user).id,
            "remarks": remarks or False,
        })


class McbBinCardLine(models.Model):
    """One printed line of the bin card — one movement, signed by the record keeper."""
    _name = "mcb.bin.card.line"
    _description = "MCB Bin / Stack Card Movement"
    _order = "date, id"

    card_id = fields.Many2one("mcb.bin.card", required=True, ondelete="cascade")
    date = fields.Date(required=True, default=fields.Date.context_today)
    party_name = fields.Char(string="Name (Requester / Vendor)")
    doc_reference = fields.Char(string="Challan / Waybill / GRN No")
    qty_in = fields.Float(string="Receive (IN)", digits="Product Unit of Measure")
    qty_out = fields.Float(string="Dispatch (OUT)", digits="Product Unit of Measure")
    running_balance = fields.Float(string="Closing Balance", compute="_compute_running",
                                   digits="Product Unit of Measure")
    recorded_by_id = fields.Many2one("res.users", string="Record Keeper",
                                     default=lambda s: s.env.user)
    remarks = fields.Char()

    @api.depends("card_id", "card_id.line_ids", "qty_in", "qty_out", "date")
    def _compute_running(self):
        """The printed card carries a running balance on every line, so recompute the
        whole card in date order whenever any line changes."""
        for card in self.mapped("card_id"):
            bal = card.opening_balance
            for line in card.line_ids.sorted(lambda l: (l.date or fields.Date.today(), l.id)):
                bal += line.qty_in - line.qty_out
                line.running_balance = bal
        for line in self.filtered(lambda l: not l.card_id):
            line.running_balance = line.qty_in - line.qty_out
