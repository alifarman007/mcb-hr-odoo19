from odoo import fields, models


class McbTopSheetWizard(models.TransientModel):
    """Annexure-24 — Expenses Top Sheet from posted vendor bills (VOU-008, TAX-002)."""
    _name = "mcb.top.sheet.wizard"
    _inherit = ["mcb.xlsx.mixin"]
    _description = "Expenses Top Sheet (Annexure-24)"

    date_from = fields.Date(required=True)
    date_to = fields.Date(required=True, default=fields.Date.context_today)
    analytic_account_id = fields.Many2one(
        "account.analytic.account", string="Project / Donor (Analytic)",
    )
    project_name = fields.Char(string="Name of Project / Office")
    funded_by = fields.Char()

    def _get_bills(self):
        domain = [
            ("move_type", "=", "in_invoice"),
            ("state", "=", "posted"),
            ("invoice_date", ">=", self.date_from),
            ("invoice_date", "<=", self.date_to),
        ]
        bills = self.env["account.move"].search(domain, order="invoice_date")
        if self.analytic_account_id:
            key = str(self.analytic_account_id.id)
            bills = bills.filtered(
                lambda m: any(
                    key in (l.analytic_distribution or {})
                    for l in m.invoice_line_ids
                )
            )
        return bills

    def _bill_rows(self):
        rows = []
        for bill in self._get_bills():
            vat = tds = 0.0
            for line in bill.line_ids.filtered(lambda l: l.display_type == "tax"):
                if line.tax_line_id and line.tax_line_id.tax_group_id.name == "TDS":
                    tds += abs(line.balance)
                elif line.tax_line_id:
                    vat += abs(line.balance)
            net_paid = bill.amount_total
            codes = set()
            for l in bill.invoice_line_ids:
                for k in (l.analytic_distribution or {}):
                    codes.add(self.env["account.analytic.account"].browse(int(k)).name)
            rows.append({
                "date": bill.invoice_date,
                "vendor": bill.partner_id.name,
                "purpose": bill.ref or bill.payment_reference or "",
                "code": ", ".join(sorted(codes)),
                "bill_no": bill.name,
                "bill": bill.amount_untaxed,
                "vat": vat,
                "tds": tds,
                "net": net_paid,
            })
        return rows

    def action_print_pdf(self):
        return self.env.ref("mcb_account.action_report_mcb_top_sheet").report_action(self)

    def action_export_xlsx(self):
        rows = [[str(r["date"]), r["vendor"], r["purpose"], r["code"], r["bill_no"],
                 r["bill"], r["vat"], r["tds"], r["net"]] for r in self._bill_rows()]
        totals = ["", "", "", "", "Grand Total",
                  sum(r[5] for r in rows), sum(r[6] for r in rows),
                  sum(r[7] for r in rows), sum(r[8] for r in rows)] if rows else []
        return self._mcb_xlsx_download(
            f"expenses_top_sheet_{self.date_to}.xlsx", "Expenses Top Sheet",
            ["Date", "Vendor/Party", "Purpose", "Activity/Accounts Code", "Bill No",
             "Bill", "VAT", "Tax (TDS)", "Net Paid"],
            rows, footer_rows=[totals] if totals else None,
        )
