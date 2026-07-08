from odoo import api, fields, models, _
from odoo.exceptions import UserError

NOAL_THRESHOLD_BDT = 500_000
APPROVAL_THRESHOLD_BDT = 10_000


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    # PO-002 — separate PO / CO / WO sequences
    mcb_po_type = fields.Selection([
        ("po", "Purchase Order"),
        ("co", "Contract Order"),
        ("wo", "Work Order"),
    ], default="po", string="Order Type", tracking=True)
    mcb_order_ref = fields.Char(string="PO/CO/WO Number", copy=False, readonly=True)
    mcb_pr_id = fields.Many2one("mcb.purchase.request", string="Purchase Request",
                                index=True)
    mcb_evaluation_id = fields.Many2one("mcb.vendor.evaluation", string="Evaluation")
    mcb_noal_id = fields.Many2one("mcb.noal", string="NOAL", copy=False)
    mcb_noal_required = fields.Boolean(compute="_compute_noal_required", store=True)

    # PO-008 — 4-level authorization with real users/dates
    mcb_checked_by_id = fields.Many2one("res.users", readonly=True, copy=False,
                                        string="Checked By")
    mcb_reviewed_by_id = fields.Many2one("res.users", readonly=True, copy=False,
                                         string="Reviewed By")
    mcb_approved_by_id = fields.Many2one("res.users", readonly=True, copy=False,
                                         string="Approved By (CE)")

    @api.depends("amount_total", "currency_id", "company_id")
    def _compute_noal_required(self):
        for po in self:
            amount_company = po.currency_id._convert(
                po.amount_total, po.company_id.currency_id,
                po.company_id, po.date_order or fields.Date.context_today(po))
            po.mcb_noal_required = amount_company >= NOAL_THRESHOLD_BDT

    def action_mcb_check(self):
        self.write({"mcb_checked_by_id": self.env.user.id})

    def action_mcb_review(self):
        for po in self:
            if not po.mcb_checked_by_id:
                raise UserError(_("PO must be Checked first (PO-008)."))
        self.write({"mcb_reviewed_by_id": self.env.user.id})

    def action_mcb_approve(self):
        for po in self:
            if not po.mcb_reviewed_by_id:
                raise UserError(_("PO must be Reviewed first (PO-008)."))
        self.write({"mcb_approved_by_id": self.env.user.id})

    def _mcb_pre_confirm_gates(self):
        for po in self:
            amount_company = po.currency_id._convert(
                po.amount_total, po.company_id.currency_id,
                po.company_id, po.date_order or fields.Date.context_today(po))
            # NOAL-006 — no confirmation ≥ 5,00,000 without an issued NOAL
            if amount_company >= NOAL_THRESHOLD_BDT:
                if not po.mcb_noal_id or po.mcb_noal_id.state == "draft":
                    raise UserError(_(
                        "NOAL-006 — order %(po)s (%(amt).2f BDT) is at/above 5,00,000: an "
                        "issued Notification of Award Letter is required before confirmation.",
                        po=po.name, amt=amount_company))
            # PO-008 — 4-level authorization gate above the direct-purchase threshold
            if amount_company >= APPROVAL_THRESHOLD_BDT and not po.mcb_approved_by_id:
                raise UserError(_(
                    "PO-008 — order %(po)s requires the 4-level authorization "
                    "(Checked → Reviewed → Approved) before confirmation.", po=po.name))
            # BUD-004 (committed side) — budget guard through the linked PR head
            pr = po.mcb_pr_id
            if pr and pr.budget_line_id:
                bl = pr.budget_line_id
                projected = bl.achieved_amount + amount_company
                if projected > bl.budget_amount and bl.budget_amount > 0:
                    budget = bl.budget_analytic_id
                    msg = _(
                        "BUD-004 — confirming %(po)s would take head '%(head)s' to "
                        "%(proj).2f against a budget of %(bud).2f.",
                        po=po.name, head=bl.display_name,
                        proj=projected, bud=bl.budget_amount)
                    if budget.mcb_locked:
                        raise UserError(_("BUD-008 — budget '%s' is locked.", budget.name))
                    if budget.mcb_overage_policy == "block":
                        raise UserError(msg)
                    po.message_post(body=msg)

    def button_confirm(self):
        self._mcb_pre_confirm_gates()
        res = super().button_confirm()
        for po in self:
            if not po.mcb_order_ref:
                seq_code = f"mcb.order.{po.mcb_po_type}"
                po.mcb_order_ref = self.env["ir.sequence"].next_by_code(seq_code) or po.name
            if po.mcb_pr_id:
                po.mcb_pr_id.write({
                    "state": "po_issued",
                    "date_po_issued": fields.Datetime.now(),
                })
        return res

    def button_approve(self, force=False):
        self._mcb_pre_confirm_gates()
        return super().button_approve(force=force)
