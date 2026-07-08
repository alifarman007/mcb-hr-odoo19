from odoo import api, fields, models, _
from odoo.exceptions import UserError

DENOMINATIONS = [1000, 500, 200, 100, 50, 20, 10, 5, 2, 1]


class McbCashCount(models.Model):
    """Annexure-14 — Daily Cash Balance Report / denomination cash count (PCH-002)."""
    _name = "mcb.cash.count"
    _description = "MCB Daily Cash Count (Annexure-14)"
    _inherit = ["mail.thread", "mcb.fy.mixin"]
    _order = "date desc"

    name = fields.Char(default="New", copy=False, readonly=True)
    journal_id = fields.Many2one(
        "account.journal", required=True, domain="[('type', '=', 'cash')]",
        string="Cash Journal")
    date = fields.Date(default=fields.Date.context_today, required=True)
    project_name = fields.Char(string="Name of Project / Office")
    funded_by = fields.Char()
    line_ids = fields.One2many("mcb.cash.count.line", "count_id")
    total_counted = fields.Monetary(compute="_compute_totals", store=True,
                                    currency_field="currency_id")
    book_balance = fields.Monetary(compute="_compute_totals", store=True,
                                   currency_field="currency_id",
                                   help="Cash journal GL balance on the count date.")
    difference = fields.Monetary(compute="_compute_totals", store=True,
                                 currency_field="currency_id")
    amount_in_words = fields.Char(compute="_compute_words")
    currency_id = fields.Many2one("res.currency", default=lambda s: s.env.company.currency_id)
    company_id = fields.Many2one("res.company", default=lambda s: s.env.company)
    state = fields.Selection([("draft", "Draft"), ("approved", "Approved")],
                             default="draft", tracking=True)

    @api.depends("line_ids.subtotal", "journal_id", "date")
    def _compute_totals(self):
        for rec in self:
            rec.total_counted = sum(rec.line_ids.mapped("subtotal"))
            balance = 0.0
            if rec.journal_id and rec.date:
                grouped = self.env["account.move.line"]._read_group(
                    [("account_id", "=", rec.journal_id.default_account_id.id),
                     ("date", "<=", rec.date), ("parent_state", "=", "posted")],
                    [], ["balance:sum"])
                balance = grouped[0][0] or 0.0
            rec.book_balance = balance
            rec.difference = rec.total_counted - balance

    @api.depends("total_counted")
    def _compute_words(self):
        for rec in self:
            rec.amount_in_words = (rec.currency_id.amount_to_text(rec.total_counted)
                                   if rec.total_counted else "")

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for rec in records:
            if rec.name == "New":
                rec.name = rec._mcb_fy_sequence_next("mcb.cash.count", "CC")
            if not rec.line_ids:
                rec.line_ids = [(0, 0, {"denomination": d}) for d in DENOMINATIONS]
        return records

    def action_approve(self):
        self.write({"state": "approved"})

    # PCH-005 — low-balance alert cron
    @api.model
    def _cron_petty_low_balance(self):
        for journal in self.env["account.journal"].search(
                [("type", "=", "cash"), ("mcb_petty_cash_limit", ">", 0)]):
            grouped = self.env["account.move.line"]._read_group(
                [("account_id", "=", journal.default_account_id.id),
                 ("parent_state", "=", "posted")], [], ["balance:sum"])
            balance = grouped[0][0] or 0.0
            if balance < journal.mcb_petty_cash_limit * 0.2:
                for user in self.env.ref("account.group_account_manager").users[:3]:
                    self.env["mail.activity"].create({
                        "res_model_id": self.env["ir.model"]._get_id("account.journal"),
                        "res_id": journal.id,
                        "activity_type_id": self.env.ref("mail.mail_activity_data_todo").id,
                        "user_id": user.id,
                        "summary": _("Petty cash below 20%% of limit (%s)", journal.name),
                        "note": _("Balance %.2f — limit %.2f. Raise a top-up (PCH-004/005).",
                                  balance, journal.mcb_petty_cash_limit),
                    })


class McbCashCountLine(models.Model):
    _name = "mcb.cash.count.line"
    _description = "Cash Count Denomination Line"
    _order = "denomination desc"

    count_id = fields.Many2one("mcb.cash.count", required=True, ondelete="cascade")
    denomination = fields.Integer(required=True)
    quantity = fields.Integer(default=0)
    subtotal = fields.Monetary(compute="_compute_subtotal", store=True,
                               currency_field="currency_id")
    currency_id = fields.Many2one(related="count_id.currency_id")

    @api.depends("denomination", "quantity")
    def _compute_subtotal(self):
        for l in self:
            l.subtotal = l.denomination * l.quantity


class McbPettyTopup(models.Model):
    """PCH-004 — petty cash top-up: request → approval → internal transfer JE."""
    _name = "mcb.petty.topup"
    _description = "MCB Petty Cash Top-Up"
    _inherit = ["mail.thread", "mcb.fy.mixin"]

    name = fields.Char(default="New", copy=False, readonly=True)
    cash_journal_id = fields.Many2one(
        "account.journal", required=True, domain="[('type', '=', 'cash')]")
    bank_journal_id = fields.Many2one(
        "account.journal", required=True, domain="[('type', '=', 'bank')]")
    amount = fields.Monetary(required=True, currency_field="currency_id")
    currency_id = fields.Many2one("res.currency", default=lambda s: s.env.company.currency_id)
    company_id = fields.Many2one("res.company", default=lambda s: s.env.company)
    move_id = fields.Many2one("account.move", readonly=True, copy=False)
    state = fields.Selection([
        ("draft", "Draft"), ("requested", "Requested"),
        ("approved", "Approved"), ("done", "Replenished"),
    ], default="draft", tracking=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self._mcb_fy_sequence_next("mcb.petty.topup", "PTU")
        return super().create(vals_list)

    def action_request(self):
        self.write({"state": "requested"})

    def action_approve(self):
        self.write({"state": "approved"})

    def action_done(self):
        for rec in self:
            if rec.amount <= 0:
                raise UserError(_("Amount must be positive."))
            move = self.env["account.move"].with_context(mcb_skip_approval=True).create({
                "move_type": "entry",
                "journal_id": rec.bank_journal_id.id,
                "date": fields.Date.context_today(self),
                "ref": _("Petty cash top-up %s", rec.name),
                "line_ids": [
                    (0, 0, {"account_id": rec.cash_journal_id.default_account_id.id,
                            "name": rec.name, "debit": rec.amount}),
                    (0, 0, {"account_id": rec.bank_journal_id.default_account_id.id,
                            "name": rec.name, "credit": rec.amount}),
                ],
            })
            move.action_post()
            rec.write({"move_id": move.id, "state": "done"})
