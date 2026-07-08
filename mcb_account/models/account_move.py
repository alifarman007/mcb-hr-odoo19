from odoo import api, fields, models, _
from odoo.exceptions import UserError

VOUCHER_PREFIX = {
    ("receipt", "cash"): "CRV",
    ("receipt", "bank"): "BRV",
    ("payment", "cash"): "CPV",
    ("payment", "bank"): "BPV",
    ("contra", "any"): "CTV",
    ("journal", "any"): "JV",
}

VOUCHER_TITLE = {
    "receipt": "Bank/Cash Receipt Voucher",   # Annexure-03 (Credit Voucher)
    "payment": "Bank/Cash Payment Voucher",   # Annexure-04 (Debit Voucher)
    "contra": "Contra / Transfer Voucher",    # Annexure-05
    "journal": "Journal Voucher",             # Annexure-06
}


class AccountMove(models.Model):
    _name = "account.move"
    _inherit = ["account.move", "mcb.fy.mixin", "mcb.xlsx.mixin"]

    # ---- VOU-001 voucher number per journal per FY ----
    mcb_voucher_no = fields.Char(string="MCB Voucher No", copy=False, readonly=True, index=True)
    mcb_voucher_type = fields.Selection([
        ("receipt", "Receipt (Credit) Voucher"),
        ("payment", "Payment (Debit) Voucher"),
        ("contra", "Contra / Transfer Voucher"),
        ("journal", "Journal Voucher"),
    ], compute="_compute_mcb_voucher_type", store=True, string="Voucher Type")

    # ---- VOU-002 four-level approval ----
    mcb_checked_by_id = fields.Many2one("res.users", string="Checked By", copy=False, tracking=True)
    mcb_checked_on = fields.Datetime(copy=False)
    mcb_reviewed_by_id = fields.Many2one("res.users", string="Reviewed By", copy=False, tracking=True)
    mcb_reviewed_on = fields.Datetime(copy=False)
    mcb_approved_by_id = fields.Many2one("res.users", string="Approved By", copy=False, tracking=True)
    mcb_approved_on = fields.Datetime(copy=False)
    mcb_approval_required = fields.Boolean(related="journal_id.mcb_require_approval")

    # ---- VOU-004 amount in words ----
    mcb_amount_in_words = fields.Char(compute="_compute_mcb_amount_in_words", string="Amount in Words")

    @api.depends("line_ids.account_id.account_type", "journal_id", "move_type")
    def _compute_mcb_voucher_type(self):
        for move in self:
            liq_lines = move.line_ids.filtered(
                lambda l: l.account_id.account_type == "asset_cash"
            )
            non_liq = move.line_ids.filtered(
                lambda l: l.account_id.account_type != "asset_cash"
                and l.display_type not in ("line_section", "line_note")
            )
            if liq_lines and not non_liq:
                move.mcb_voucher_type = "contra"
            elif liq_lines and sum(liq_lines.mapped("debit")) > sum(liq_lines.mapped("credit")):
                move.mcb_voucher_type = "receipt"
            elif liq_lines:
                move.mcb_voucher_type = "payment"
            else:
                move.mcb_voucher_type = "journal"

    @api.depends("amount_total", "currency_id")
    def _compute_mcb_amount_in_words(self):
        for move in self:
            try:
                move.mcb_amount_in_words = move.currency_id.amount_to_text(move.amount_total)
            except Exception:
                move.mcb_amount_in_words = False

    # ---- approval buttons ----
    def action_mcb_check(self):
        self.write({"mcb_checked_by_id": self.env.user.id, "mcb_checked_on": fields.Datetime.now()})

    def action_mcb_review(self):
        for move in self:
            if not move.mcb_checked_by_id:
                raise UserError(_("Voucher must be Checked before Review (VOU-002)."))
        self.write({"mcb_reviewed_by_id": self.env.user.id, "mcb_reviewed_on": fields.Datetime.now()})

    def action_mcb_approve(self):
        for move in self:
            if not move.mcb_reviewed_by_id:
                raise UserError(_("Voucher must be Reviewed before Approval (VOU-002)."))
        self.write({"mcb_approved_by_id": self.env.user.id, "mcb_approved_on": fields.Datetime.now()})

    def _mcb_approval_gate_applies(self):
        """VOU-002 gate — manual journal entries only; system-generated moves
        (payments, statement lines, depreciation, payroll, expenses) bypass it
        so native automated flows keep working (plan-review finding 17)."""
        self.ensure_one()
        if self.env.context.get("mcb_skip_approval"):
            return False
        if not self.journal_id.mcb_require_approval:
            return False
        if self.origin_payment_id or self.statement_line_id:
            return False
        if self.move_type != "entry":
            return False
        for auto_field in ("asset_id", "payslip_run_id", "expense_sheet_id"):
            if auto_field in self._fields and self[auto_field]:
                return False
        return True

    def _post(self, soft=True):
        for move in self:
            if move._mcb_approval_gate_applies() and not move.mcb_approved_by_id:
                raise UserError(_(
                    "Journal '%s' enforces the MCB 4-level voucher workflow: the entry must be "
                    "Checked, Reviewed and Approved before posting (VOU-002).",
                    move.journal_id.name,
                ))
        posted = super()._post(soft=soft)
        for move in posted:
            if not move.mcb_voucher_no and move.journal_id.type in ("bank", "cash", "general"):
                jtype = move.journal_id.type if move.journal_id.type in ("bank", "cash") else "any"
                key = (move.mcb_voucher_type, jtype if move.mcb_voucher_type in ("receipt", "payment") else "any")
                prefix = VOUCHER_PREFIX.get(key, "JV")
                move.mcb_voucher_no = move._mcb_fy_sequence_next(
                    f"mcb.vch.{prefix}.{move.company_id.id}", prefix, move.date
                )
        return posted

    def mcb_voucher_title(self):
        self.ensure_one()
        return VOUCHER_TITLE.get(self.mcb_voucher_type, "Journal Voucher")

    # ---- client feedback VOU-006: XLSX export of vouchers ----
    def action_mcb_export_voucher_xlsx(self):
        rows = []
        for move in self:
            for line in move.line_ids.filtered(lambda l: l.display_type == "product" or not l.display_type):
                rows.append([
                    move.mcb_voucher_no or move.name,
                    str(move.date),
                    move.mcb_voucher_title(),
                    f"{line.account_id.code} {line.account_id.name}",
                    line.name or "",
                    line.partner_id.name or "",
                    ", ".join(
                        self.env["account.analytic.account"].browse(int(k)).name
                        for k in (line.analytic_distribution or {})
                    ),
                    line.debit,
                    line.credit,
                ])
        return self[:1]._mcb_xlsx_download(
            "mcb_vouchers.xlsx", "Vouchers",
            ["Voucher No", "Date", "Type", "Account", "Memo", "Party", "Analytic (Class)",
             "Debit", "Credit"],
            rows,
        )
