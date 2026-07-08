from odoo import fields, models


class McbPettyBookWizard(models.TransientModel):
    """Annexure-15 (Petty Cash Book, running balance) and Annexure-16 (Petty Cash
    Statement grouped by accounts head) over a cash journal (PCH-001/003)."""
    _name = "mcb.petty.book.wizard"
    _inherit = ["mcb.xlsx.mixin"]
    _description = "Petty Cash Book / Statement (Annexure-15/16)"

    journal_id = fields.Many2one(
        "account.journal", required=True, domain="[('type', '=', 'cash')]")
    date_from = fields.Date(required=True)
    date_to = fields.Date(required=True, default=fields.Date.context_today)
    project_name = fields.Char(string="Name of Project / Office")
    funded_by = fields.Char()

    def _entries(self):
        """Cash account move lines with running balance."""
        account = self.journal_id.default_account_id
        opening_grp = self.env["account.move.line"]._read_group(
            [("account_id", "=", account.id), ("date", "<", self.date_from),
             ("parent_state", "=", "posted")], [], ["balance:sum"])
        opening = opening_grp[0][0] or 0.0
        lines = self.env["account.move.line"].search(
            [("account_id", "=", account.id),
             ("date", ">=", self.date_from), ("date", "<=", self.date_to),
             ("parent_state", "=", "posted")], order="date, id")
        rows, run = [], opening
        for l in lines:
            run += l.balance
            counterparts = l.move_id.line_ids - l
            code = ", ".join(sorted(set(counterparts.mapped("account_id.code"))))
            rows.append({
                "date": l.date,
                "ref": l.move_id.mcb_voucher_no or l.move_id.name,
                "particulars": l.name or l.move_id.ref or "",
                "code": code,
                "received": l.debit,
                "paid": l.credit,
                "balance": run,
                "counter_accounts": counterparts.mapped("account_id"),
                "amount": l.credit or l.debit,
            })
        return opening, rows

    def _statement_columns(self):
        """Annexure-16 — expenditures analysed per accounts head."""
        opening, rows = self._entries()
        heads = {}
        for r in rows:
            if r["paid"]:
                for acc in r["counter_accounts"]:
                    if acc.account_type in ("expense", "expense_direct_cost",
                                            "expense_depreciation"):
                        heads.setdefault(f"{acc.code} {acc.name}", 0.0)
                        heads[f"{acc.code} {acc.name}"] += r["paid"] / max(
                            len(r["counter_accounts"]), 1)
        return heads

    def action_print_book(self):
        return self.env.ref("mcb_cash_advance.action_report_mcb_petty_book").report_action(self)

    def action_print_statement(self):
        return self.env.ref(
            "mcb_cash_advance.action_report_mcb_petty_statement").report_action(self)

    def action_export_xlsx(self):
        opening, rows = self._entries()
        data = [[str(r["date"]), r["ref"], r["particulars"], r["code"],
                 r["received"], r["paid"], r["balance"]] for r in rows]
        return self._mcb_xlsx_download(
            f"petty_cash_book_{self.journal_id.code}.xlsx", "Petty Cash Book",
            ["Date", "Bill/Voucher #", "Particulars", "Accounts Code",
             "Received", "Payment", "Balance"],
            data, footer_rows=[["", "", "Opening", "", opening, "", ""]],
        )
