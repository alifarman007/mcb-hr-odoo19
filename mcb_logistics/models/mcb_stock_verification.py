from odoo import api, fields, models, _
from odoo.exceptions import UserError


class McbStockVerification(models.Model):
    """LOG-006 — Physical Inventory Verification.

    SOP, quarterly: 'The Store keeper/officer in charge for inventories in coordination
    with the Project warehouse focal point and guidance from Coordinator Finance &
    Accounts must conduct a full Physical Inventory Verification quarterly. Any
    discrepancy between the physical inventory as per count sheets and the Automation
    Inventory software stock records must be investigated and explained.'

    Also used for the yearly count and for the handover count when a storekeeper
    changes — the SOP requires a full verification on any change of custody.
    """
    _name = "mcb.stock.verification"
    _description = "MCB Physical Stock Verification"
    _inherit = ["mail.thread", "mail.activity.mixin", "mcb.fy.mixin"]
    _order = "date desc, id desc"

    name = fields.Char(default="New", copy=False, readonly=True, index=True)
    verification_type = fields.Selection([
        ("quarterly", "Quarterly"),
        ("yearly", "Yearly"),
        ("handover", "Handover of custody"),
        ("adhoc", "Ad-hoc / High turnover"),
    ], default="quarterly", required=True, tracking=True)
    date = fields.Date(string="Count Date", required=True,
                       default=fields.Date.context_today, tracking=True)
    warehouse_id = fields.Many2one("stock.warehouse", required=True, tracking=True)
    project_id = fields.Many2one("project.project", string="Project / Office")
    period_label = fields.Char(string="Period",
                               help="e.g. Q2 FY 26-27, or the financial year for a yearly count.")

    # SOP: storekeeper + project warehouse focal + Coordinator Finance & Accounts
    storekeeper_id = fields.Many2one("hr.employee", string="Store Keeper")
    focal_point_id = fields.Many2one("hr.employee", string="Project Warehouse Focal Point")
    finance_coordinator_id = fields.Many2one("hr.employee",
                                             string="Coordinator, Finance & Accounts")
    committee_ids = fields.Many2many("hr.employee", string="Other Committee Members")

    # handover only
    outgoing_keeper_id = fields.Many2one("hr.employee", string="Outgoing Store Keeper")
    incoming_keeper_id = fields.Many2one("hr.employee", string="Incoming Store Keeper")

    line_ids = fields.One2many("mcb.stock.verification.line", "verification_id",
                               string="Count Sheet")
    discrepancy_count = fields.Integer(compute="_compute_discrepancy", store=True)
    has_discrepancy = fields.Boolean(compute="_compute_discrepancy", store=True)
    explanation = fields.Text(
        string="Explanation of Discrepancies",
        help="SOP: every discrepancy must be investigated and explained, and the full "
             "documentation sent to Senior Management.")
    company_id = fields.Many2one("res.company", default=lambda s: s.env.company)

    state = fields.Selection([
        ("draft", "Draft"),
        ("counting", "Counting"),
        ("reconciled", "Reconciled"),
        ("submitted", "Submitted to Management"),
        ("cancelled", "Cancelled"),
    ], default="draft", tracking=True)

    @api.depends("line_ids.difference")
    def _compute_discrepancy(self):
        for rec in self:
            diffs = rec.line_ids.filtered(lambda l: abs(l.difference) > 0.0001)
            rec.discrepancy_count = len(diffs)
            rec.has_discrepancy = bool(diffs)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self._mcb_fy_sequence_next("mcb.stock.verification",
                                                          "PIV", padding=3)
        return super().create(vals_list)

    # ------------------------------------------------------------- workflow --
    def action_load_stock(self):
        """Build the count sheet from what the system currently believes is on hand."""
        for rec in self:
            if not rec.warehouse_id.lot_stock_id:
                raise UserError(_("Warehouse '%s' has no stock location.",
                                  rec.warehouse_id.display_name))
            quants = self.env["stock.quant"].search([
                ("location_id", "child_of", rec.warehouse_id.lot_stock_id.id),
                ("quantity", "!=", 0),
            ])
            rec.line_ids.unlink()
            lines = []
            for q in quants:
                card = self.env["mcb.bin.card"].search([
                    ("product_id", "=", q.product_id.id),
                    ("warehouse_id", "=", rec.warehouse_id.id),
                ], limit=1)
                lines.append((0, 0, {
                    "product_id": q.product_id.id,
                    "location_id": q.location_id.id,
                    "lot_id": q.lot_id.id if q.lot_id else False,
                    "uom_id": q.product_id.uom_id.id,
                    "qty_system": q.quantity,
                    "qty_physical": q.quantity,
                    "bin_card_id": card.id if card else False,
                }))
            rec.line_ids = lines
            rec.state = "counting"
            if not lines:
                raise UserError(_(
                    "There is no stock on hand in warehouse '%s', so there is nothing to "
                    "count. Post a GSRN first.", rec.warehouse_id.display_name))

    def action_reconcile(self):
        for rec in self:
            if not rec.line_ids:
                raise UserError(_("LOG-006 — load the count sheet first."))
            missing = rec.line_ids.filtered(
                lambda l: abs(l.difference) > 0.0001 and not l.reason)
            if missing:
                raise UserError(_(
                    "LOG-006 — %(n)d line(s) differ from the system but carry no reason. "
                    "The SOP requires every discrepancy to be investigated and explained "
                    "before the count can be reconciled.\n\nFirst one: %(item)s "
                    "(system %(sys).2f, counted %(phys).2f).",
                    n=len(missing), item=missing[0].product_id.display_name,
                    sys=missing[0].qty_system, phys=missing[0].qty_physical))
        self.write({"state": "reconciled"})

    def action_submit(self):
        for rec in self:
            if rec.state != "reconciled":
                raise UserError(_("Reconcile the count before submitting it."))
            if rec.has_discrepancy and not rec.explanation:
                raise UserError(_(
                    "LOG-006 — this count found %(n)d discrepancy(ies). Write the overall "
                    "explanation before sending the documentation to Senior Management.",
                    n=rec.discrepancy_count))
            if rec.verification_type == "handover" and not (
                    rec.outgoing_keeper_id and rec.incoming_keeper_id):
                raise UserError(_(
                    "LOG-006 — a handover count must name both the outgoing and the "
                    "incoming store keeper. Both sign the updated records."))
        self.write({"state": "submitted"})

    def action_cancel(self):
        self.write({"state": "cancelled"})

    def action_draft(self):
        self.write({"state": "draft"})


