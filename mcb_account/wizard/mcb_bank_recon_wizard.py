from odoo import api, fields, models


class McbBankReconWizard(models.TransientModel):
    """Annexure-17 — Bank Reconciliation Statement (BNK-002/004/005 + XLSX feedback).

    A = balance per bank statement (input / last statement)
    B = outstanding credits (inbound not yet on statement)
    C = A + B ; D = outstanding cheques (outbound not yet on statement)
    E = C - D ; G = balance per cash book (bank GL) ; F = E - G
    """
    _name = "mcb.bank.recon.wizard"
    _inherit = ["mcb.xlsx.mixin"]
    _description = "Bank Reconciliation Statement (Annexure-17)"

    journal_id = fields.Many2one(
        "account.journal", required=True, domain="[('type', '=', 'bank')]",
        string="Bank Journal",
    )
    date_to = fields.Date(string="Reporting Date", required=True,
                          default=fields.Date.context_today)
    statement_balance = fields.Monetary(
        string="Balance as per Bank Statement", currency_field="currency_id",
        help="Enter from the bank statement; defaults to the last imported statement balance.",
    )
    currency_id = fields.Many2one("res.currency", default=lambda s: s.env.company.currency_id)

    @api.onchange("journal_id", "date_to")
    def _onchange_statement_default(self):
        for wiz in self:
            if not wiz.journal_id:
                continue
            st = self.env["account.bank.statement"].search([
                ("journal_id", "=", wiz.journal_id.id),
                ("date", "<=", wiz.date_to or fields.Date.context_today(self)),
            ], order="date desc", limit=1)
            wiz.statement_balance = st.balance_end_real if st else 0.0

    def _gather(self):
        self.ensure_one()
        journal = self.journal_id
        outstanding_accounts = (
            journal.company_id.account_journal_payment_debit_account_id
            | journal.company_id.account_journal_payment_credit_account_id
        )
        lines = self.env["account.move.line"].search([
            ("journal_id", "=", journal.id),
            ("account_id", "in", outstanding_accounts.ids),
            ("date", "<=", self.date_to),
            ("parent_state", "=", "posted"),
            ("full_reconcile_id", "=", False),
        ])
        out_credits = lines.filtered(lambda l: l.debit > 0)   # money in, not on statement
        out_cheques = lines.filtered(lambda l: l.credit > 0)  # cheques issued, not cleared
        default_account = journal.default_account_id
        book_lines = self.env["account.move.line"]._read_group(
            [("account_id", "=", default_account.id),
             ("date", "<=", self.date_to),
             ("parent_state", "=", "posted")],
            [], ["balance:sum"],
        )
        book_balance = book_lines[0][0] if book_lines else 0.0
        return out_credits, out_cheques, book_balance

    def _report_values(self):
        out_credits, out_cheques, book_balance = self._gather()
        a = self.statement_balance
        b = sum(out_credits.mapped("debit"))
        c = a + b
        d = sum(out_cheques.mapped("credit"))
        e = c - d
        g = book_balance
        f = e - g
        return {
            "wizard": self,
            "out_credits": out_credits,
            "out_cheques": out_cheques,
            "A": a, "B": b, "C": c, "D": d, "E": e, "F": f, "G": g,
        }

    def action_print_pdf(self):
        return self.env.ref("mcb_account.action_report_mcb_bank_recon").report_action(self)

    def action_export_xlsx(self):
        vals = self._report_values()
        rows = [["A", "Balance as per Bank Statement", "", vals["A"]]]
        rows.append(["B", "Add: Outstanding Credits", "", vals["B"]])
        for l in vals["out_credits"]:
            rows.append(["", str(l.date), l.partner_id.name or l.name or "", l.debit])
        rows.append(["C", "Total (A+B)", "", vals["C"]])
        rows.append(["D", "Less: Outstanding Cheques", "", vals["D"]])
        for l in vals["out_cheques"]:
            rows.append(["", f"{l.date} {l.payment_id.check_number or ''}",
                         l.partner_id.name or l.name or "", l.credit])
        rows.append(["E", "Balance (C-D)", "", vals["E"]])
        rows.append(["G", "Balance as per Cash Book", "", vals["G"]])
        rows.append(["F", "Difference (E-G)", "", vals["F"]])
        return self._mcb_xlsx_download(
            f"bank_reconciliation_{self.journal_id.code}_{self.date_to}.xlsx",
            "Bank Reconciliation",
            ["Sl", "Particulars", "Party", "Amount"],
            rows,
        )
