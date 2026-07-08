from dateutil.relativedelta import relativedelta

from odoo import api, fields, models

PERIODS = {
    "monthly": 1,
    "bimonthly": 2,
    "quarterly": 3,
    "half_yearly": 6,
    "annual": 12,
}


class McbDonorReportWizard(models.TransientModel):
    """BUD-003/006 + DFR-002/003 (client feedback) — Budget-vs-Actual donor report,
    period granularity monthly / bimonthly / quarterly / half-yearly / annual,
    with cumulative actuals, variance % and optional donor-currency display."""
    _name = "mcb.donor.report.wizard"
    _inherit = ["mcb.xlsx.mixin", "mcb.fy.mixin"]
    _description = "Donor Budget vs Actual Report (Annex-11 / DFR-002)"

    budget_id = fields.Many2one("budget.analytic", required=True, string="Project Budget")
    granularity = fields.Selection([
        ("monthly", "Monthly"),
        ("bimonthly", "Bimonthly"),
        ("quarterly", "Quarterly"),
        ("half_yearly", "Half-Yearly"),
        ("annual", "Annual"),
    ], default="quarterly", required=True)
    display_currency_id = fields.Many2one(
        "res.currency", string="Display Currency",
        help="DFR-003 — optional donor currency; converted at the given rate.")
    manual_rate = fields.Float(
        string="BDT per 1 unit", default=1.0,
        help="Exchange rate applied when a display currency is chosen.")

    def _line_analytic(self, bl):
        for fname, field in bl._fields.items():
            if field.type == "many2one" and field.comodel_name == "account.analytic.account":
                if bl[fname]:
                    return bl[fname]
        return self.env["account.analytic.account"]

    def _periods(self):
        step = PERIODS[self.granularity]
        start, end = self.budget_id.date_from, self.budget_id.date_to
        periods, cur = [], start
        while cur <= end:
            nxt = cur + relativedelta(months=step)
            periods.append((cur, min(nxt - relativedelta(days=1), end)))
            cur = nxt
        return periods

    def _matrix(self):
        """rows: budget lines; cols: periods -> {'budget','actual'}; plus cumulative."""
        rate = self.manual_rate if (self.display_currency_id and self.manual_rate) else 1.0

        def conv(v):
            return v / rate if rate else v

        periods = self._periods()
        n = max(len(periods), 1)
        rows = []
        for bl in self.budget_id.budget_line_ids:
            analytic = self._line_analytic(bl)
            per_cells, cumulative = [], 0.0
            for (p_from, p_to) in periods:
                actual = 0.0
                if analytic:
                    grouped = self.env["account.analytic.line"]._read_group(
                        [("account_id", "=", analytic.id),
                         ("date", ">=", p_from), ("date", "<=", p_to),
                         ("amount", "<", 0)],
                        [], ["amount:sum"])
                    actual = -(grouped[0][0] or 0.0)
                cumulative += actual
                per_cells.append({
                    "budget": conv(bl.budget_amount / n),
                    "actual": conv(actual),
                    "cum": conv(cumulative),
                })
            variance = bl.budget_amount - cumulative
            rows.append({
                "line": bl,
                "analytic": analytic,
                "cells": per_cells,
                "approved": conv(bl.budget_amount),
                "cumulative": conv(cumulative),
                "variance": conv(variance),
                "variance_pct": (variance / bl.budget_amount * 100.0)
                                 if bl.budget_amount else 0.0,
            })
        return periods, rows

    def action_print_pdf(self):
        return self.env.ref("mcb_budget.action_report_mcb_donor_budget").report_action(self)

    def action_print_variance(self):
        return self.env.ref("mcb_budget.action_report_mcb_variance").report_action(self)

    def action_export_xlsx(self):
        periods, rows = self._matrix()
        headers = ["Activity Code", "Head / Activity", "Analytic", "Approved Budget"]
        for (pf, pt) in periods:
            headers += [f"{pf:%b%y} Actual"]
        headers += ["Cumulative Actual", "Variance", "Variance %"]
        data = []
        for r in rows:
            row = [r["line"].mcb_activity_code or "",
                   r["line"].mcb_activity_name or r["line"].name or "",
                   r["analytic"].name or "", r["approved"]]
            row += [c["actual"] for c in r["cells"]]
            row += [r["cumulative"], r["variance"], round(r["variance_pct"], 1)]
            data.append(row)
        return self._mcb_xlsx_download(
            f"donor_budget_report_{self.budget_id.name}.xlsx",
            "Budget vs Actual", headers, data)
