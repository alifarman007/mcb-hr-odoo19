from odoo import fields, models


class McbPrReportWizard(models.TransientModel):
    """Table-14 — PR Report + PR Process Report (days elapsed per stage)."""
    _name = "mcb.pr.report.wizard"
    _inherit = ["mcb.xlsx.mixin"]
    _description = "PR / PR-Process Report"

    date_from = fields.Date(required=True)
    date_to = fields.Date(required=True, default=fields.Date.context_today)
    project_analytic_id = fields.Many2one("account.analytic.account",
                                          string="Project (optional)")

    def _prs(self):
        domain = [("date_request", ">=", self.date_from),
                  ("date_request", "<=", self.date_to)]
        if self.project_analytic_id:
            domain.append(("project_analytic_id", "=", self.project_analytic_id.id))
        return self.env["mcb.purchase.request"].search(domain, order="date_request")

    @staticmethod
    def _days(d1, d2):
        if d1 and d2:
            return (d2.date() if hasattr(d2, "date") else d2) - \
                   (d1.date() if hasattr(d1, "date") else d1)
        return None

    def _rows(self):
        rows = []
        for pr in self._prs():
            po = pr.order_ids.filtered(lambda o: o.state in ("purchase", "done"))[:1]
            rows.append({
                "pr": pr,
                "po": po,
                "d_confirm": self._days(pr.create_date, pr.date_confirmed),
                "d_approve": self._days(pr.date_confirmed, pr.date_approved),
                "d_pc": self._days(pr.date_approved, pr.date_sent_pc),
                "d_po": self._days(pr.date_sent_pc, pr.date_po_issued),
            })
        return rows

    def action_print_pr_report(self):
        return self.env.ref("mcb_purchase.action_report_mcb_pr_report").report_action(self)

    def action_export_xlsx(self):
        rows = []
        for r in self._rows():
            pr, po = r["pr"], r["po"]
            rows.append([
                pr.name, str(pr.date_request),
                po.mcb_order_ref or po.name or "", str(po.date_approve or "") if po else "",
                ", ".join(pr.line_ids.mapped("name"))[:60],
                po.amount_total if po else 0.0,
                po.partner_id.name if po else "",
                pr.project_analytic_id.name or "",
                dict(pr._fields["procurement_method"].selection).get(pr.procurement_method, ""),
                str(r["d_po"].days) if r["d_po"] else "",
                dict(pr._fields["state"].selection).get(pr.state, ""),
            ])
        return self._mcb_xlsx_download(
            f"pr_report_{self.date_to}.xlsx", "PR Report",
            ["PR#", "PR Entry Date", "PO/WO#", "PO Date", "Items/Service Head",
             "WO Value (BDT)", "Selected Vendor", "Project", "Method",
             "Days to PO", "Status"],
            rows)
