from odoo import fields, models


class AccountJournal(models.Model):
    _inherit = "account.journal"

    mcb_require_approval = fields.Boolean(
        string="MCB 4-Level Voucher Approval",
        help="VOU-002 — entries in this journal cannot be posted until Checked, "
             "Reviewed and Approved (Prepared = creator).",
    )
    mcb_petty_cash_limit = fields.Monetary(
        string="Petty Cash Limit",
        currency_field="currency_id",
        help="PCH-005 — configured float for this cash journal; alert below 20%.",
    )
