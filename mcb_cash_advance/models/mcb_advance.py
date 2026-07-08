from datetime import timedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


def add_working_days(start, days):
    """Bangladesh weekend = Friday & Saturday (weekday 4, 5)."""
    d, added = start, 0
    while added < days:
        d = d + timedelta(days=1)
        if d.weekday() not in (4, 5):
            added += 1
    return d


class McbAdvance(models.Model):
    """Annexure-18 — Advance Request; full lifecycle ADV-001..007."""
    _name = "mcb.advance"
    _description = "MCB Advance Request (Annexure-18)"
    _inherit = ["mail.thread", "mail.activity.mixin", "mcb.fy.mixin"]
    _order = "create_date desc"

    name = fields.Char(default="New", copy=False, readonly=True)
    employee_id = fields.Many2one("hr.employee", required=True, tracking=True,
                                  default=lambda s: s.env.user.employee_id)
    project_analytic_id = fields.Many2one(
        "account.analytic.account", string="Project / Donor", tracking=True)
    funded_by = fields.Char()
    activity_name = fields.Char(string="Name of Activity", required=True)
    account_id = fields.Many2one(
        "account.account", string="Accounts Head",
        help="Expense head the advance is drawn against (Annexure-18).")
    required_date = fields.Date(string="Advance Requirement Date",
                                default=fields.Date.context_today)
    line_ids = fields.One2many("mcb.advance.line", "advance_id", string="Itemised Budget")
    amount = fields.Monetary(compute="_compute_amount", store=True,
                             currency_field="currency_id", tracking=True)
    amount_in_words = fields.Char(compute="_compute_words")
    currency_id = fields.Many2one("res.currency", default=lambda s: s.env.company.currency_id)
    company_id = fields.Many2one("res.company", default=lambda s: s.env.company, required=True)
    journal_id = fields.Many2one(
        "account.journal", string="Pay From", domain="[('type', 'in', ('bank', 'cash'))]")
    payment_move_id = fields.Many2one("account.move", readonly=True, copy=False)
    date_paid = fields.Date(readonly=True, copy=False)
    adjust_deadline = fields.Date(
        compute="_compute_deadline", store=True,
        help="ADV-005 — adjustment due within 5 working days of payment.")
    adjustment_ids = fields.One2many("mcb.advance.adjustment", "advance_id")
    outstanding = fields.Monetary(compute="_compute_outstanding", store=True,
                                  currency_field="currency_id")
    finance_comment = fields.Char(string="Finance Comments")
    state = fields.Selection([
        ("draft", "Draft"),
        ("submitted", "Submitted"),
        ("finance", "Finance Checked"),
        ("reviewed", "Reviewed"),
        ("approved", "Approved"),
        ("paid", "Paid"),
        ("adjusted", "Adjusted / Closed"),
        ("cancelled", "Cancelled"),
    ], default="draft", tracking=True)

    @api.depends("line_ids.amount")
    def _compute_amount(self):
        for rec in self:
            rec.amount = sum(rec.line_ids.mapped("amount"))

    @api.depends("amount", "currency_id")
    def _compute_words(self):
        for rec in self:
            rec.amount_in_words = rec.currency_id.amount_to_text(rec.amount) if rec.amount else ""

    @api.depends("date_paid")
    def _compute_deadline(self):
        for rec in self:
            rec.adjust_deadline = add_working_days(rec.date_paid, 5) if rec.date_paid else False

    @api.depends("state", "amount", "adjustment_ids.state")
    def _compute_outstanding(self):
        # The settlement JE credits the FULL advance and cash-settles any
        # difference (ADV-007), so one approved adjustment always clears it.
        for rec in self:
            if rec.state == "paid" and not rec.adjustment_ids.filtered(
                    lambda a: a.state == "approved"):
                rec.outstanding = rec.amount
            else:
                rec.outstanding = 0.0

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self._mcb_fy_sequence_next("mcb.advance", "ADV")
        return super().create(vals_list)

    # ---- ADV-003: block a new advance while one is outstanding ----
    def action_submit(self):
        for rec in self:
            other = self.search([
                ("employee_id", "=", rec.employee_id.id),
                ("state", "=", "paid"),
                ("outstanding", ">", 0),
                ("id", "!=", rec.id),
            ], limit=1)
            if other:
                raise UserError(_(
                    "ADV-003 — %(emp)s still has unadjusted advance %(adv)s "
                    "(outstanding %(amt).2f). Adjust it before requesting a new one.",
                    emp=rec.employee_id.name, adv=other.name, amt=other.outstanding))
            if not rec.line_ids:
                raise ValidationError(_("Add at least one itemised budget line (Annexure-18)."))
        self.write({"state": "submitted"})

    def action_finance_check(self):
        self.write({"state": "finance"})

    def action_review(self):
        self.write({"state": "reviewed"})

    def action_approve(self):
        self.write({"state": "approved"})

    def action_pay(self):
        """Dr Employee Advances / Cr cash-bank — posts the advance out (ADV-002 end)."""
        for rec in self:
            if not rec.journal_id:
                raise UserError(_("Choose the cash/bank journal to pay from."))
            advance_acc = self.env["account.account"].search(
                [("code", "=", "102910"), ("company_ids", "in", rec.company_id.id)], limit=1)
            if not advance_acc:
                raise UserError(_("Employee Advances account (102910) missing."))
            partner = rec.employee_id.work_contact_id or rec.employee_id.user_id.partner_id
            dist = {str(rec.project_analytic_id.id): 100} if rec.project_analytic_id else False
            move = self.env["account.move"].with_context(mcb_skip_approval=True).create({
                "move_type": "entry",
                "journal_id": rec.journal_id.id,
                "date": fields.Date.context_today(self),
                "ref": _("Advance %s — %s", rec.name, rec.activity_name),
                "line_ids": [
                    (0, 0, {
                        "account_id": advance_acc.id,
                        "partner_id": partner.id if partner else False,
                        "name": rec.activity_name,
                        "debit": rec.amount,
                        "analytic_distribution": dist,
                    }),
                    (0, 0, {
                        "account_id": rec.journal_id.default_account_id.id,
                        "name": rec.name,
                        "credit": rec.amount,
                    }),
                ],
            })
            move.action_post()
            rec.write({"payment_move_id": move.id, "date_paid": move.date, "state": "paid"})

    def action_cancel(self):
        self.write({"state": "cancelled"})

    # ---- ADV-005 cron: reminder before/after deadline ----
    @api.model
    def _cron_adjustment_reminder(self):
        today = fields.Date.context_today(self)
        overdue = self.search([("state", "=", "paid"), ("adjust_deadline", "<=", today)])
        for adv in overdue:
            users = adv.employee_id.user_id | adv.employee_id.parent_id.user_id
            for user in users:
                adv.activity_schedule(
                    "mail.mail_activity_data_todo",
                    user_id=user.id,
                    summary=_("Advance %s adjustment overdue", adv.name),
                    note=_("ADV-005 — the advance must be adjusted within 5 working days "
                           "of activity completion. Outstanding: %.2f", adv.outstanding),
                )


