from odoo import api, fields, models, _
from odoo.exceptions import UserError

from .mcb_advance import add_working_days


class McbIou(models.Model):
    """Annexure-13 — IOU / Cash Requisition (PCH-006 + client-feedback ADV-008)."""
    _name = "mcb.iou"
    _description = "MCB IOU / Cash Requisition (Annexure-13)"
    _inherit = ["mail.thread", "mail.activity.mixin", "mcb.fy.mixin"]
    _order = "create_date desc"

    name = fields.Char(default="New", copy=False, readonly=True)
    employee_id = fields.Many2one("hr.employee", required=True, tracking=True,
                                  default=lambda s: s.env.user.employee_id)
    project_analytic_id = fields.Many2one("account.analytic.account", string="Project / Donor")
    funded_by = fields.Char()
    purpose = fields.Char(string="Purpose of IOU", required=True)
    amount = fields.Monetary(required=True, currency_field="currency_id", tracking=True)
    amount_in_words = fields.Char(compute="_compute_words")
    currency_id = fields.Many2one("res.currency", default=lambda s: s.env.company.currency_id)
    company_id = fields.Many2one("res.company", default=lambda s: s.env.company, required=True)
    journal_id = fields.Many2one(
        "account.journal", string="Pay From (Cash)", domain="[('type', '=', 'cash')]")
    days_to_adjust = fields.Integer(default=5, string="Adjust Within (working days)")
    receiving_date = fields.Date(readonly=True, copy=False)
    adjust_deadline = fields.Date(compute="_compute_deadline", store=True)
    payment_move_id = fields.Many2one("account.move", readonly=True, copy=False)
    settle_move_id = fields.Many2one("account.move", readonly=True, copy=False)
    settle_amount_spent = fields.Monetary(currency_field="currency_id")
    settle_account_id = fields.Many2one(
        "account.account", string="Expense Head",
        domain="[('account_type', 'in', ('expense', 'expense_direct_cost'))]")
    state = fields.Selection([
        ("draft", "Draft"),
        ("submitted", "Submitted"),
        ("approved", "Approved"),
        ("paid", "Cash Paid"),
        ("adjusted", "Adjusted"),
        ("cancelled", "Cancelled"),
    ], default="draft", tracking=True)

    @api.depends("amount", "currency_id")
    def _compute_words(self):
        for rec in self:
            rec.amount_in_words = rec.currency_id.amount_to_text(rec.amount) if rec.amount else ""

    @api.depends("receiving_date", "days_to_adjust")
    def _compute_deadline(self):
        for rec in self:
            rec.adjust_deadline = (
                add_working_days(rec.receiving_date, rec.days_to_adjust)
                if rec.receiving_date else False)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self._mcb_fy_sequence_next("mcb.iou", "IOU")
        return super().create(vals_list)

    def action_submit(self):
        for rec in self:
            other = self.search([
                ("employee_id", "=", rec.employee_id.id),
                ("state", "=", "paid"), ("id", "!=", rec.id)], limit=1)
            if other:
                raise UserError(_(
                    "%(emp)s has an outstanding IOU %(iou)s — adjust it first "
                    "(Annexure-13 commitment).", emp=rec.employee_id.name, iou=other.name))
        self.write({"state": "submitted"})

    def action_approve(self):
        self.write({"state": "approved"})

    def _advance_account(self):
        acc = self.env["account.account"].search(
            [("code", "=", "102910"), ("company_ids", "in", self.company_id.id)], limit=1)
        if not acc:
            raise UserError(_("Employee Advances account (102910) missing."))
        return acc

    def action_pay(self):
        for rec in self:
            if not rec.journal_id:
                raise UserError(_("Choose the cash journal."))
            partner = rec.employee_id.work_contact_id or rec.employee_id.user_id.partner_id
            move = self.env["account.move"].with_context(mcb_skip_approval=True).create({
                "move_type": "entry",
                "journal_id": rec.journal_id.id,
                "date": fields.Date.context_today(self),
                "ref": _("IOU %s — %s", rec.name, rec.purpose),
                "line_ids": [
                    (0, 0, {"account_id": rec._advance_account().id,
                            "partner_id": partner.id if partner else False,
                            "name": rec.purpose, "debit": rec.amount}),
                    (0, 0, {"account_id": rec.journal_id.default_account_id.id,
                            "name": rec.name, "credit": rec.amount}),
                ],
            })
            move.action_post()
            rec.write({"payment_move_id": move.id,
                       "receiving_date": move.date, "state": "paid"})

    def action_adjust(self):
        """Settle: Dr expense (spent) / Cr advance (full) / cash line for the difference."""
        for rec in self:
            if not rec.settle_account_id or rec.settle_amount_spent <= 0:
                raise UserError(_("Set the expense head and the amount actually spent."))
            dist = ({str(rec.project_analytic_id.id): 100}
                    if rec.project_analytic_id else False)
            diff = rec.settle_amount_spent - rec.amount
            lines = [
                (0, 0, {"account_id": rec.settle_account_id.id, "name": rec.purpose,
                        "debit": rec.settle_amount_spent, "analytic_distribution": dist}),
                (0, 0, {"account_id": rec._advance_account().id,
                        "name": _("Clear IOU %s", rec.name), "credit": rec.amount}),
            ]
            if abs(diff) >= 0.005:
                lines.append((0, 0, {
                    "account_id": rec.journal_id.default_account_id.id,
                    "name": _("IOU refund") if diff < 0 else _("IOU extra payment"),
                    "debit": -diff if diff < 0 else 0.0,
                    "credit": diff if diff > 0 else 0.0,
                }))
            move = self.env["account.move"].with_context(mcb_skip_approval=True).create({
                "move_type": "entry", "journal_id": rec.journal_id.id,
                "date": fields.Date.context_today(self),
                "ref": _("IOU adjustment %s", rec.name), "line_ids": lines,
            })
            move.action_post()
            rec.write({"settle_move_id": move.id, "state": "adjusted"})

    def action_cancel(self):
        self.write({"state": "cancelled"})

    @api.model
    def _cron_iou_reminder(self):
        today = fields.Date.context_today(self)
        for iou in self.search([("state", "=", "paid"), ("adjust_deadline", "<=", today)]):
            user = iou.employee_id.user_id
            if user:
                iou.activity_schedule(
                    "mail.mail_activity_data_todo", user_id=user.id,
                    summary=_("IOU %s adjustment overdue", iou.name),
                    note=_("Adjust the IOU taken on %s (%.2f BDT).",
                           iou.receiving_date, iou.amount))