class McbStockVerificationLine(models.Model):
    _name = "mcb.stock.verification.line"
    _description = "MCB Stock Verification Count Line"
    _order = "id"

    verification_id = fields.Many2one("mcb.stock.verification", required=True,
                                      ondelete="cascade")
    product_id = fields.Many2one("product.product", required=True, string="Item")
    location_id = fields.Many2one("stock.location", string="Location")
    lot_id = fields.Many2one("stock.lot", string="Batch No")
    bin_card_id = fields.Many2one("mcb.bin.card", string="Bin / Stack Card")
    uom_id = fields.Many2one("uom.uom", string="Unit")
    qty_system = fields.Float(string="As per System", digits="Product Unit of Measure")
    qty_physical = fields.Float(string="Physically Counted", digits="Product Unit of Measure")
    difference = fields.Float(compute="_compute_difference", store=True,
                              digits="Product Unit of Measure",
                              string="Short / Excess")
    reason = fields.Char(string="Reason / Investigation")
    action_taken = fields.Selection([
        ("adjust", "Adjust stock"),
        ("investigate", "Under investigation"),
        ("dispose", "Refer for disposal"),
        ("none", "No action"),
    ], string="Action")

    @api.depends("qty_system", "qty_physical")
    def _compute_difference(self):
        for line in self:
            line.difference = (line.qty_physical or 0.0) - (line.qty_system or 0.0)
