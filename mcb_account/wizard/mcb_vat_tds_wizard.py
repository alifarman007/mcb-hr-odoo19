from odoo import fields, models


class McbVatTdsWizard(models.TransientModel):
    """TAX-004 (amended) — Monthly VAT/TDS summary: Deductible, Deducted, Deposited
    (Treasury/Mushak challan no, date, bank & branch) and Dues — by vendor & project."""
    _name = "mcb.vat.tds.wizard"
    _inherit = ["mcb.xlsx.mixin"]
    _description = "Monthly VAT/TDS Summary"

    date_from = fields.Date(required=True)
    date_to = fields.Date(required=True, default=fields.Date.context_today)

    def _tax_lines(self):
        return self.env["account.move.line"].search([
            ("display_type", "=", "tax"),
            ("parent_state", "=", "posted"),
            ("date", ">=", self.date_from),
            ("date", "<=", self.date_to),
            ("tax_line_id", "!=", False),
        ])

    def _summary(self):
        vat_rows, tds_rows = {}, {}
        for line in self._tax_lines():
            is_tds = line.tax_line_id.tax_group_id.name == "TDS"
            bucket = tds_rows if is_tds else vat_rows
            vendor = line.move_id.partner_id.name or "(no vendor)"
            projects = ", ".join(
                self.env["account.analytic.account"].browse(int(k)).name
                for k in (line.analytic_distribution or {})
            ) or "-"
            key = (vendor, projects)
            bucket.setdefault(key, 0.0)
            bucket[key] += abs(line.balance)
        challans = self.env["mcb.tax.challan"].search([
            ("date", ">=", self.date_from), ("date", "<=", self.date_to),
            ("state", "=", "deposited"),
        ])
        vat_deposited = sum(c.amount for c in challans if c.challan_type == "mushak_vat")
        tds_deposited = sum(c.amount for c in challans if c.challan_type == "treasury_tds")
        return {
            "vat_rows": vat_rows, "tds_rows": tds_rows,
            "vat_total": sum(vat_rows.values()), "tds_total": sum(tds_rows.values()),
            "vat_deposited": vat_deposited, "tds_deposited": tds_deposited,
            "vat_dues": sum(vat_rows.values()) - vat_deposited,
            "tds_dues": sum(tds_rows.values()) - tds_deposited,
            "challans": challans,
        }

    def action_print_pdf(self):
        return self.env.ref("mcb_account.action_report_mcb_vat_tds").report_action(self)

    def action_export_xlsx(self):
        s = self._summary()
        rows = []
        for (vendor, project), amt in sorted(s["vat_rows"].items()):
            rows.append(["VAT", vendor, project, amt])
        for (vendor, project), amt in sorted(s["tds_rows"].items()):
            rows.append(["TDS", vendor, project, amt])
        footer = [
            ["", "VAT: Deducted / Deposited / Dues",
             f"{s['vat_total']:.2f} / {s['vat_deposited']:.2f}", s["vat_dues"]],
            ["", "TDS: Deducted / Deposited / Dues",
             f"{s['tds_total']:.2f} / {s['tds_deposited']:.2f}", s["tds_dues"]],
        ]
        return self._mcb_xlsx_download(
            f"vat_tds_summary_{self.date_to}.xlsx", "VAT-TDS Summary",
            ["Type", "Vendor", "Project", "Amount Deducted"],
            rows, footer_rows=footer,
        )
