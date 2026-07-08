from odoo import api, fields, models


class AccountPayment(models.Model):
    _inherit = "account.payment"

    mcb_receipt_no = fields.Char(string="Money Receipt No", copy=False, readonly=True)
    mcb_amount_in_words = fields.Char(compute="_compute_mcb_amount_in_words")

    @api.depends("amount", "currency_id")
    def _compute_mcb_amount_in_words(self):
        for pay in self:
            try:
                pay.mcb_amount_in_words = pay.currency_id.amount_to_text(pay.amount)
            except Exception:
                pay.mcb_amount_in_words = False

    def action_post(self):
        res = super().action_post()
        seq = self.env["ir.sequence"]
        for pay in self:
            # DFR-007 — auto money-receipt number on inbound collections
            if pay.payment_type == "inbound" and not pay.mcb_receipt_no:
                pay.mcb_receipt_no = seq.next_by_code("mcb.money.receipt") or "/"
        return res
