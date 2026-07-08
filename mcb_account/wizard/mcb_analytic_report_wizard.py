from odoo import fields, models


class McbAnalyticReportWizard(models.TransientModel):
    """DFR-001 — income / expenditure / balance by project+donor analytic account."""
    _name = "mcb.analytic.report.wizard"
    _inherit = ["mcb.xlsx.mixin"]
    _description = "Donor/Project Financial Report (DFR-001)"

    analytic_account_ids = fields.Many2many(
        "account.analytic.account", string="Projects / Donors",
        help="Empty = all analytic accounts.",
    )
    date_from = fields.Date(required=True)
    date_to = fields.Date(required=True, default=fields.Date.context_today)

    def _rows(self):
        domain = [("date", ">=", self.date_from), ("date", "<=", self.date_to)]
        if self.analytic_account_ids:
            domain.append(("account_id", "in", self.analytic_account_ids.ids))
        lines = self.env["account.analytic.line"].search(domain)
        data = {}
        for l in lines:
            rec = data.setdefault(l.account_id, {"income": 0.0, "expense": 0.0})
            if l.amount >= 0:
                rec["income"] += l.amount
            else:
                rec["expense"] += -l.amount
        return data

    def action_print_pdf(self):
        return self.env.ref("mcb_account.action_report_mcb_analytic").report_action(self)

    def action_export_xlsx(self):
        rows = [[acc.name, v["income"], v["expense"], v["income"] - v["expense"]]
                for acc, v in sorted(self._rows().items(), key=lambda kv: kv[0].name or "")]
        return self._mcb_xlsx_download(
            f"donor_financial_report_{self.date_to}.xlsx", "Donor Financial Report",
            ["Project / Donor (Analytic)", "Income", "Expenditure", "Balance"],
            rows,
        )