class McbAdvanceLine(models.Model):
    _name = "mcb.advance.line"
    _description = "Advance Itemised Budget Line"

    advance_id = fields.Many2one("mcb.advance", required=True, ondelete="cascade")
    name = fields.Char(string="Particulars", required=True)
    amount = fields.Monetary(currency_field="currency_id")
    remarks = fields.Char()
    currency_id = fields.Many2one(related="advance_id.currency_id")


class McbAdvanceAdjustment(models.Model):
    """Annexure-19 — Advance Adjustment (ADV-004/007)."""
    _name = "mcb.advance.adjustment"
    _description = "MCB Advance Adjustment (Annexure-19)"
    _inherit = ["mail.thread", "mcb.fy.mixin"]

    name = fields.Char(default="New", copy=False, readonly=True)
    advance_id = fields.Many2one("mcb.advance", required=True, ondelete="restrict",
                                 domain="[('state', '=', 'paid')]")
    employee_id = fields.Many2one(related="advance_id.employee_id", store=True)
    company_id = fields.Many2one(related="advance_id.company_id", store=True)
    currency_id = fields.Many2one(related="advance_id.currency_id")
    date_adjustment = fields.Date(default=fields.Date.context_today, required=True)
    line_ids = fields.One2many("mcb.advance.adjustment.line", "adjustment_id")
    amount_received = fields.Monetary(related="advance_id.amount", string="Amount Received")
    amount_spent = fields.Monetary(compute="_compute_amounts", store=True,
                                   currency_field="currency_id")
    amount_diff = fields.Monetary(
        compute="_compute_amounts", store=True, currency_field="currency_id",
        string="Claimable (+) / Refundable (−)",
        help="Positive: MCB owes the employee extra; negative: employee refunds cash.")
    settle_move_id = fields.Many2one("account.move", readonly=True, copy=False)
    state = fields.Selection([
        ("draft", "Draft"),
        ("submitted", "Submitted"),
        ("approved", "Approved / Settled"),
    ], default="draft", tracking=True)

    @api.depends("line_ids.amount", "amount_received")
    def _compute_amounts(self):
        for rec in self:
            rec.amount_spent = sum(rec.line_ids.mapped("amount"))
            rec.amount_diff = rec.amount_spent - rec.amount_received

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self._mcb_fy_sequence_next("mcb.advance.adjust", "ADJ")
        return super().create(vals_list)

    def action_submit(self):
        for rec in self:
            if not rec.line_ids:
                raise UserError(_("Add itemised expenditure lines (Annexure-19)."))
        self.write({"state": "submitted"})

    def action_approve(self):
        """ADV-007 — one settlement JE: Dr expenses, Cr Employee Advances,
        cash line balances refund/extra automatically."""
        for rec in self:
            adv = rec.advance_id
            advance_acc = self.env["account.account"].search(
                [("code", "=", "102910"), ("company_ids", "in", rec.company_id.id)], limit=1)
            partner = adv.employee_id.work_contact_id or adv.employee_id.user_id.partner_id
            dist = ({str(adv.project_analytic_id.id): 100}
                    if adv.project_analytic_id else False)
            lines = []
            for l in rec.line_ids:
                lines.append((0, 0, {
                    "account_id": l.account_id.id,
                    "name": l.name,
                    "debit": l.amount,
                    "analytic_distribution": dist,
                }))
            lines.append((0, 0, {
                "account_id": advance_acc.id,
                "partner_id": partner.id if partner else False,
                "name": _("Clear advance %s", adv.name),
                "credit": rec.amount_received,
            }))
            diff = rec.amount_diff
            if abs(diff) >= 0.005:
                journal = adv.journal_id
                lines.append((0, 0, {
                    "account_id": journal.default_account_id.id,
                    "name": _("Refund" ) if diff < 0 else _("Extra payment"),
                    "debit": -diff if diff < 0 else 0.0,
                    "credit": diff if diff > 0 else 0.0,
                }))
            move = self.env["account.move"].with_context(mcb_skip_approval=True).create({
                "move_type": "entry",
                "journal_id": adv.journal_id.id,
                "date": rec.date_adjustment,
                "ref": _("Advance adjustment %s / %s", rec.name, adv.name),
                "line_ids": lines,
            })
            move.action_post()
            rec.write({"settle_move_id": move.id, "state": "approved"})
            adv.state = "adjusted"


class McbAdvanceAdjustmentLine(models.Model):
    _name = "mcb.advance.adjustment.line"
    _description = "Advance Adjustment Expenditure Line"

    adjustment_id = fields.Many2one("mcb.advance.adjustment", required=True, ondelete="cascade")
    name = fields.Char(string="Particulars", required=True)
    account_id = fields.Many2one(
        "account.account", string="Accounts Code", required=True,
        domain="[('account_type', 'in', ('expense', 'expense_direct_cost'))]")
    amount = fields.Monetary(currency_field="currency_id")
    remarks = fields.Char()
    currency_id = fields.Many2one(related="adjustment_id.currency_id")
