from odoo import fields, models


class McbAssetRegisterWizard(models.TransientModel):
    """Annexure-07 — Fixed Assets Register for a reporting period (AST-001)."""
    _name = "mcb.asset.register.wizard"
    _inherit = ["mcb.xlsx.mixin"]
    _description = "Fixed Assets Register (Annexure-07)"

    date_from = fields.Date(required=True)
    date_to = fields.Date(required=True, default=fields.Date.context_today)
    project_analytic_id = fields.Many2one("account.analytic.account",
                                          string="Project / Donor (optional)")
    project_name = fields.Char(string="Name of Project / Office")
    funded_by = fields.Char()

    def _assets(self):
        domain = [("state", "in", ("open", "close")),
                  ("company_id", "=", self.env.company.id)]
        if self.project_analytic_id:
            domain.append(("mcb_project_analytic_id", "=", self.project_analytic_id.id))
        return self.env["account.asset"].search(domain, order="acquisition_date")

    def _rows(self):
        rows = []
        for a in self._assets():
            fig = a._mcb_depreciation_figures(self.date_from, self.date_to)
            rows.append({
                "asset": a, "code": a.mcb_asset_code or "",
                "date": a.acquisition_date, "cost": a.original_value,
                "rate": (a.method_number and a.method_period and
                         round(100.0 / max(a.method_number, 1), 1)) or 0.0,
                **fig,
                "location": a.mcb_location or "", "condition": a.mcb_condition or "",
                "user": a.mcb_custodian_id.name or "",
            })
        return rows

    def action_print_pdf(self):
        return self.env.ref("mcb_asset.action_report_mcb_asset_register").report_action(self)

    def action_export_xlsx(self):
        rows = [[r["code"], r["asset"].name, str(r["date"] or ""), r["cost"],
                 f"{r['rate']}%", r["opening"], r["charge"], r["adjustment"],
                 r["closing"], r["wdv"], r["location"], r["condition"], r["user"]]
                for r in self._rows()]
        return self._mcb_xlsx_download(
            f"fixed_assets_register_{self.date_to}.xlsx", "Fixed Assets Register",
            ["ID Number", "Description", "Date of Purchase", "Cost", "Dep. Rate",
             "Dep. Opening", "Charge (Period)", "Adjustment", "Dep. Closing",
             "WDV", "Location", "Condition", "Name of User"],
            rows)
