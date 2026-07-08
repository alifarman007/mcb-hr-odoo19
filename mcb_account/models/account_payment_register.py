from odoo import models, _
from odoo.exceptions import UserError


class AccountPaymentRegister(models.TransientModel):
    _inherit = "account.payment.register"

    def _create_payments(self):
        """PO-007 hard gate (plan-review finding 5) — account_3way_match only computes
        an advisory release_to_pay flag; MCB requires payment blocked until the GRN is
        certified. Finance Managers may override."""
        blocked = self.env["account.move"]
        for wizard in self:
            moves = wizard.line_ids.mapped("move_id")
            for move in moves:
                if (
                    move.move_type == "in_invoice"
                    and "release_to_pay" in move._fields
                    and move.release_to_pay == "no"
                ):
                    blocked |= move
        if blocked and not self.env.user.has_group("mcb_account.group_mcb_finance_manager"):
            raise UserError(_(
                "PO-007 — payment is blocked until the goods receipt (GRN) is certified "
                "for: %s. A Finance Manager may override.",
                ", ".join(blocked.mapped("name")),
            ))
        return super()._create_payments()
