from odoo import api, fields, models, _
from odoo.exceptions import UserError


class McbSrf(models.Model):
    """LOG-004 — the field-office Materials Requisition Note.

    mcb_store already models the store requisition and its issue picking. The printed
    field form carries a little more than that model does: a 'within date' by which the
    goods are needed, the present stock balance the requester saw, the recommending and
    reviewing signatures, and the 'office use only' box that ties the requisition to the
    challan it was finally delivered against.
    """
    _inherit = "mcb.srf"

    within_date = fields.Date(
        string="Required Within",
        help="The printed form's 'With in Date' — when the requester needs the goods.")
    requester_designation = fields.Char(string="Designation")
    lc_name = fields.Char(string="LC Name / Purpose")
    makeshift_settlement = fields.Char(string="Makeshift Settlements")

    recommended_by_id = fields.Many2one("res.users", string="Recommended By",
                                        readonly=True, copy=False)
    reviewed_by_id = fields.Many2one("res.users", string="Reviewed By",
                                     readonly=True, copy=False)
    pc_approved_by_id = fields.Many2one("res.users", string="P.C.",
                                        readonly=True, copy=False)

    challan_ids = fields.One2many("mcb.challan", "srf_id", string="Challans")
    challan_count = fields.Integer(compute="_compute_challan_count")

    def _compute_challan_count(self):
        for rec in self:
            rec.challan_count = len(rec.challan_ids)

    def action_recommend(self):
        self.write({"recommended_by_id": self.env.user.id})

    def action_review(self):
        self.write({"reviewed_by_id": self.env.user.id})

    def action_pc_approve(self):
        """The fourth signature on the printed form."""
        self.write({"pc_approved_by_id": self.env.user.id})

    def action_approve(self):
        """FMM 12.12 segregation of duties — whoever raised the requisition must not be
        the person who approves it."""
        for rec in self:
            if rec.requester_id and rec.requester_id == self.env.user:
                raise UserError(_(
                    "LOG-004 — %(user)s raised this requisition, so the same person "
                    "cannot approve it. Segregation of duties applies to store issues.",
                    user=self.env.user.name))
        return super().action_approve()

    def action_issue(self):
        """mcb_store confirms the transfer but never validates it, so issued goods were
        never actually deducted from stock. Validate it here."""
        res = super().action_issue()
        for rec in self:
            picking = rec.picking_id
            if not picking or picking.state in ("done", "cancel"):
                continue
            try:
                picking.action_assign()
                for move in picking.move_ids:
                    move.quantity = move.product_uom_qty
                    move.picked = True
                picking.button_validate()
            except Exception as exc:            # noqa: BLE001 - surfaced to the user
                raise UserError(_(
                    "LOG-004 — the goods could not be taken out of stock: %s\n\n"
                    "Check that the store actually holds the quantity requested.",
                    str(exc)[:300])) from exc
        return res

    def action_create_challan(self):
        """Raise the Materials Supply Note that will carry these goods to the field."""
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "res_model": "mcb.challan",
            "view_mode": "form",
            "context": {
                "default_srf_id": self.id,
                "default_project_id": self.project_id.id,
                "default_recipient_name": self.recipient_name,
            },
        }

    def action_view_challans(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Challans",
            "res_model": "mcb.challan",
            "view_mode": "list,form",
            "domain": [("srf_id", "=", self.id)],
        }


class McbSrfLine(models.Model):
    _inherit = "mcb.srf.line"

    present_stock_balance = fields.Float(
        string="Present Stock Balance", digits="Product Unit of Measure",
        help="What the requester saw on the shelf when raising the requisition.")
    on_hand_now = fields.Float(string="On Hand (system)", compute="_compute_on_hand",
                               digits="Product Unit of Measure")
    remarks = fields.Char()

    @api.depends("product_id")
    def _compute_on_hand(self):
        for line in self:
            line.on_hand_now = line.product_id.qty_available if line.product_id else 0.0
