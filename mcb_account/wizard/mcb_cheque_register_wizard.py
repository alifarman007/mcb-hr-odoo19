from odoo import fields, models


class McbChequeRegisterWizard(models.TransientModel):
    """Annexure-02 — Cheque Issue Register from bank payments (BNK-003)."""
    _name = "mcb.cheque.register.wizard"
    _inherit = ["mcb.xlsx.mixin"]
    _description = "Cheque Issue Register (Annexure-02)"

    journal_id = fields.Many2one(
        "account.journal", required=True, domain="[('type', '=', 'bank')]",
    )
    date_from = fields.Date(required=True)
    date_to = fields.Date(required=True, default=fields.Date.context_today)
    project_name = fields.Char(string="Name of Project / Office")
    funded_by = fields.Char()

    def _payments(self):
        return self.env["account.payment"].search([
            ("journal_id", "=", self.journal_id.id),
            ("payment_type", "=", "outbound"),
            ("date", ">=", self.date_from),
            ("date", "<=", self.date_to),
            ("state", "in", ("in_process", "paid", "posted")),
        ], order="date")

    def action_print_pdf(self):
        return self.env.ref("mcb_account.action_report_mcb_cheque_register").report_action(self)

    def action_export_xlsx(self):
        rows = []
        for i, p in enumerate(self._payments(), 1):
            rows.append([i, str(p.date), p.check_number or "", p.partner_id.name or "",
                         p.memo or "", p.amount, p.mcb_amount_in_words or ""])
        return self._mcb_xlsx_download(
            f"cheque_register_{self.journal_id.code}.xlsx", "Cheque Issue Register",
            ["Sl", "Date", "Cheque No", "Name of Party", "Purpose", "Amount BDT",
             "Amount in Words"],
            rows,
        )
